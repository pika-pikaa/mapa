"""
Funkcje pogodowe dla aplikacji Nasza Mapa Przygód
Integracja z OpenWeatherMap API
"""

import requests
import streamlit as st
from typing import Dict, List, Optional

from utils.constants import WEATHER_API_KEY


@st.cache_data(ttl=1800)  # Cache na 30 minut
def get_weather(lat: float, lon: float) -> Optional[Dict]:
    """Pobiera aktualną pogodę z OpenWeatherMap API"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=pl"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # m/s -> km/h
                'city': data.get('name', 'Nieznane')
            }
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)  # Cache na 1 godzinę
def get_weather_forecast(lat: float, lon: float, days: int = 3) -> Optional[List[Dict]]:
    """Pobiera prognozę pogody na kilka dni"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=pl&cnt={days * 8}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Grupuj prognozy po dniach
            daily = {}
            for item in data['list']:
                date = item['dt_txt'].split(' ')[0]
                if date not in daily:
                    daily[date] = {
                        'date': date,
                        'temp_min': item['main']['temp_min'],
                        'temp_max': item['main']['temp_max'],
                        'description': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon']
                    }
                else:
                    daily[date]['temp_min'] = min(daily[date]['temp_min'], item['main']['temp_min'])
                    daily[date]['temp_max'] = max(daily[date]['temp_max'], item['main']['temp_max'])
            return list(daily.values())[:days]
    except Exception:
        pass
    return None


def get_weather_icon_url(icon_code: str) -> str:
    """Zwraca URL do ikony pogody"""
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


def get_weather_recommendation(weather: Dict) -> str:
    """Zwraca rekomendację na podstawie pogody"""
    if not weather:
        return ""
    temp = weather['temp']
    desc = weather['description'].lower()

    if 'deszcz' in desc or 'rain' in desc:
        return "Weź parasol lub wybierz atrakcje pod dachem"
    elif 'śnieg' in desc or 'snow' in desc:
        return "Ubierz się ciepło, może być ślisko"
    elif temp < 5:
        return "Zimno - ubierz się ciepło"
    elif temp > 30:
        return "Upał - pij dużo wody, szukaj cienia"
    elif 'burz' in desc or 'storm' in desc:
        return "Możliwe burze - sprawdź przed wyjazdem"
    return "Dobra pogoda na wycieczkę!"
