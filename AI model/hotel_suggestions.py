from math import radians, sin, cos, sqrt, asin
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is missing")

def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance between two points on Earth."""
    R = 6371  # Earth radius in kilometers
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def is_lunch_time_slot(time_slot):
    """Check if a time slot falls within lunch hours (12:00-14:00)."""
    try:
        start_time = datetime.strptime(time_slot.split("-")[0].strip(), "%H:%M").time()
        lunch_start = datetime.strptime("12:00", "%H:%M").time()
        lunch_end = datetime.strptime("14:00", "%H:%M").time()
        return lunch_start <= start_time <= lunch_end
    except ValueError:
        return False

def suggest_hotels(activities, user_input):
    """Suggest hotels and lunch spots based on activity locations."""
    client = MongoClient(MONGO_URI)
    db = client["TripCraft"]
    collection = db["destination"]
    try:
        start_date = datetime.strptime(user_input["trip"]["startDate"], "%Y-%m-%d")
        end_date = datetime.strptime(user_input["trip"]["endDate"], "%Y-%m-%d")
        days = (end_date - start_date).days + 1
        people = int(user_input["trip"]["people"])
        budget = float(user_input["trip"]["budget"])
        destination = user_input["trip"]["destination"]
        preferences = user_input["trip"].get("preferences", [])
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid input: {str(e)}")

    destination_doc = collection.find_one({"destination": destination})
    if not destination_doc:
        raise ValueError("Destination not found in database")

    hotels = destination_doc.get("hotels", [])
    # Validate hotel coordinates
    valid_hotels = []
    for hotel in hotels:
        lat = float(hotel.get("latitude", 0))
        lon = float(hotel.get("longitude", 0))
        if lat == 0 or lon == 0:
            print(f"Skipping hotel '{hotel.get('name', 'Unknown')}' due to invalid coordinates")
            continue
        valid_hotels.append(hotel)
    hotels = valid_hotels

    stay_hotels = [h for h in hotels if h.get("stayType") == "Stay"]
    lunch_restaurants = [h for h in hotels if h.get("stayType") == "Lunch"]

    day_map = {}
    for activity in activities:
        day = activity["day"]
        day_map.setdefault(day, []).append(activity)

    suggestions = {}
    used_lunch_names = set()  # Track used lunch spots
    used_stay_names = set()   # Track used stay spots

    for day, activities in day_map.items():
        day_key = f"day{day}"
        suggestions[day_key] = {"lunch": {}, "stay": {}}

        if not activities:
            continue

        day_activities = [act for act in activities if act.get("category") != "Travel"]
        if not day_activities:
            continue
        day_activities.sort(key=lambda a: a["time_slot"])

        # Stay suggestions (closest to last activity)
        last_activity = day_activities[-1]
        if stay_hotels:
            stay_sorted = sorted(
                stay_hotels,
                key=lambda h: haversine(
                    float(h["longitude"]), float(h["latitude"]),
                    float(last_activity["longitude"]), float(last_activity["latitude"])
                )
            )
            for i, spot in enumerate(stay_sorted[:4], 1):
                if spot["name"] not in used_stay_names:  # Only add unused stays
                    suggestions[day_key]["stay"][f"spot{i}"] = {
                        "name": spot["name"],
                        "location": spot["location"],
                        "rating": float(spot["rating"]),
                        "pricePerNight": int(spot["pricePerNight"]),
                        "longitude": float(spot["longitude"]),
                        "latitude": float(spot["latitude"])
                    }
                    used_stay_names.add(spot["name"])
                if len(suggestions[day_key]["stay"]) >= 2:  # Limit to 2 unique stays
                    break

        # Lunch suggestions (closest to lunch-time activity)
        lunch_activities = [a for a in day_activities if is_lunch_time_slot(a["time_slot"])]
        if lunch_activities and lunch_restaurants:
            lunch_activity = lunch_activities[0]
            lunch_sorted = sorted(
                lunch_restaurants,
                key=lambda r: haversine(
                    float(r["longitude"]), float(r["latitude"]),
                    float(lunch_activity["longitude"]), float(lunch_activity["latitude"])
                )
            )
            for i, spot in enumerate(lunch_sorted[:3], 1):
                if spot["name"] not in used_lunch_names:  # Only add unused lunch spots
                    suggestions[day_key]["lunch"][f"spot{i}"] = {
                        "name": spot["name"],
                        "location": spot["location"],
                        "rating": float(spot["rating"]),
                        "price": int(spot["pricePerNight"]),
                        "longitude": float(spot["longitude"]),
                        "latitude": float(spot["latitude"])
                    }
                    used_lunch_names.add(spot["name"])
                if len(suggestions[day_key]["lunch"]) >= 1:  # Limit to 1 unique lunch spot
                    break

    return suggestions