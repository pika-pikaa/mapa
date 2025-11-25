"""
Stałe konfiguracyjne dla aplikacji Nasza Mapa Przygód
"""

# Lokalizacja domowa (punkt startowy)
HOME_LOCATION = {
    "name": "Dom (Jelenia Góra, ul. Ptasia 12)",
    "latitude": 50.9044,
    "longitude": 15.7194,
    "address": "Jelenia Góra, ul. Ptasia 12"
}

# Kolory kategorii miejsc
CATEGORY_COLORS = {
    "Natura": "#22c55e",
    "Przygoda": "#f97316",
    "Historia": "#a855f7",
    "Nauka": "#3b82f6",
    "Architektura": "#1e40af",
    "Relaks": "#84cc16",
    "Punkt widokowy": "#ef4444",
    "Inne": "#6b7280"
}

# Klucz API pogody (OpenWeatherMap)
WEATHER_API_KEY = "99b9762819df745313f613ab600c866b"

# Typy wycieczek z limitami czasowymi
TRIP_TYPES = {
    "Półdniowa (do 4h)": {"max_hours": 4.0, "max_places": 3, "days": 1},
    "Jednodniowa (do 8h)": {"max_hours": 8.0, "max_places": 5, "days": 1},
    "Pełny dzień (do 12h)": {"max_hours": 12.0, "max_places": 7, "days": 1},
    "Weekendowa (2 dni)": {"max_hours": 16.0, "max_places": 10, "days": 2},
    "Długa (3 dni)": {"max_hours": 24.0, "max_places": 15, "days": 3},
    "Niestandardowa": {"max_hours": None, "max_places": None, "days": None}
}

# Nazwy zakładek z ikonami
TAB_NAMES = [
    "🗺️ Odkrywaj",
    "✨ Planuj",
    "📋 Twoje plany",
    "➕ Dodaj nowe"
]

# Empty states - komunikaty dla pustych list
EMPTY_STATES = {
    "no_places": {
        "icon": "🔍",
        "title": "Brak miejsc do wyświetlenia",
        "message": "Zmień filtry lub dodaj nowe miejsca",
        "action": "Wyczyść filtry"
    },
    "no_trips": {
        "icon": "🎒",
        "title": "Nie masz jeszcze żadnych planów",
        "message": "Stwórz swoją pierwszą wycieczkę w Kreatorze!",
        "action": "Przejdź do Kreatora"
    },
    "no_active_trips": {
        "icon": "🚀",
        "title": "Brak aktywnych planów",
        "message": "Wszystkie wycieczki zrealizowane? Czas na nowe przygody!",
        "action": "Zaplanuj wycieczkę"
    },
    "no_completed_trips": {
        "icon": "🏆",
        "title": "Jeszcze żadna wycieczka nie została zrealizowana",
        "message": "Wybierz się na pierwszą przygodę i oznacz ją jako zrealizowaną!",
        "action": None
    },
    "no_search_results": {
        "icon": "🤷",
        "title": "Nie znaleziono wyników",
        "message": "Spróbuj innych słów kluczowych",
        "action": None
    },
    "no_proposals": {
        "icon": "🎯",
        "title": "Brak propozycji wycieczek",
        "message": "Zmień preferencje i spróbuj ponownie",
        "action": None
    }
}
