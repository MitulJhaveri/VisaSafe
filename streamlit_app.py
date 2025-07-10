
import streamlit as st
import requests
from datetime import datetime

# Title
st.set_page_config(page_title="VisaSafe Flight Search", page_icon="🌍")
st.markdown("# 🌍 Visa-Safe Flight Search")
st.write("This tool checks visa safety of your flight routes based on layovers.")

# User input
passport_country = st.selectbox(
    "Select your nationality",
    ["India", "United States", "Mexico", "Brazil", "United Kingdom", "Germany"]
)

has_us_visa = False
if passport_country != "United States":
    has_us_visa = st.checkbox("✅ Do you have a valid US visa?")

origin = st.text_input("Departure Airport IATA Code (e.g., BOM)")
destination = st.text_input("Destination Airport IATA Code (e.g., JFK)")

search = st.button("Search Visa-Safe Routes")

# Amadeus API credentials from secrets
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

# Access token request
def get_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

# Sample visa logic
def visa_safe_route(route, passport, has_us_visa):
    risky_airports = ["CDG", "FRA", "AMS"]
    exemptions = ["US"] if has_us_visa else []
    for stop in route:
        if stop in risky_airports and "US" not in exemptions:
            return False
    return True

# Search flights and check visa logic
if search and origin and destination:
    st.info("🔍 Checking visa safety for route...")

    token = get_access_token()
    if not token:
        st.error("❌ Failed to authenticate with Amadeus API.")
    else:
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": datetime.now().date().isoformat(),
            "adults": 1,
            "max": 3
        }
        response = requests.get(
            "https://test.api.amadeus.com/v2/shopping/flight-offers",
            headers=headers,
            params=params
        )
        data = response.json()

        if "data" in data:
            for i, offer in enumerate(data["data"]):
                route = []
                for segment in offer["itineraries"][0]["segments"]:
                    route.append(segment["departure"]["iataCode"])
                route.append(offer["itineraries"][0]["segments"][-1]["arrival"]["iataCode"])

                st.markdown(f"### ✈️ Option {i+1}")
                st.write(" → ".join(route))

                if visa_safe_route(route, passport_country, has_us_visa):
                    st.success("✅ Visa-safe route")
                else:
                    st.error("⚠️ Potential visa issue in this route")
        else:
            st.warning("No routes found. Try a different input.")
