from flask import Flask, render_template, request, jsonify
import json
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_location', methods=['POST'])
def get_location():
    try:
        data = request.json
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        category = data.get('category', 'food')  # Default to 'food' if not specified
        
        # Load places based on selected category
        places = load_places(f'{category}.json')
        nearest_places = find_nearest_places(lat, lon, places)
        
        return jsonify({
            'status': 'success',
            'places': nearest_places
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True) 