import os
import numpy as np
from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is missing")

db = None

trip_keywords = {
    "history": ["historical", "monuments", "museum", "ancient", "heritage", "ruins", "castle", "fort", "palace"],
    "food": ["food", "cuisine", "restaurant", "street food"],
    "adventure": ["hiking", "trekking", "rafting", "skydiving", "scuba diving"],
    "relaxation": ["spa", "beach", "resort", "yoga", "wellness"],
    "shopping": ["mall", "market", "souvenirs", "bazaar"],
    "culture": ["festival", "traditional", "heritage", "cultural site"],
    "nature": ["forest", "park", "wildlife", "waterfall", "lake", "mountain"],
    "nightlife": ["club", "bar", "pub", "night market"],
    "art": ["museum", "gallery", "exhibition", "theater"],
    "spiritual": ["temple", "mosque", "church", "pilgrimage"]
}

category_to_tags = {
    "Museum": ["art", "history"],
    "Historical": ["history"],
    "Landmark": ["history", "culture"],
    "Church": ["spiritual"],
    "Palace": ["history", "culture"],
    "Park": ["nature"],
    "Beach": ["relaxation", "nature"],
    "Spiritual": ["spiritual"],
    "Relaxation": ["relaxation"],
    "History": ["history"]
}

category_durations = {
    "Museum": 3,
    "Historical": 2,
    "Landmark": 1,
    "Church": 1,
    "Palace": 2,
    "Park": 1,
    "Beach": 2,
    "Spiritual": 1,
    "Relaxation": 2
}

all_possible_tags = set(trip_keywords.keys())

def safe_string_contains(haystack, needle):
    """Check if needle is in haystack, case-insensitive."""
    try:
        haystack_str = str(haystack).lower()
        needle_str = str(needle).lower()
        logger.debug(f"Checking if '{needle_str}' is in '{haystack_str}'")
        return needle_str in haystack_str
    except Exception as e:
        logger.error(f"Error in safe_string_contains: haystack={haystack}, needle={needle}, error={e}")
        return False

def compute_similarity_score(user_prefs, spot_tags, spot_name):
    """Compute similarity score between user preferences and spot tags/name."""
    try:
        spot_name = str(spot_name).strip() if spot_name else ""
        logger.debug(f"Computing similarity for spot: {spot_name}")
        user_prefs = [str(pref).lower() for pref in user_prefs if str(pref).strip()]
        spot_tags = [str(tag).lower() for tag in spot_tags if str(tag).strip()]
        
        user_vec = np.zeros(len(all_possible_tags))
        spot_vec = np.zeros(len(all_possible_tags))
        
        for i, tag in enumerate(all_possible_tags):
            if tag in user_prefs:
                user_vec[i] = 2.0
            if tag in spot_tags:
                spot_vec[i] = 1.0
        
        keyword_score = 0.0
        max_keywords = 0
        spot_text = spot_name.lower()
        
        for pref in user_prefs:
            keywords = trip_keywords.get(pref, [])
            max_keywords += len(keywords)
            for keyword in keywords:
                if safe_string_contains(spot_text, keyword):
                    keyword_score += 1
        
        keyword_weight = 0.3
        keyword_score = (keyword_score / max_keywords) * keyword_weight if max_keywords > 0 else 0.0
        tag_similarity = cosine_similarity([user_vec], [spot_vec])[0][0] if np.sum(user_vec) > 0 else 0.0
        tag_weight = 0.7
        total_similarity = tag_weight * tag_similarity + keyword_score
        return min(total_similarity, 1.0)
    except Exception as e:
        logger.error(f"Error computing similarity for spot '{spot_name}': {e}")
        return 0.0

def fetch_low_cost_activities(destination, budget, people, required_activities):
    """Fetch low-cost activities within budget."""
    global db
    if db is None:
        client = MongoClient(MONGO_URI)
        db = client.get_database("TripCraft")
    
    start_time = time.time()
    destination_clean = str(destination).lower().strip()
    logger.info(f"Fetching low-cost activities for: {destination_clean}")
    dest_data = db.destination.find_one({"destination": {"$regex": f"^{destination_clean}$", "$options": "i"}})
    if not dest_data or "spots" not in dest_data:
        logger.warning(f"No spots found for '{destination_clean}'")
        return []
    
    spots = dest_data["spots"]
    low_cost_spots = []
    unique_spot_names = set()
    unique_coords = set()

    for spot in spots:
        spot_name = str(spot.get('name', '')).strip()
        logger.debug(f"Processing spot: {spot_name}")
        if not spot_name or spot_name.lower() in unique_spot_names:
            logger.debug(f"Skipping duplicate or invalid name: {spot_name}")
            continue
        
        cost = spot.get('estimatedCost', None)
        if cost is None:
            logger.warning(f"No cost data for '{spot_name}', skipping")
            continue
        try:
            cost = float(cost)
        except (ValueError, TypeError):
            logger.warning(f"Invalid cost for '{spot_name}', skipping")
            continue
        total_cost = cost * people
        if total_cost > budget:
            logger.debug(f"Skipping '{spot_name}' (cost: {total_cost} > budget: {budget})")
            continue
        
        try:
            latitude = float(spot.get("latitude", 0))
            longitude = float(spot.get("longitude", 0))
        except (ValueError, TypeError):
            logger.warning(f"Invalid coordinates for '{spot_name}', skipping")
            continue
        if latitude == 0 or longitude == 0 or not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.warning(f"Invalid coordinates for '{spot_name}': lat={latitude}, lon={longitude}")
            continue
        coord = (round(longitude, 6), round(latitude, 6))
        if coord in unique_coords:
            logger.warning(f"Duplicate coordinates for '{spot_name}': {coord}")
            continue
        unique_coords.add(coord)
        
        category = str(spot.get('category', '')).lower()
        rating = float(spot.get('rating', 4.0)) if isinstance(spot.get('rating', 4.0), (int, float)) else 4.0
        duration = category_durations.get(category.capitalize(), 2)
        tags = category_to_tags.get(category.capitalize(), [])
        time_slot = str(spot.get('timeSlot', 'Daytime'))
        
        spot_name_lower = spot_name.lower()
        for pref, keywords in trip_keywords.items():
            for keyword in keywords:
                if safe_string_contains(spot_name_lower, keyword):
                    tags.append(pref)
                    logger.debug(f"Tag '{pref}' added for '{keyword}' in '{spot_name_lower}'")
                    break
        tags = list(set(tags))
        if "shopping" in tags and category in ["spiritual", "history"]:
            tags.remove("shopping")
        
        unique_spot_names.add(spot_name.lower())
        
        activity_data = {
            "activity": {
                "name": spot_name,
                "location": str(spot.get("location", destination)),
                "estimatedCost": cost,
                "category": category.capitalize(),
                "latitude": latitude,
                "longitude": longitude,
                "timeSlot": time_slot,
                "tags": tags
            },
            "similarity_score": 0.0,
            "rating": rating,
            "duration": duration
        }
        low_cost_spots.append((cost, activity_data))
    
    low_cost_spots.sort(key=lambda x: x[0])
    result = [spot[1] for spot in low_cost_spots[:required_activities]]
    logger.info(f"Returning {len(result)} low-cost activities in {time.time() - start_time:.2f}s")
    return result

def find_similar_activities(destination, preferences, budget, people, days):
    """Find activities matching user preferences within budget."""
    global db
    if db is None:
        client = MongoClient(MONGO_URI)
        db = client.get_database("TripCraft")
    
    logger.info(f"Finding similar activities for: {destination}, Preferences: {preferences}, People: {people}")
    start_time = time.time()
    destination_clean = str(destination).lower().strip()
    dest_data = db.destination.find_one({"destination": {"$regex": f"^{destination_clean}$", "$options": "i"}})
    if not dest_data or "spots" not in dest_data:
        logger.warning(f"No spots found for '{destination_clean}'")
        return []
    
    preferences = [p for p in preferences if p in trip_keywords] if preferences else []
    logger.debug(f"Validated preferences: {preferences}")

    spots = dest_data["spots"]
    all_spots = []
    unique_spot_names = set()
    unique_coords = set()

    for spot in spots:
        spot_name = str(spot.get('name', '')).strip()
        logger.debug(f"Processing spot: {spot_name}")
        if not spot_name or spot_name.lower() in unique_spot_names:
            logger.debug(f"Skipping duplicate or invalid name: {spot_name}")
            continue
        
        cost = spot.get('estimatedCost', None)
        if cost is None:
            logger.warning(f"No cost data for '{spot_name}', skipping")
            continue
        try:
            cost = float(cost)
        except (ValueError, TypeError):
            logger.warning(f"Invalid cost for '{spot_name}', skipping")
            continue
        total_cost = cost * people
        if total_cost > budget:
            logger.debug(f"Skipping '{spot_name}' (cost: {total_cost} > budget: {budget})")
            continue
        
        try:
            latitude = float(spot.get("latitude", 0))
            longitude = float(spot.get("longitude", 0))
        except (ValueError, TypeError):
            logger.warning(f"Invalid coordinates for '{spot_name}', skipping")
            continue
        if latitude == 0 or longitude == 0 or not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.warning(f"Invalid coordinates for '{spot_name}': lat={latitude}, lon={longitude}")
            continue
        coord = (round(longitude, 6), round(latitude, 6))
        if coord in unique_coords:
            logger.warning(f"Duplicate coordinates for '{spot_name}': {coord}")
            continue
        unique_coords.add(coord)
        
        category = str(spot.get('category', '')).lower()
        rating = float(spot.get('rating', 4.0)) if isinstance(spot.get('rating', 4.0), (int, float)) else 4.0
        duration = category_durations.get(category.capitalize(), 2)
        tags = category_to_tags.get(category.capitalize(), [])
        time_slot = str(spot.get('timeSlot', 'Daytime'))
        
        spot_name_lower = spot_name.lower()
        for pref, keywords in trip_keywords.items():
            for keyword in keywords:
                if safe_string_contains(spot_name_lower, keyword):
                    tags.append(pref)
                    logger.debug(f"Tag '{pref}' added for '{keyword}' in '{spot_name_lower}'")
                    break
        tags = list(set(tags))
        if "shopping" in tags and category in ["spiritual", "history"]:
            tags.remove("shopping")
        
        unique_spot_names.add(spot_name.lower())
        
        similarity_score = compute_similarity_score(preferences, tags, spot_name) if preferences else 0.0
        activity_data = {
            "activity": {
                "name": spot_name,
                "location": str(spot.get("location", destination)),
                "estimatedCost": cost,
                "category": category.capitalize(),
                "latitude": latitude,
                "longitude": longitude,
                "timeSlot": time_slot,
                "tags": tags
            },
            "similarity_score": similarity_score,
            "rating": rating,
            "duration": duration
        }
        all_spots.append(activity_data)
    
    required_activities = min(50, max(20, 7 * days))
    logger.info(f"Need {required_activities} activities, found {len(all_spots)}")
    if len(all_spots) < required_activities:
        logger.info("Fetching additional low-cost activities")
        additional_spots = fetch_low_cost_activities(destination, budget, people, required_activities - len(all_spots))
        all_spots.extend(additional_spots)
        logger.info(f"Added {len(additional_spots)} additional activities, total: {len(all_spots)}")
    
    if preferences:
        preferences = [str(p).lower() for p in preferences if str(p).strip()]
        invalid_prefs = [p for p in preferences if p not in trip_keywords]
        if invalid_prefs:
            raise ValueError(f"Invalid preferences: {invalid_prefs}")
        all_spots.sort(key=lambda x: (x["similarity_score"], x["rating"], -x["activity"]["estimatedCost"]))
    else:
        all_spots.sort(key=lambda x: (x["rating"], -x["activity"]["estimatedCost"]))
    
    result = all_spots[:required_activities]
    logger.info(f"Returning {len(result)} activities in {time.time() - start_time:.2f}s")
    return result