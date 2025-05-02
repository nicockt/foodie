import json
from math import radians, sin, cos, sqrt, atan2
import geocoder
import geopy
from geopy.geocoders import Nominatim
import requests
import webbrowser
import os
import time

def haversine(lat1, lon1, lat2, lon2):
    # Calculate the great-circle distance between two points on the Earth
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_user_location():
    try:
        # Open the HTML file in the default browser
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'get_location.html')
        webbrowser.open('file://' + html_path)
        
        print("Please allow location access in your browser and copy the coordinates.")
        print("Enter the coordinates when prompted.")
        
        lat = float(input("Enter your latitude: "))
        lon = float(input("Enter your longitude: "))
        
        print(f"Using location: latitude={lat}, longitude={lon}")
        return lat, lon
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Please enter your location manually.")
        lat = float(input("Enter your latitude: "))
        lon = float(input("Enter your longitude: "))
        return lat, lon

def load_places(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_nearest_places(user_lat, user_lon, places, top_n=10):
    for place in places:
        try:
            place_lat = float(place['latitude'])
            place_lon = float(place['longitude'])
            place['distance_km'] = haversine(user_lat, user_lon, place_lat, place_lon)
        except Exception:
            place['distance_km'] = float('inf')
    sorted_places = sorted(places, key=lambda x: x['distance_km'])
    return sorted_places[:top_n]

def main():
    user_lat, user_lon = get_user_location()
    places = load_places('assets/food.json')
    nearest_places = find_nearest_places(user_lat, user_lon, places)
    print("\nNearest places:")
    for place in nearest_places:
        print(f"{place['name']} - {place['address']} ({place['distance_km']:.2f} km)")

if __name__ == "__main__":
    main()