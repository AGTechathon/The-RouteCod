import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
import time
from Similarity_Algorithm import find_similar_activities, fetch_low_cost_activities
from route import fetch_distance_matrix, cluster_locations
from hotel_suggestions import suggest_hotels
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MINIMUM_BUDGET = 100.0
MAX_HOURS_PER_DAY = 10.0
TAXI_RATE = 16.0
MAX_TRAVEL_TIME = 5.0
MAX_ACTIVITIES_PER_DAY = 3

def score_activity(activity, daily_budget_per_person):
    similarity = activity["similarity_score"]
    rating = activity["rating"]
    cost = activity["activity"]["estimatedCost"]
    cost_score = 1.0 - min(cost / daily_budget_per_person, 1.0)
    return 0.5 * similarity + 0.3 * rating / 5.0 + 0.2 * cost_score

def assign_time_slot(start_time, duration):
    start_str = start_time.strftime("%H:%M")
    end_time = start_time + timedelta(hours=duration)
    end_str = end_time.strftime("%H:%M")
    return start_str, end_str

def format_travel_duration(travel_time):
    hours = int(travel_time)
    minutes = round((travel_time - hours) * 60)
    if hours > 0 and minutes > 0:
        return f"{hours} hr {minutes} min"
    elif hours > 0:
        return f"{hours} hr"
    else:
        return f"{minutes} min"

def convert_to_serializable(data):
    if isinstance(data, dict):
        return {k: convert_to_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, (np.integer, np.int64)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64)):
        return float(data)
    return data

def generate_itinerary(user_input):
    start_time = time.time()
    start_date = datetime.strptime(user_input["trip"]["startDate"], "%Y-%m-%d")
    end_date = datetime.strptime(user_input["trip"]["endDate"], "%Y-%m-%d")
    days = (end_date - start_date).days + 1
    people = int(user_input["trip"]["people"])
    budget = float(user_input["trip"]["budget"])
    destination = user_input["trip"]["destination"]
    preferences = user_input["trip"].get("preferences", [])

    if days < 1 or people < 1 or budget < MINIMUM_BUDGET:
        raise ValueError("Invalid trip inputs: days, people, or budget too low")

    daily_budget = budget / days
    activities = find_similar_activities(destination, preferences, budget, people, days)
    fallback_activities = fetch_low_cost_activities(destination, budget, people, 50)

    valid_activities, locations = [], []
    coord_to_activity = {}
    for activity in activities:
        lat = float(activity["activity"].get("latitude", 0))
        lon = float(activity["activity"].get("longitude", 0))
        if lat == 0 or lon == 0:
            continue
        coord = (lon, lat)
        coord_to_activity.setdefault(coord, []).append(activity)

    for coord, acts in coord_to_activity.items():
        best_act = max(acts, key=lambda a: a["similarity_score"])
        valid_activities.append(best_act)
        locations.append(coord)

    if not valid_activities:
        return {"itinerary": []}

    distance_matrix, time_matrix, valid_indices = fetch_distance_matrix(locations)
    valid_activities = [valid_activities[i] for i in valid_indices]
    for i, act in enumerate(valid_activities):
        act["matrix_index"] = i
        act["id"] = i

    clusters = cluster_locations(distance_matrix, eps_km=5.0, min_samples=2)
    for i, cluster_id in enumerate(clusters):
        valid_activities[i]["cluster_id"] = cluster_id
    logger.info(f"Cluster sizes: {[np.sum(clusters == c) for c in np.unique(clusters) if c >= 0]}")

    for act in valid_activities:
        act["score"] = score_activity(act, daily_budget / people)

    cluster_groups = {}
    for act in valid_activities:
        cid = act.get("cluster_id", -1)
        cluster_groups.setdefault(cid, []).append(act)

    itinerary = []
    used_ids = set()
    used_names_global = set()

    for day in range(1, days + 1):
        current_time = datetime.strptime("09:00", "%H:%M")
        daily_cost, daily_duration = 0.0, 0.0
        day_entries = []

        available_clusters = [cid for cid in cluster_groups if cluster_groups[cid] and cid != -1]
        if available_clusters:
            cluster_scores = [(cid, sum(a["score"] for a in cluster_groups[cid]) / len(cluster_groups[cid])) for cid in available_clusters]
            cluster_id = max(cluster_scores, key=lambda x: x[1])[0]
            day_activities = [a for a in cluster_groups[cluster_id] if a["id"] not in used_ids and a["activity"]["name"] not in used_names_global]
        else:
            day_activities = [a for a in valid_activities if a["id"] not in used_ids and a["activity"]["name"] not in used_names_global]

        day_activities.sort(key=lambda x: x["score"], reverse=True)

        for a in day_activities[:MAX_ACTIVITIES_PER_DAY]:
            if a["activity"]["name"] in used_names_global:
                continue
            cost = float(a["activity"]["estimatedCost"]) * people
            dur = float(a.get("duration", 2))
            if daily_cost + cost <= daily_budget and daily_duration + dur <= MAX_HOURS_PER_DAY:
                start_str, end_str = assign_time_slot(current_time, dur)
                entry = {
                    "name": a["activity"]["name"],
                    "category": a["activity"]["category"],
                    "location": a["activity"]["location"],
                    "time_slot": f"{start_str}-{end_str}",
                    "duration": format_travel_duration(dur),
                    "estimatedCost": cost,
                    "rating": float(a["rating"]),
                    "latitude": float(a["activity"]["latitude"]),
                    "longitude": float(a["activity"]["longitude"]),
                    "day": day,
                    "date": (start_date + timedelta(days=day - 1)).strftime("%Y-%m-%d")
                }
                day_entries.append(entry)
                used_ids.add(a["id"])
                used_names_global.add(a["activity"]["name"])
                daily_cost += cost
                daily_duration += dur
                current_time += timedelta(hours=dur)

        if len([a for a in day_entries if a["category"] != "Travel"]) < MAX_ACTIVITIES_PER_DAY:
            for fallback in fallback_activities:
                if fallback["activity"]["name"] in used_names_global:
                    continue
                cost = float(fallback["activity"]["estimatedCost"]) * people
                dur = float(fallback.get("duration", 2))
                if daily_cost + cost <= daily_budget and daily_duration + dur <= MAX_HOURS_PER_DAY:
                    start_str, end_str = assign_time_slot(current_time, dur)
                    entry = {
                        "name": fallback["activity"]["name"],
                        "category": fallback["activity"]["category"],
                        "location": fallback["activity"]["location"],
                        "time_slot": f"{start_str}-{end_str}",
                        "duration": format_travel_duration(dur),
                        "estimatedCost": cost,
                        "rating": float(fallback["rating"]),
                        "latitude": float(fallback["activity"]["latitude"]),
                        "longitude": float(fallback["activity"]["longitude"]),
                        "day": day,
                        "date": (start_date + timedelta(days=day - 1)).strftime("%Y-%m-%d")
                    }
                    day_entries.append(entry)
                    used_names_global.add(fallback["activity"]["name"])
                    daily_cost += cost
                    daily_duration += dur
                    current_time += timedelta(hours=dur)
                if len([a for a in day_entries if a["category"] != "Travel"]) >= MAX_ACTIVITIES_PER_DAY:
                    break

        # Recompute travel between activities
        new_entries = []
        current_time = datetime.strptime("09:00", "%H:%M")
        for i, entry in enumerate(day_entries):
            dur = float(entry["duration"].split()[0]) if "hr" in entry["duration"] else float(entry["duration"].split()[0]) / 60
            start_str, end_str = assign_time_slot(current_time, dur)
            entry["time_slot"] = f"{start_str}-{end_str}"
            new_entries.append(entry)
            current_time += timedelta(hours=dur)

            if i < len(day_entries) - 1:
                next_entry = day_entries[i + 1]
                idx_from = next((a["matrix_index"] for a in valid_activities if a["activity"]["name"] == entry["name"]), -1)
                idx_to = next((a["matrix_index"] for a in valid_activities if a["activity"]["name"] == next_entry["name"]), -1)
                if idx_from == -1 or idx_to == -1:
                    continue
                dist_km = float(distance_matrix[idx_from][idx_to])
                time_hr = float(time_matrix[idx_from][idx_to])
                travel_cost = dist_km * people * TAXI_RATE
                start_str, end_str = assign_time_slot(current_time, time_hr)
                travel = {
                    "name": f"Travel to {next_entry['name']}",
                    "category": "Travel",
                    "location": f"Travel from {entry['name']} to {next_entry['name']}",
                    "distance": round(dist_km, 2),
                    "distanceUnit": "km",
                    "duration": format_travel_duration(time_hr),
                    "estimatedCost": round(travel_cost, 2),
                    "time_slot": f"{start_str}-{end_str}",
                    "rating": 0.0,
                    "latitude": next_entry["latitude"],
                    "longitude": next_entry["longitude"],
                    "day": day,
                    "date": (start_date + timedelta(days=day - 1)).strftime("%Y-%m-%d")
                }
                new_entries.append(travel)
                current_time += timedelta(hours=time_hr)

        itinerary.append({
            "day": day,
            "date": (start_date + timedelta(days=day - 1)).strftime("%Y-%m-%d"),
            "activities": new_entries,
            "lunch": [],
            "stay": []
        })

    suggestions = suggest_hotels([a for day in itinerary for a in day["activities"]], {"trip": user_input["trip"]})
    for day_it in itinerary:
        key = f"day{day_it['day']}"
        day_it["lunch"] = list(suggestions.get(key, {}).get("lunch", {}).values())
        day_it["stay"] = list(suggestions.get(key, {}).get("stay", {}).values())

    logger.info(f"Generated itinerary in {time.time() - start_time:.2f}s")
    return convert_to_serializable({"itinerary": itinerary})
