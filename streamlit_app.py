
# streamlit_app.py
# ✈️ Visa-Safe Flight Route Checker using Amadeus API

import streamlit as st
import requests

# --- Sidebar Inputs ---
st.sidebar.title("🧳 Traveler Info")

origin = st.sidebar.text_input("From (IATA Code)", value="BOM")
destination = st.sidebar.text_input("To (IATA Code)", value="JFK")
departure_date = st.sidebar.date_input("Departure Date")
passport_country = st.sidebar.selectbox("Passport Country", ["IND", "USA"])
has_us_visa = st.sidebar.checkbox("Valid US Visa?", value=False)

st.title("🌐 Visa-Safe Flight Search")
st.write("This tool checks visa safety of your flight routes based on layovers.")

# --- API Credentials ---
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

# --- Run search ---
if st.sidebar.button("Search Flights"):
    # Step 1: Get token
    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        token = requests.post(auth_url, data=auth_data).json()["access_token"]
    except:
        st.error("❌ Failed to get Amadeus access token. Check credentials.")
        st.stop()

    # Step 2: Call Amadeus flight search
    search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin.strip().upper(),
        "destinationLocationCode": destination.strip().upper(),
        "departureDate": str(departure_date),
        "adults": 1,
        "max": 3
    }

    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()

    if "data" not in data:
        st.error("❌ No flights found or API error.")
        st.json(data)
        st.stop()

    # Step 3: Process flight options
    for idx, offer in enumerate(data["data"], start=1):
        layovers = []
        flags = []
        for itinerary in offer.get("itineraries", []):
            for segment in itinerary.get("segments", []):
                arrival = segment["arrival"]["iataCode"]
                layovers.append(arrival)
                if arrival == "IST" and passport_country == "IND" and not has_us_visa:
                    flags.append("⚠️ Turkish transit visa required at IST")
                elif arrival == "AMS" and passport_country == "IND" and not has_us_visa:
                    flags.append("⚠️ Schengen visa required at AMS")
                elif arrival == "CDG" and passport_country == "IND" and not has_us_visa:
                    flags.append("⚠️ Schengen visa required at CDG")

        st.subheader(f"✈️ Option {idx}")
        st.markdown(" → ".join(layovers))
        if flags:
            for f in flags:
                st.warning(f)
        else:
            st.success("✅ Visa-safe route")
