import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from sklearn.cluster import KMeans
from geopy.distance import geodesic
import requests

def get_coordinates(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "SustainableCommutePlannerApp/1.0"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result["lat"]), float(result["lon"])
    else:
        return None, None

def get_weather():
    return {'weather': 'Clear', 'temperature': 26}

st.set_page_config(page_title="Sustainable Commute Planner", page_icon="🚲")
st.title("🌍 Sustainable Commute Planner")
st.markdown("Plan your commute with eco-friendly options. Save fuel, reduce carbon footprint, and stay healthy!")

# Initialize session state on first load
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False

# Sample user data
initial_users = pd.DataFrame({
    'user_id': [1, 2, 3, 4],
    'home_lat': [12.9716, 12.9352, 13.0352, 12.9711],
    'home_lon': [77.5946, 77.6146, 77.6101, 77.5800],
    'work_lat': [12.9352, 12.9716, 12.9716, 12.9352],
    'work_lon': [77.6146, 77.5946, 77.5946, 77.6146],
    'prefers_biking': [1, 0, 1, 0],
    'prefers_walking': [0, 1, 0, 1],
    'prefers_carpool': [1, 1, 0, 1]
})

# 🧾 Input Form
with st.form("commute_form"):
    st.subheader("📍 Enter Place Names or Landmarks")
    home_place = st.text_input("🏠 Home Location", placeholder="Enter Source")
    work_place = st.text_input("🏢 Work Location", placeholder="Enter Destination")

    st.subheader("🛣️ Commute Preferences")
    col1, col2, col3 = st.columns(3)
    with col1:
        prefers_biking = st.checkbox("🚴 Prefer Biking")
    with col2:
        prefers_walking = st.checkbox("🚶 Prefer Walking")
    with col3:
        prefers_carpool = st.checkbox("🚗 Prefer Carpool")

    submit = st.form_submit_button("🚀 Plan My Commute")

    if submit:
        # Store form data in session_state
        st.session_state['submitted'] = True
        st.session_state['home_place'] = home_place
        st.session_state['work_place'] = work_place
        st.session_state['prefers_biking'] = prefers_biking
        st.session_state['prefers_walking'] = prefers_walking
        st.session_state['prefers_carpool'] = prefers_carpool

# ✅ Process after form is submitted
if st.session_state['submitted']:
    home_place = st.session_state['home_place']
    work_place = st.session_state['work_place']
    prefers_biking = st.session_state['prefers_biking']
    prefers_walking = st.session_state['prefers_walking']
    prefers_carpool = st.session_state['prefers_carpool']

    home_lat, home_lon = get_coordinates(home_place)
    work_lat, work_lon = get_coordinates(work_place)

    if home_lat is None or work_lat is None:
        st.error("❌ Could not locate one or both addresses. Please try more specific or well-known landmarks.")
    else:
        distance_km = round(geodesic((home_lat, home_lon), (work_lat, work_lon)).km, 2)
        weather = get_weather()

        if prefers_walking and weather['weather'] == 'Clear' and weather['temperature'] < 30 and distance_km < 3:
            mode = "🚶 Walking"
            emissions_saved = distance_km * 0.21
        elif prefers_biking and weather['weather'] == 'Clear' and distance_km < 8:
            mode = "🚴 Biking"
            emissions_saved = distance_km * 0.21
        elif prefers_carpool:
            mode = "🚗 Carpool"
            emissions_saved = distance_km * 0.1
        else:
            mode = "🚌 Public Transit"
            emissions_saved = distance_km * 0.15

        st.success(f"✅ **Recommended Mode:** {mode}")
        st.metric("📏 Commute Distance (km)", distance_km)
        st.metric("🌱 Estimated CO₂ Saved (kg)", round(emissions_saved, 2))

        current_user = pd.DataFrame([{
            'user_id': 5,
            'home_lat': home_lat,
            'home_lon': home_lon,
            'work_lat': work_lat,
            'work_lon': work_lon,
            'prefers_biking': int(prefers_biking),
            'prefers_walking': int(prefers_walking),
            'prefers_carpool': int(prefers_carpool)
        }])
        user_data = pd.concat([initial_users, current_user], ignore_index=True)
        features = user_data[['home_lat', 'home_lon', 'work_lat', 'work_lon']]
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        user_data['carpool_cluster'] = kmeans.fit_predict(features)
        user_cluster = user_data[user_data['user_id'] == 5]['carpool_cluster'].values[0]
        carpool_matches = user_data[
            (user_data['carpool_cluster'] == user_cluster) &
            (user_data['user_id'] != 5) &
            (user_data['prefers_carpool'] == 1)
        ]

        st.subheader("👥 Suggested Carpool Matches")
        if prefers_carpool and not carpool_matches.empty:
            st.write("You can connect with the following users:")
            st.dataframe(carpool_matches[['user_id', 'home_lat', 'home_lon', 'work_lat', 'work_lon']])
        else:
            st.info("No carpool matches available nearby.")

        st.subheader("🗺️ Commute Route Map")

        # Create a folium map centered between points
        mid_lat = (home_lat + work_lat) / 2
        mid_lon = (home_lon + work_lon) / 2
        m = folium.Map(location=[mid_lat, mid_lon], zoom_start=13)

        # Add markers
        folium.Marker([home_lat, home_lon], tooltip="Home").add_to(m)
        folium.Marker([work_lat, work_lon], tooltip="Work").add_to(m)

        # Draw route line
        folium.PolyLine(locations=[[home_lat, home_lon], [work_lat, work_lon]],
                        color='blue', weight=5).add_to(m)

        st_folium(m, width=700, height=500)
