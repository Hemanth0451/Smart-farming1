import streamlit as st
import pandas as pd
import joblib
import requests
import pyttsx3
from datetime import datetime
from dotenv import load_dotenv
import openai
import os

# --- Load Environment Variables ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Crop Info Data ---
crop_info = {
    "rice": {"temperature": "20°C - 35°C", "ph": "5.5 - 7.0", "rainfall": "100 - 200 cm", "tips": "Rice needs plenty of water and warm climate.", "harvest_time": "3 - 6 months"},
    "wheat": {"temperature": "12°C - 25°C", "ph": "6.0 - 7.0", "rainfall": "30 - 90 cm", "tips": "Requires cool weather during growth and dry weather for harvest.", "harvest_time": "4 - 6 months"},
    "maize": {"temperature": "18°C - 27°C", "ph": "5.8 - 7.0", "rainfall": "50 - 100 cm", "tips": "Requires well-drained fertile soil and moderate rainfall.", "harvest_time": "3 - 4 months"},
    "cotton": {"temperature": "21°C - 30°C", "ph": "5.5 - 7.5", "rainfall": "50 - 100 cm", "tips": "Needs black soil rich in lime and moisture.", "harvest_time": "6 - 7 months"},
    "banana": {"temperature": "26°C - 30°C", "ph": "5.5 - 7.0", "rainfall": "100 - 200 cm", "tips": "Needs rich, well-drained soil and frequent watering.", "harvest_time": "9 - 12 months"},
}

# --- Weather & Model ---
API_KEY = "f7cfab71e02685a88920f40cd70180e1"
model = joblib.load("crop_model.pkl")

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecast = [
            {"date": datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d %H:%M"),
             "temp": entry["main"]["temp"],
             "humidity": entry["main"]["humidity"]}
            for entry in data["list"][:5]
        ]
        return forecast
    return None

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 0.9)
    engine.say(text)
    engine.runAndWait()

def recommend_fertilizer(n, p, k):
    recommendation = ""
    if n < 90:
        recommendation += "🌿 Nitrogen is low. Use Urea or Ammonium Sulphate.\n"
    elif n > 120:
        recommendation += "🚫 Nitrogen is high. Avoid nitrogen-rich fertilizers.\n"
    if p < 40:
        recommendation += "🌿 Phosphorus is low. Use Single Super Phosphate (SSP).\n"
    elif p > 60:
        recommendation += "🚫 Phosphorus is high. Avoid over-fertilizing.\n"
    if k < 40:
        recommendation += "🌿 Potassium is low. Use Muriate of Potash (MOP).\n"
    elif k > 60:
        recommendation += "🚫 Potassium is high. Reduce potash-based fertilizers.\n"
    return recommendation if recommendation else "✅ NPK levels are in optimal range. No extra fertilizers needed."

# --- UI Layout ---
st.set_page_config(page_title="Smart Farmer Assistant", layout="wide")
st.markdown("<h1 style='text-align:center;'>🌾 Smart Farmer Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Empowering farmers with AI, data & technology</h4>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("📋 Select Module", ["Dashboard", "Crop Advisor", "Weather Forecast", "Market Prices", "Chatbot"])

# --- Dashboard ---
if menu == "Dashboard":
    st.subheader("📊 Dashboard Overview")
    st.write("- 🌡️ Weather & price alerts")
    st.write("- 🌾 Crop recommendation highlights")
    st.write("- 👨‍🌾 Welcome, Farmer!")
    st.success("AI assistant for crop planning, market prices, weather alerts & more.")

# --- Crop Advisor ---
elif menu == "Crop Advisor":
    st.subheader("🌱 Crop Recommendation System")
    city = st.text_input("Enter your city name (e.g. Kadapa,IN):")
    temperature, humidity = 25.0, 50.0
    if city:
        weather_data = get_weather(city)
        if weather_data:
            temperature = weather_data[0]['temp']
            humidity = weather_data[0]['humidity']
            st.success(f"Weather: {temperature}°C, {humidity}% humidity")
        else:
            st.error("Failed to fetch weather")

    n = st.number_input("Nitrogen (N)", 0)
    p = st.number_input("Phosphorus (P)", 0)
    k = st.number_input("Potassium (K)", 0)
    temp = st.number_input("Temperature (°C)", value=temperature)
    hum = st.number_input("Humidity (%)", value=humidity)
    ph = st.number_input("pH value", min_value=0.0, max_value=14.0, value=6.5)
    rain = st.number_input("Rainfall (mm)", min_value=0.0, value=100.0)

    if st.button("🌾 Recommend Crop"):
        crop = model.predict([[n, p, k, temp, hum, ph, rain]])[0]
        st.success(f"Recommended Crop: {crop}")
        speak_text(f"Recommended Crop is {crop}")

        st.info("🧪 Fertilizer Tips")
        tips = recommend_fertilizer(n, p, k)
        st.write(tips)
        speak_text(tips)

        st.info("📘 Crop Info")
        info = crop_info.get(crop.lower(), {})
        if info:
            for key, val in info.items():
                st.write(f"**{key.capitalize()}**: {val}")
            speak_text(info.get("tips", ""))
        else:
            st.warning("No detailed info available.")

# --- Weather Forecast ---
elif menu == "Weather Forecast":
    st.subheader("🌦 Weather Forecast")
    city = st.text_input("Enter city for forecast")
    if city:
        data = get_weather(city)
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.error("Weather data unavailable")

# --- Market Prices ---
elif menu == "Market Prices":
    st.subheader("📉 Mandi Prices")
    st.write("Feature coming soon (MVP uses static prices or Agmarknet API)")
    prices = {
        "rice": "₹2000/qtl",
        "wheat": "₹2100/qtl",
        "maize": "₹1700/qtl",
    }
    crop = st.selectbox("Choose crop", list(prices.keys()))
    st.info(f"🪙 Price for {crop}: {prices[crop]}")

# --- Chatbot (OpenAI GPT Integration) ---
elif menu == "Chatbot":
    st.subheader("💬 Farming Chatbot")
    query = st.text_input("Ask something about farming...")

    if query:
        with st.spinner("🤖 Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert agriculture assistant. Help farmers with crops, fertilizers, pests, weather, and related queries."},
                        {"role": "user", "content": query}
                    ]
                )
                answer = response.choices[0].message['content']
                st.write(f"🤖: {answer}")
                speak_text(answer)
            except Exception as e:
                st.error(f"Error: {e}")
