import os
import numpy as np
from dotenv import load_dotenv
import openrouteservice
import time
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.neighbors import NearestNeighbors
import logging

# Load environment variables
load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")
if not ORS_API_KEY:
    raise ValueError("ORS_API_KEY not found in .env file")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_distance_matrix(locations, profile='driving-car'):
    """
    Fetch distance and time matrices using OpenRouteService API.
    
    Parameters:
    - locations: list of (longitude, latitude) tuples.
    - profile: str, transport mode (default: 'driving-car').
    
    Returns:
    - tuple: (distance_matrix, time_matrix, valid_indices) as NumPy arrays (km, hours) and list of valid location indices.
    """
    # Validate locations
    if not locations or not all(len(loc) == 2 for loc in locations):
        raise ValueError("Invalid locations format")
    coords = [(round(float(lon), 6), round(float(lat), 6)) for lon, lat in locations]
    
    # Check for duplicate coordinates
    unique_coords = set(coords)
    if len(unique_coords) < len(coords):
        logger.warning(f"Found {len(coords) - len(unique_coords)} duplicate coordinates")
    
    n = len(coords)
    logger.info(f"Fetching distance matrix for {n} locations using ORS ({profile})...")
    
    client = openrouteservice.Client(key=ORS_API_KEY)
    try:
        result = client.distance_matrix(
            locations=coords,
            profile=profile,
            metrics=["distance", "duration"],
            resolve_locations=False,
            units="km"
        )
    except Exception as e:
        logger.error(f"ORS Matrix API failed: {e}")
        raise
    
    # Parse result
    if "distances" not in result or "durations" not in result:
        raise ValueError("ORS response missing distances or durations.")
    
    # Convert to NumPy arrays
    distance_matrix = np.array(result["distances"], dtype=float)  # km
    time_matrix = np.array(result["durations"], dtype=float) / 3600  # hours
    
    # Identify problematic locations (those with too many NaNs)
    nan_dist_counts = np.sum(np.isnan(distance_matrix), axis=1)
    nan_time_counts = np.sum(np.isnan(time_matrix), axis=1)
    nan_threshold = n // 2  # Exclude locations with NaNs in over half the entries
    valid_indices = [i for i in range(n) if nan_dist_counts[i] <= nan_threshold and nan_time_counts[i] <= nan_threshold]
    
    if not valid_indices:
        raise ValueError("No valid locations after NaN filtering")
    
    if len(valid_indices) < n:
        logger.warning(f"Excluding {n - len(valid_indices)} locations due to excessive NaN values")
        for i in range(n):
            if i not in valid_indices:
                logger.warning(f"Excluded location {coords[i]} with {nan_dist_counts[i]} NaN distances and {nan_time_counts[i]} NaN times")
        distance_matrix = distance_matrix[np.ix_(valid_indices, valid_indices)]
        time_matrix = time_matrix[np.ix_(valid_indices, valid_indices)]
    
    # Log NaN locations for remaining matrix
    nan_dist_indices = np.where(np.isnan(distance_matrix))
    for i, j in zip(nan_dist_indices[0], nan_dist_indices[1]):
        logger.warning(f"NaN distance between {coords[valid_indices[i]]} and {coords[valid_indices[j]]}")
    nan_time_indices = np.where(np.isnan(time_matrix))
    for i, j in zip(nan_time_indices[0], nan_time_indices[1]):
        logger.warning(f"NaN time between {coords[valid_indices[i]]} and {coords[valid_indices[j]]}")
    
    # Replace None and NaN with large finite values
    distance_matrix[distance_matrix == None] = 1000.0  # 1000 km
    time_matrix[time_matrix == None] = 10.0  # 10 hours
    if np.any(np.isnan(distance_matrix)):
        logger.warning(f"Found {np.sum(np.isnan(distance_matrix))} NaN values in distance matrix. Replacing with 1000 km.")
        distance_matrix[np.isnan(distance_matrix)] = 1000.0
    if np.any(np.isnan(time_matrix)):
        logger.warning(f"Found {np.sum(np.isnan(time_matrix))} NaN values in time matrix. Replacing with 10 hours.")
        time_matrix[np.isnan(time_matrix)] = 10.0
    
    # Log matrix statistics for debugging
    logger.info(f"Distance matrix shape: {distance_matrix.shape}")
    logger.info(f"Contains NaN: {np.any(np.isnan(distance_matrix))}")
    logger.info(f"Contains inf: {np.any(np.isinf(distance_matrix))}")
    
    # Check for asymmetry and symmetrize
    if not np.allclose(distance_matrix, distance_matrix.T, atol=0.1, equal_nan=True):
        logger.warning("Distance matrix is asymmetric. Symmetrizing by averaging.")
        distance_matrix = (distance_matrix + distance_matrix.T) / 2
        distance_matrix[np.isnan(distance_matrix)] = 1000.0
        diff = np.abs(distance_matrix - distance_matrix.T)
        finite_diff = diff[np.isfinite(diff)]
        max_diff = np.max(finite_diff) if len(finite_diff) > 0 else 0
        logger.info(f"Max asymmetry in distance matrix: {max_diff:.2f} km")
    
    if not np.allclose(time_matrix, time_matrix.T, atol=0.1/3600, equal_nan=True):
        logger.warning("Time matrix is asymmetric. Symmetrizing by averaging.")
        time_matrix = (time_matrix + time_matrix.T) / 2
        time_matrix[np.isnan(time_matrix)] = 10.0
        diff = np.abs(time_matrix - time_matrix.T)
        finite_diff = diff[np.isfinite(diff)]
        max_diff = np.max(finite_diff) if len(finite_diff) > 0 else 0
        logger.info(f"Max asymmetry in time matrix: {max_diff*3600:.2f} seconds")
    
    # Ensure non-negative
    if np.any(distance_matrix < 0):
        raise ValueError("Distance matrix contains negative values")
    if np.any(time_matrix < 0):
        raise ValueError("Time matrix contains negative values")
    
    return distance_matrix, time_matrix, valid_indices

def cluster_locations(distance_matrix, locations=None, eps_km=None, min_samples=2, method='dbscan', max_distance=None):
    """
    Cluster locations based on distance matrix.
    
    Parameters:
    - distance_matrix: NumPy array of distances.
    - locations: Optional list of (lon, lat) tuples for centroid calculation.
    - eps_km: Clustering radius in km (auto-estimated if None).
    - min_samples: Minimum points per cluster.
    - method: Clustering method ('dbscan' or 'hierarchical').
    - max_distance: Distance to replace inf values.
    
    Returns:
    - clusters: Array of cluster labels.
    """
    # Validate distance matrix
    dist_array = np.array(distance_matrix)
    
    # Log matrix statistics
    logger.info(f"Clustering distance matrix shape: {dist_array.shape}")
    logger.info(f"Contains NaN: {np.any(np.isnan(dist_array))}")
    logger.info(f"Contains inf: {np.any(np.isinf(dist_array))}")
    
    # Replace NaN with large finite value
    if np.any(np.isnan(dist_array)):
        logger.warning(f"Found {np.sum(np.isnan(dist_array))} NaN values in distance matrix. Replacing with 1000 km.")
        dist_array[np.isnan(dist_array)] = 1000.0
    
    # Relaxed symmetry check with higher tolerance
    if not np.allclose(dist_array, dist_array.T, atol=1e-2, equal_nan=True):
        logger.warning("Distance matrix is not symmetric. Forcing symmetry.")
        dist_array = (dist_array + dist_array.T) / 2
        dist_array[np.isnan(dist_array)] = 1000.0
        diff = np.abs(dist_array - dist_array.T)
        finite_diff = diff[np.isfinite(diff)]
        max_diff = np.max(finite_diff) if len(finite_diff) > 0 else 0
        logger.info(f"Forced symmetrization max difference: {max_diff:.6f} km")
    
    if np.any(dist_array < 0):
        raise ValueError("Distance matrix contains negative values")
    
    # Handle unreachable points
    finite_distances = dist_array[np.isfinite(dist_array)]
    if len(finite_distances) == 0:
        raise ValueError("Distance matrix has no finite distances")
    max_finite = np.max(finite_distances) if len(finite_distances) > 0 else 100
    inf_replacement = max_distance if max_distance else max_finite * 10
    dist_array[np.isinf(dist_array)] = inf_replacement
    
    # Auto-estimate eps if not provided (for DBSCAN)
    if method == 'dbscan' and eps_km is None:
        if dist_array.shape[0] < min_samples:
            logger.warning("Too few points for clustering, returning single cluster")
            clusters = np.zeros(dist_array.shape[0], dtype=int)
            if locations:
                centroid = np.mean(locations, axis=0).tolist()
                logger.info(f"Centroid: {centroid}")
            logger.info("Formed 1 cluster")
            logger.info("Noise points (unclustered): 0")
            return clusters
    # Compute k-distance graph
        neigh = NearestNeighbors(n_neighbors=min_samples, metric='precomputed')
        neigh.fit(dist_array)
        distances, _ = neigh.kneighbors(dist_array)
        k_distances = distances[:, -1]
        k_distances = np.sort(k_distances)
        # Use 75th percentile as eps
        eps_km = k_distances[int(0.75 * len(k_distances))]
        eps_km = max(1.0, min(eps_km, max_finite))
        logger.info(f"Auto-estimated eps_km: {eps_km:.2f}")

    # Perform clustering
    if method == 'dbscan':
        db = DBSCAN(eps=eps_km, min_samples=min_samples, metric='precomputed')
        clusters = db.fit_predict(dist_array)
    elif method == 'hierarchical':
        agg = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=eps_km,
            metric='precomputed',
            linkage='average'
        )
        clusters = agg.fit_predict(dist_array)
        # Mark small clusters as noise
        cluster_sizes = np.bincount(clusters[clusters >= 0])
        small_clusters = np.where(cluster_sizes < min_samples)[0]
        for small in small_clusters:
            clusters[clusters == small] = -1
    else:
        raise ValueError("Method must be 'dbscan' or 'hierarchical'")

    # Compute statistics
    unique_clusters = np.unique(clusters[clusters >= 0])
    n_clusters = len(unique_clusters)
    n_noise = np.sum(clusters == -1)
    
    # Calculate average intra-cluster distance
    avg_intra_distance = 0.0
    if n_clusters > 0:
        intra_distances = []
        for cluster_id in unique_clusters:
            cluster_points = np.where(clusters == cluster_id)[0]
            if len(cluster_points) > 1:
                cluster_distances = dist_array[np.ix_(cluster_points, cluster_points)]
                finite_cluster_distances = cluster_distances[np.isfinite(cluster_distances)]
                if len(finite_cluster_distances) > 0:
                    intra_distances.append(np.mean(finite_cluster_distances))
        avg_intra_distance = np.mean(intra_distances) if intra_distances else 0.0

    # Log centroids if locations provided
    if locations is not None and len(locations) == len(clusters):
        locations = np.array(locations)
        for cluster_id in unique_clusters:
            cluster_points = np.where(clusters == cluster_id)[0]
            if len(cluster_points) > 0:
                centroid = np.mean(locations[cluster_points], axis=0).tolist()
                logger.info(f"Cluster {cluster_id} centroid: {centroid}")

    logger.info(f"Formed {n_clusters} clusters")
    logger.info(f"Noise points (unclustered): {n_noise}")
    logger.info(f"Average intra-cluster distance: {avg_intra_distance:.2f} km")

    return clusters