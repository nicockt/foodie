import streamlit as st
import json
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import time
import random

# Set page config
st.set_page_config(
    page_title="Find Nearest Places",
    layout="wide"
)

# Functions from the original app
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
        
    Returns:
        Distance between the points in kilometers
    """
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def load_places(filename: str) -> list:
    """
    Load places from a JSON file.
    
    Args:
        filename: Path to the JSON file containing places
        
    Returns:
        List of places with their information
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_nearest_places(user_lat: float, user_lon: float, places: list, top_n: int = 10) -> list:
    """
    Find the nearest places to the user's location.
    
    Args:
        user_lat: User's latitude in decimal degrees
        user_lon: User's longitude in decimal degrees
        places: List of places with latitude and longitude information
        top_n: Number of nearest places to return
        
    Returns:
        List of the nearest places sorted by distance
    """
    for place in places:
        try:
            place_lat = float(place['latitude'])
            place_lon = float(place['longitude'])
            place['distance_km'] = haversine(user_lat, user_lon, place_lat, place_lon)
        except Exception:
            place['distance_km'] = float('inf')
    sorted_places = sorted(places, key=lambda x: x['distance_km'])
    return sorted_places[:top_n]

# Initialize session state for geolocation
if 'latitude' not in st.session_state:
    st.session_state.latitude = 40.7128  # Default to New York City
if 'longitude' not in st.session_state:
    st.session_state.longitude = -74.0060
if 'location_obtained' not in st.session_state:
    st.session_state.location_obtained = False
if 'random_place' not in st.session_state:
    st.session_state.random_place = None

# App title
st.title("Find Nearest Places")

# Category selection with random option
col1, col2 = st.columns([3, 1])
with col1:
    category = st.selectbox("Select Category", ["food", "cafe", "drink", "sweet"], key="category_select")
with col2:
    if st.button("🎲 Random Pick"):
        st.session_state.random_place = True
        st.experimental_rerun()

# Get user's location using streamlit_js_eval - this auto-triggers
location = get_geolocation()

# Update session state if we got a valid location
if location and 'coords' in location:
    coords = location['coords']
    if 'latitude' in coords and 'longitude' in coords:
        st.session_state.latitude = coords['latitude']
        st.session_state.longitude = coords['longitude']
        st.session_state.location_obtained = True
else:
    # If we don't have location yet, try to get it with JS
    streamlit_js_eval(js="""
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    // This will trigger a rerun with the location
                    window.parent.postMessage({
                        type: "streamlit:setComponentValue",
                        value: {
                            coords: {
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                                accuracy: position.coords.accuracy
                            }
                        }
                    }, "*");
                },
                function(error) {
                    console.error("Error getting location:", error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 0
                }
            );
        }
        """,
        key="get_location_js"
    )

# Display results automatically
try:
    # Load places based on selected category
    places = load_places(f'assets/{category}.json')
    nearest_places = find_nearest_places(
        st.session_state.latitude,
        st.session_state.longitude, 
        places
    )
    
    # Create a map centered on the user's location
    m = folium.Map(
        location=[st.session_state.latitude, st.session_state.longitude], 
        zoom_start=13
    )
    
    # Add marker for user's location
    folium.Marker(
        [st.session_state.latitude, st.session_state.longitude],
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="user"),
    ).add_to(m)
    
    # Randomly select a place if random pick was clicked
    random_place_data = None
    if st.session_state.random_place and places:
        random_place_idx = random.randint(0, len(places) - 1)
        random_place_data = places[random_place_idx]
        st.session_state.random_place = False
    
    # Create a DataFrame for display
    places_data = []
    
    # Add markers for each place
    for i, place in enumerate(nearest_places):
        try:
            place_lat = float(place['latitude'])
            place_lon = float(place['longitude'])
            
            # Determine if this is the randomly selected place
            is_random_pick = random_place_data and place == random_place_data
            
            # Choose icon based on whether this is the random pick
            icon_color = "green" if is_random_pick else "red"
            icon_type = "star" if is_random_pick else "info-sign"
            
            # Add marker to map
            folium.Marker(
                [place_lat, place_lon],
                popup=f"{place['name']}<br>{place['address']}<br>{place['distance_km']:.2f} km",
                icon=folium.Icon(color=icon_color, icon=icon_type),
            ).add_to(m)
            
            # Add to data for table
            places_data.append({
                "Name": place['name'],
                "Address": place['address'],
                "Distance (km)": f"{place['distance_km']:.2f}"
            })
        except Exception as e:
            st.error(f"Error displaying place: {str(e)}")
    
    # Display random pick highlight if applicable
    if random_place_data:
        st.success(f"🎲 Random Pick: {random_place_data['name']} - {random_place_data['distance_km']:.2f} km away")
    
    # Display map
    st.subheader("Map")
    folium_static(m)
    
    # Display table of results
    st.subheader(f"Nearest {category.capitalize()} Places")
    if places_data:
        st.table(pd.DataFrame(places_data))
    else:
        st.info("No places found")
        
except Exception as e:
    st.error(f"Error: {str(e)}") 