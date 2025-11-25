"""
Nasza Mapa Przygód - Kompletna aplikacja Streamlit
Odkrywaj, planuj i zapisuj swoje przygody na Dolnym Śląsku!
"""

import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
import sys
import os
import math
import requests
from typing import List, Dict, Tuple, Optional

# Dodaj katalog utils do ścieżki
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db_manager import DatabaseManager
from utils.constants import HOME_LOCATION, CATEGORY_COLORS, WEATHER_API_KEY, TRIP_TYPES, TAB_NAMES, EMPTY_STATES
from utils.weather import get_weather, get_weather_forecast, get_weather_icon_url, get_weather_recommendation
from utils.trip_helpers import (
    haversine_distance, estimate_travel_time, parse_time_for_display, get_category_color,
    optimize_route_nearest_neighbor, optimize_route_2opt, optimize_route,
    calculate_route_distance, calculate_trip_stats, calculate_trip_stats_detailed,
    generate_smart_trip, find_best_gallery_for_trip, insert_gallery_into_trip
)
from utils.map_helpers import create_map
from utils.pdf_export import generate_trip_pdf
from utils.qr_generator import generate_trip_qr, generate_google_maps_url

# ============================================
# KONFIGURACJA STRONY
# ============================================
st.set_page_config(
    page_title="Nasza Mapa Przygód",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# SESSION STATE - INICJALIZACJA NA POCZĄTKU
# ============================================
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0
if 'trip_proposals' not in st.session_state:
    st.session_state.trip_proposals = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# ============================================
# VIEWPORT META TAG DLA MOBILE
# ============================================
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# ============================================
# ŁADOWANIE STYLÓW CSS Z PLIKU
# ============================================
def load_css():
    """Ładuje style CSS z zewnętrznego pliku"""
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles', 'main.css')
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)


def render_empty_state(state_key: str):
    """Renderuje przyjazny komunikat dla pustego stanu"""
    state = EMPTY_STATES.get(state_key, {})
    icon = state.get('icon', '📭')
    title = state.get('title', 'Brak danych')
    message = state.get('message', '')

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; color: #64748b;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
        <p style="font-size: 1.1rem; font-weight: 500; color: #334155; margin-bottom: 0.25rem;">{title}</p>
        <p style="font-size: 0.9rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# INICJALIZACJA BAZY DANYCH
# ============================================
@st.cache_resource
def get_database():
    db = DatabaseManager()
    db.import_from_csv()  # Import Dolny Śląsk
    db.import_wielkopolska_from_csv()  # Import Wielkopolska
    db.import_lubuskie_from_csv()  # Import Lubuskie
    db.import_opolskie_from_csv()  # Import Opolskie
    db.import_slaskie_from_csv()  # Import Śląskie
    if hasattr(db, 'import_lodzkie_from_csv'):
        db.import_lodzkie_from_csv()  # Import Łódzkie
    db.import_galleries_from_csv()  # Import galerii handlowych
    # Inicjalizacja użytkowników
    if hasattr(db, 'init_default_users'):
        db.init_default_users()
    return db

db = get_database()

def trigger_refresh():
    st.session_state.refresh_trigger += 1
    # Wyczyść cache przy refresh
    get_cached_places.clear()
    get_cached_statistics.clear()
    get_cached_trips.clear()
    get_cached_notes_stats.clear()


# ============================================
# FUNKCJE CACHE'UJĄCE (OPTYMALIZACJA)
# ============================================
@st.cache_data(ttl=60)  # Cache na 1 minutę
def get_cached_places(_db, categories, vibes, hide_visited, _trigger):
    """Cache'owana wersja get_places_by_filters"""
    return _db.get_places_by_filters(
        categories=categories if categories else None,
        vibes=vibes if vibes else None,
        hide_visited=hide_visited
    )

@st.cache_data(ttl=60)
def get_cached_statistics(_db, _trigger):
    """Cache'owana wersja get_statistics"""
    return _db.get_statistics()

@st.cache_data(ttl=60)
def get_cached_trips(_db, _trigger):
    """Cache'owana wersja get_all_trips"""
    return _db.get_all_trips()

@st.cache_data(ttl=60)
def get_cached_notes_stats(_db, _trigger):
    """Cache'owana wersja get_all_notes_stats"""
    if hasattr(_db, 'get_all_notes_stats'):
        return _db.get_all_notes_stats()
    return {}

@st.cache_data(ttl=300)  # Cache na 5 minut
def get_cached_categories(_db):
    """Cache'owana wersja get_categories"""
    return _db.get_categories()

@st.cache_data(ttl=300)
def get_cached_vibes(_db):
    """Cache'owana wersja get_vibes"""
    return _db.get_vibes()

@st.cache_data(ttl=300)
def get_cached_all_places(_db, _trigger):
    """Cache'owana wersja get_all_places"""
    return _db.get_all_places()

@st.cache_data(ttl=300)
def get_cached_galleries(_db):
    """Cache'owana wersja get_all_galleries"""
    return _db.get_all_galleries()

# ============================================
# FUNKCJE LOGOWANIA
# ============================================
def login(username: str, password: str) -> bool:
    """Próba logowania użytkownika"""
    if not hasattr(db, 'verify_user'):
        # Fallback - akceptuj domyślnych użytkowników bez bazy
        default_users = {
            'mateusz': {'password': 'mateusz123', 'display_name': 'Mateusz'},
            'elena': {'password': 'elena123', 'display_name': 'Elena'}
        }
        user_data = default_users.get(username.lower())
        if user_data and user_data['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user = {'username': username.lower(), 'display_name': user_data['display_name']}
            return True
        return False

    user = db.verify_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        return True
    return False

def logout():
    """Wylogowanie użytkownika"""
    st.session_state.logged_in = False
    st.session_state.user = None

# ============================================
# EKRAN LOGOWANIA
# ============================================
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: #f8fafc;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .login-title {
            text-align: center;
            font-size: 1.8rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            text-align: center;
            color: #64748b;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p class="login-title">Nasza Mapa Przygod</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Zaloguj sie, aby kontynuowac</p>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Nazwa uzytkownika", placeholder="np. mateusz")
            password = st.text_input("Haslo", type="password", placeholder="Wprowadz haslo")
            submit = st.form_submit_button("Zaloguj", use_container_width=True, type="primary")

            if submit:
                if username and password:
                    if login(username, password):
                        st.success(f"Witaj, {st.session_state.user['display_name']}!")
                        st.rerun()
                    else:
                        st.error("Nieprawidlowa nazwa uzytkownika lub haslo")
                else:
                    st.warning("Wprowadz nazwe uzytkownika i haslo")

        st.caption("Uzytkownicy: mateusz / elena")
    st.stop()

# ============================================
# NAGŁÓWEK - MINIMALISTYCZNY + INFO O UŻYTKOWNIKU
# ============================================
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">Nasza Mapa Przygód</h1>
        <p class="app-subtitle">Odkrywaj i planuj wycieczki po Polsce</p>
    </div>
    """, unsafe_allow_html=True)
with header_col2:
    if st.session_state.user:
        st.markdown(f"**{st.session_state.user['display_name']}**")
        if st.button("Wyloguj", use_container_width=True):
            logout()
            st.rerun()

# ============================================
# STATYSTYKI - LINIA
# ============================================
stats = get_cached_statistics(db, st.session_state.refresh_trigger)

st.markdown(f"""
<div class="stats-row">
    <div class="stat-item">
        <span class="stat-number">{stats.get('total_places', 0)}</span>
        <span class="stat-label">miejsc</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">{stats.get('visited_places', 0)}</span>
        <span class="stat-label">odwiedzonych</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">{stats.get('total_trips', 0)}</span>
        <span class="stat-label">wycieczek</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">{stats.get('completed_trips', 0)}</span>
        <span class="stat-label">zrealizowanych</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# TABY NAWIGACYJNE
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(TAB_NAMES)

# ============================================
# TAB 1: MAPA I ODKRYWANIE
# ============================================
with tab1:
    with st.sidebar:
        st.markdown('<p class="sidebar-title">Filtry</p>', unsafe_allow_html=True)

        categories = get_cached_categories(db)
        vibes = get_cached_vibes(db)

        selected_categories = st.multiselect(
            "Kategorie",
            options=categories,
            default=[],
            placeholder="Wybierz kategorie...",
            help="Filtruj miejsca według kategorii"
        )

        selected_vibes = st.multiselect(
            "Charakter",
            options=vibes,
            default=[],
            placeholder="Wybierz...",
            help="Filtruj według charakterystyki"
        )

        hide_visited = st.checkbox(
            "Ukryj odwiedzone",
            value=False,
            help="Pokaż tylko nieodwiedzone miejsca"
        )

        if st.button("Wyczyść filtry", use_container_width=True):
            st.rerun()

        st.markdown('<p class="sidebar-title">Legenda</p>', unsafe_allow_html=True)

        for cat, color in CATEGORY_COLORS.items():
            st.markdown(f"""
            <div class="legend-item">
                <div class="legend-dot" style="background: {color};"></div>
                <span>{cat}</span>
            </div>
            """, unsafe_allow_html=True)

    # Używamy cache'owanych zapytań dla wydajności
    places = get_cached_places(
        db,
        tuple(selected_categories) if selected_categories else None,
        tuple(selected_vibes) if selected_vibes else None,
        hide_visited,
        st.session_state.refresh_trigger
    )

    st.markdown(f'<p class="section-title">Mapa ({len(places)} miejsc)</p>', unsafe_allow_html=True)

    # Mapa - pełna szerokość na górze
    if places:
        all_galleries = get_cached_galleries(db)
        m = create_map(places, show_home=True, galleries=all_galleries)
        st_folium(m, height=500, use_container_width=True, key="main_map")
    else:
        render_empty_state("no_places")

    # Lista miejsc - pod mapą
    st.markdown('<p class="section-title">Lista miejsc</p>', unsafe_allow_html=True)
    search_query = st.text_input("Szukaj", placeholder="Wpisz nazwę miejsca", label_visibility="collapsed")

    filtered_places = places
    if search_query:
        filtered_places = [p for p in places if search_query.lower() in p['name'].lower()]

    st.caption(f"Wyświetlono {len(filtered_places)} miejsc")

    # Lista w 4 kolumnach
    cols = st.columns(4)

    # Pobierz statystyki notatek (cache'owane)
    all_notes_stats = get_cached_notes_stats(db, st.session_state.refresh_trigger)

    for i, place in enumerate(filtered_places):
        dist = haversine_distance(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'],
                                 place['latitude'], place['longitude'])

        # Pobierz stats z cache lub domyślne
        place_stats = all_notes_stats.get(place['id'], {'count': 0, 'avg_rating': None})
        notes_count = place_stats['count']
        avg_rating = place_stats['avg_rating']

        # Label z oceną jeśli jest
        rating_badge = f" ★{avg_rating}" if avg_rating else ""
        visited_badge = " ✓" if place['is_visited'] else ""
        expander_label = f"{place['name']}{visited_badge}{rating_badge}"

        # Rozłożenie na 4 kolumny
        with cols[i % 4]:
            with st.expander(expander_label, expanded=False):
                st.markdown(f"**{place['category']}** · {place['location']} · {dist:.1f} km")
                st.markdown(place['description'])
                st.caption(f"Czas: {place['time_needed']} | {place['season_hours']}")

                if not place['is_visited']:
                    if st.button("Oznacz jako odwiedzone", key=f"v_{place['id']}", use_container_width=True):
                        db.mark_as_visited(place['id'])
                        st.toast(f"✅ {place['name']} - odwiedzone!")
                        trigger_refresh()
                        st.rerun()
                else:
                    if st.button("Cofnij odwiedzenie", key=f"u_{place['id']}", use_container_width=True):
                        db.mark_as_unvisited(place['id'])
                        st.toast(f"↩️ {place['name']} - cofnięto")
                        trigger_refresh()
                        st.rerun()

                # Sekcja notatek (uproszczona)
                if notes_count > 0:
                    st.markdown("---")
                    st.caption(f"📝 {notes_count} notatek")
                    # Lazy load notatek - tylko na żądanie
                    if st.button("Pokaż notatki", key=f"show_notes_{place['id']}", use_container_width=True):
                        notes = db.get_place_notes(place['id'])
                        for note in notes[:3]:
                            rating_stars = "★" * note['rating'] if note['rating'] else ""
                            author = f" - {note['author']}" if note['author'] else ""
                            st.markdown(f"**{rating_stars}**{author}")
                            st.caption(note['note_text'][:100] + ("..." if len(note['note_text']) > 100 else ""))

                # Formularz dodawania notatki (tylko dla odwiedzonych)
                if place['is_visited']:
                    with st.popover("➕ Notatka"):
                        new_note = st.text_area("Twoja notatka", key=f"note_text_{place['id']}", height=80)
                        note_rating = st.slider("Ocena", 1, 5, 4, key=f"note_rating_{place['id']}")
                        note_date = st.date_input("Data wizyty", key=f"note_date_{place['id']}")

                        if st.button("Zapisz", key=f"save_note_{place['id']}"):
                            if new_note.strip():
                                user_id = st.session_state.user.get('id') if st.session_state.user else None
                                if hasattr(db, 'add_place_note'):
                                    db.add_place_note(
                                        place['id'],
                                        new_note.strip(),
                                        note_rating,
                                        note_date.isoformat() if note_date else None,
                                        user_id
                                    )
                                    st.toast("📝 Notatka zapisana!")
                                    st.rerun()
                            else:
                                st.toast("⚠️ Wpisz treść notatki", icon="⚠️")

# ============================================
# TAB 2: KREATOR WYCIECZEK
# ============================================
with tab2:
    st.markdown('<p class="section-title">Kreator wycieczek</p>', unsafe_allow_html=True)

    st.caption(f"Punkt startowy: {HOME_LOCATION['address']}")

    trip_mode = st.radio(
        "Wybierz tryb:",
        ["Automatyczny (zaplanuj trasę)", "Ręczny (sam wybierasz miejsca)"],
        horizontal=True
    )

    if "Automatyczny" in trip_mode:
        st.markdown("#### Ustawienia")

        # Wybór województwa
        selected_region = st.selectbox(
            "Województwo",
            options=["Wszystkie", "Dolny Śląsk", "Wielkopolskie", "Lubuskie", "Opolskie", "Śląskie", "Łódzkie"],
            index=0,
            help="Wybierz region do planowania wycieczki"
        )

        # Kategorie na pełną szerokość
        pref_categories = st.multiselect(
            "Preferowane kategorie",
            options=get_cached_categories(db),
            placeholder="Wszystkie kategorie"
        )

        # Typ wycieczki
        st.markdown("#### Typ wycieczki")
        trip_type = st.selectbox(
            "Wybierz typ wycieczki",
            options=list(TRIP_TYPES.keys()),
            index=1,  # Domyślnie "Jednodniowa"
            help="Określa czas i liczbę miejsc do odwiedzenia"
        )

        # Pobierz ustawienia dla wybranego typu
        trip_config = TRIP_TYPES[trip_type]

        # Ustawienia - zależne od typu wycieczki
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if trip_type == "Niestandardowa":
                max_places = st.slider("Liczba miejsc", 2, 20, 5)
                max_hours = st.slider("Maks. czas (h)", 2.0, 48.0, 8.0, 0.5)
            else:
                max_places = trip_config['max_places']
                max_hours = trip_config['max_hours']
                st.info(f"Miejsca: do {max_places} | Czas: do {max_hours}h | Dni: {trip_config['days']}")
        with col_s2:
            num_proposals = st.slider("Liczba propozycji", 1, 5, 3)
            prefer_unvisited = st.checkbox("Preferuj nieodwiedzone", True)

        # Zaawansowane opcje
        with st.expander("Opcje zaawansowane"):
            route_algorithm = st.radio(
                "Algorytm optymalizacji trasy",
                options=["2opt", "nearest_neighbor"],
                format_func=lambda x: "2-opt (lepszy, wolniejszy)" if x == "2opt" else "Nearest Neighbor (szybszy)",
                index=0,
                horizontal=True,
                help="2-opt znajduje krótsze trasy, ale wymaga więcej obliczeń"
            )

        # Pogoda dla punktu startowego
        st.markdown("#### Pogoda")
        weather = get_weather(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'])
        if weather:
            weather_col1, weather_col2 = st.columns([1, 2])
            with weather_col1:
                st.image(get_weather_icon_url(weather['icon']), width=60)
            with weather_col2:
                st.markdown(f"**{weather['temp']}°C** - {weather['description']}")
                st.caption(f"Odczuwalna: {weather['feels_like']}°C | Wiatr: {weather['wind_speed']} km/h")
            recommendation = get_weather_recommendation(weather)
            if recommendation:
                st.caption(f"Tip: {recommendation}")

            # Prognoza dla wycieczek wielodniowych
            if trip_config['days'] and trip_config['days'] > 1:
                forecast = get_weather_forecast(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'], trip_config['days'])
                if forecast:
                    st.caption("Prognoza na kolejne dni:")
                    forecast_cols = st.columns(min(len(forecast), 3))
                    for i, day in enumerate(forecast[:3]):
                        with forecast_cols[i]:
                            st.caption(f"{day['date']}: {round(day['temp_min'])}°-{round(day['temp_max'])}°C")
        else:
            st.caption("Nie udało się pobrać pogody")

        # Opcja zakupów
        st.markdown("#### + Zakupy")
        include_shopping = st.checkbox("Dodaj przystanek na zakupy", False,
                                       help="Automatycznie dodaj galerię handlową po drodze")

        gallery_types_selected = None
        if include_shopping:
            all_gallery_types = db.get_gallery_types()
            gallery_types_selected = st.multiselect(
                "Preferowany typ galerii",
                options=all_gallery_types,
                default=[],
                placeholder="Dowolna galeria",
                help="Zostaw puste, aby wybrać najbliższą galerię"
            )
            st.caption("Galeria zostanie dopasowana do trasy (min. dodatkowy dystans)")

        if st.button("Wygeneruj wycieczki", use_container_width=True, type="primary"):
            all_places = get_cached_all_places(db, st.session_state.refresh_trigger)

            # Filtruj według województwa
            if selected_region == "Dolny Śląsk":
                # Miejsca z Dolnego Śląska (współrzędne około 50-51.5 lat, 14.5-17.5 lon)
                all_places = [p for p in all_places if 50.0 <= p['latitude'] <= 51.5 and 14.5 <= p['longitude'] <= 17.5]
            elif selected_region == "Wielkopolskie":
                # Miejsca z Wielkopolski (współrzędne około 51.5-53.5 lat, 15.5-19 lon)
                all_places = [p for p in all_places if 51.5 <= p['latitude'] <= 53.5 and 15.5 <= p['longitude'] <= 19.5]
            elif selected_region == "Lubuskie":
                # Miejsca z Lubuskiego (współrzędne około 51.5-53.0 lat, 14.5-16.5 lon)
                all_places = [p for p in all_places if 51.5 <= p['latitude'] <= 53.0 and 14.5 <= p['longitude'] <= 16.5]
            elif selected_region == "Opolskie":
                # Miejsca z Opolskiego (współrzędne około 50.0-51.2 lat, 17.0-18.5 lon)
                all_places = [p for p in all_places if 50.0 <= p['latitude'] <= 51.2 and 17.0 <= p['longitude'] <= 18.5]
            elif selected_region == "Śląskie":
                # Miejsca ze Śląskiego (współrzędne około 49.0-50.5 lat, 18.5-20.5 lon)
                all_places = [p for p in all_places if 49.0 <= p['latitude'] <= 50.5 and 18.5 <= p['longitude'] <= 20.5]
            elif selected_region == "Łódzkie":
                # Miejsca z Łódzkiego (współrzędne około 51.0-52.5 lat, 18.5-20.5 lon)
                all_places = [p for p in all_places if 51.0 <= p['latitude'] <= 52.5 and 18.5 <= p['longitude'] <= 20.5]

            all_galleries = db.get_all_galleries() if include_shopping else []
            proposals = []
            variant_names = ["Najbliższe miejsca", "Blisko-średnie", "Średni dystans", "Średnio-daleko", "Dalsze miejsca"]

            with st.spinner("Planuję trasy..."):
                for i in range(num_proposals):
                    trip_places, trip_stats = generate_smart_trip(
                        all_places, pref_categories if pref_categories else None,
                        max_places, max_hours, prefer_unvisited, variant=i,
                        algorithm=route_algorithm
                    )
                    if trip_places:
                        # Dodaj galerię jeśli opcja włączona
                        gallery_info = None
                        if include_shopping and all_galleries:
                            best_gallery = find_best_gallery_for_trip(
                                trip_places, all_galleries,
                                max_detour_km=20.0,
                                gallery_types=gallery_types_selected if gallery_types_selected else None
                            )
                            if best_gallery:
                                trip_places = insert_gallery_into_trip(trip_places, best_gallery)
                                trip_stats = calculate_trip_stats_detailed(trip_places)
                                gallery_info = best_gallery

                        proposals.append({
                            'name': variant_names[i],
                            'places': trip_places,
                            'stats': trip_stats,
                            'gallery': gallery_info
                        })

            if proposals:
                st.session_state.trip_proposals = proposals
                st.toast(f"✨ Wygenerowano {len(proposals)} propozycji!")
            else:
                render_empty_state("no_proposals")

        if st.session_state.get('trip_proposals'):
            proposals = st.session_state.trip_proposals

            st.markdown("---")
            st.markdown("#### Propozycje tras")

            # Tabs dla propozycji
            if len(proposals) > 1:
                prop_tabs = st.tabs([f"Propozycja {i+1}: {p['name']}" for i, p in enumerate(proposals)])
            else:
                prop_tabs = [st.container()]

            for idx, (tab, proposal) in enumerate(zip(prop_tabs, proposals)):
                with tab:
                    trip_places = proposal['places']
                    trip_stats = proposal['stats']
                    gallery_info = proposal.get('gallery')

                    # Info o galerii
                    if gallery_info:
                        st.success(f"Zakupy: **{gallery_info['name']}** ({gallery_info['gallery_type']}) - +{gallery_info.get('_detour_km', 0):.1f} km")

                    # Metryki - 2x2 grid na mobile (lepiej niż 4 w rzędzie)
                    row1_c1, row1_c2 = st.columns(2)
                    row1_c1.metric("Miejsca", trip_stats['place_count'])
                    row1_c2.metric("Dystans", f"{trip_stats['total_distance']:.0f} km")
                    row2_c1, row2_c2 = st.columns(2)
                    row2_c1.metric("Zwiedzanie", f"{trip_stats['visit_time']:.1f} h")
                    row2_c2.metric("Przejazdy", f"{trip_stats['travel_time']:.1f} h")

                    # Mapa
                    route_map = create_map(trip_places, show_home=True, show_route=True)
                    st_folium(route_map, height=450, use_container_width=True, key=f"map_{idx}")

                    # Szczegółowy plan trasy
                    st.markdown("**Szczegółowy plan trasy:**")

                    segments = trip_stats.get('segments', [])
                    for i, place in enumerate(trip_places):
                        # Dojazd do miejsca
                        if i < len(segments):
                            seg = segments[i]
                            st.caption(f"  ↓ {seg['distance']:.1f} km (~{seg['travel_time']*60:.0f} min jazdy)")

                        # Miejsce - z oznaczeniem galerii
                        is_gallery = place.get('_is_gallery', False)
                        if is_gallery:
                            st.markdown(f"**{i+1}. {place['name']}** - {place['location']}")
                            st.caption(f"     Czas na zakupy: {place['time_needed']} | {place.get('_gallery_type', 'Galeria')}")
                        else:
                            st.markdown(f"**{i+1}. {place['name']}** - {place['location']}")
                            st.caption(f"     Czas zwiedzania: {place['time_needed']}")

                    # Powrót do domu
                    if segments:
                        last_seg = segments[-1]
                        st.caption(f"  ↓ {last_seg['distance']:.1f} km (~{last_seg['travel_time']*60:.0f} min jazdy)")
                        st.markdown("**Dom**")

                    # Podsumowanie
                    st.markdown("---")
                    total_h = int(trip_stats['total_time'])
                    total_m = int((trip_stats['total_time'] - total_h) * 60)
                    st.info(f"Łączny czas wycieczki: **{total_h}h {total_m}min** (w tym {trip_stats['travel_time']:.1f}h jazdy)")

                    # Eksport PDF i QR
                    pdf_col1, pdf_col2 = st.columns([1, 1])
                    with pdf_col1:
                        pdf_bytes = generate_trip_pdf(
                            f"Wycieczka - {proposal['name']}",
                            trip_places,
                            trip_stats,
                            HOME_LOCATION['address']
                        )
                        st.download_button(
                            label="Pobierz PDF",
                            data=pdf_bytes,
                            file_name=f"wycieczka_{proposal['name'].lower().replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{idx}",
                            use_container_width=True
                        )
                    with pdf_col2:
                        # Link do Google Maps
                        maps_url = generate_google_maps_url(trip_places, HOME_LOCATION)
                        st.link_button("Otwórz w Google Maps", maps_url, use_container_width=True)

                    # QR kod (w popoverze)
                    with st.popover("Pokaż kod QR"):
                        qr_bytes = generate_trip_qr(trip_places, proposal['name'], HOME_LOCATION)
                        st.image(qr_bytes, caption="Zeskanuj, aby otworzyć trasę w Google Maps")
                        st.caption("Kod QR zawiera link do nawigacji w Google Maps")

                    # Zapisywanie
                    with st.form(f"save_prop_{idx}"):
                        trip_name = st.text_input("Nazwa wycieczki", f"Wycieczka - {proposal['name']}", key=f"name_{idx}")
                        trip_desc = st.text_area("Opis (opcjonalnie)", key=f"desc_{idx}")
                        if st.form_submit_button("Zapisz ten plan", use_container_width=True):
                            if trip_name:
                                # Filtruj tylko miejsca (nie galerie) do zapisu
                                places_to_save = [p for p in trip_places if not p.get('_is_gallery', False)]
                                place_ids = [p['id'] for p in places_to_save]

                                # Dodaj info o galerii do opisu
                                final_desc = trip_desc
                                if gallery_info:
                                    gallery_note = f"\n\n+ Zakupy: {gallery_info['name']} ({gallery_info['location']})"
                                    final_desc = (trip_desc or "") + gallery_note

                                trip_id = db.create_trip(trip_name, place_ids, final_desc)
                                if trip_id:
                                    st.toast(f"💾 Zapisano '{trip_name}'!")
                                    st.session_state.trip_proposals = []
                                    st.rerun()

    else:
        st.markdown("#### Ręczne planowanie")
        all_places = get_cached_all_places(db, st.session_state.refresh_trigger)
        place_options = {f"{p['name']} ({p['location']})": p['id'] for p in all_places}

        with st.form("manual_trip"):
            trip_name = st.text_input("Nazwa wycieczki", placeholder="np. Weekend w górach")
            trip_desc = st.text_area("Opis (opcjonalnie)")
            selected_names = st.multiselect("Wybierz miejsca", list(place_options.keys()), placeholder="Kliknij, aby wybrać")
            optimize = st.checkbox("Optymalizuj kolejność", True)

            if st.form_submit_button("Zapisz plan", use_container_width=True, type="primary"):
                if trip_name and selected_names:
                    ids = [place_options[n] for n in selected_names]
                    if optimize:
                        sel_places = [p for p in all_places if p['id'] in ids]
                        opt = optimize_route_nearest_neighbor(sel_places, HOME_LOCATION['latitude'], HOME_LOCATION['longitude'])
                        ids = [p['id'] for p in opt]
                    trip_id = db.create_trip(trip_name, ids, trip_desc)
                    if trip_id:
                        st.toast(f"💾 Zapisano '{trip_name}'!")
                        st.rerun()
                else:
                    st.toast("⚠️ Podaj nazwę i wybierz miejsca!", icon="⚠️")

        if selected_names:
            st.markdown("---")
            ids = [place_options[n] for n in selected_names]
            sel_places = [p for p in all_places if p['id'] in ids]
            if optimize:
                sel_places = optimize_route_nearest_neighbor(sel_places, HOME_LOCATION['latitude'], HOME_LOCATION['longitude'])
            stats = calculate_trip_stats(sel_places)
            c1, c2, c3 = st.columns(3)
            c1.metric("Miejsca", len(sel_places))
            c2.metric("Dystans", f"{stats['total_distance']:.0f} km")
            c3.metric("Czas", f"{stats['total_time']:.1f} h")
            st_folium(create_map(sel_places, show_home=True, show_route=True), height=450, use_container_width=True)

# ============================================
# TAB 3: NASZE PLANY
# ============================================
with tab3:
    st.markdown('<p class="section-title">Nasze plany</p>', unsafe_allow_html=True)

    trips = get_cached_trips(db, st.session_state.refresh_trigger)

    if trips:
        active = [t for t in trips if not t['is_completed']]
        completed = [t for t in trips if t['is_completed']]

        st.markdown("**Aktywne plany**")
        if active:
            for trip in active:
                with st.expander(f"{trip['name']} ({trip['place_count']} miejsc, ~{trip['total_time_hours']:.1f}h)"):
                    if trip['description']:
                        st.markdown(f"*{trip['description']}*")
                    st.markdown(f"**Miejsca:** {trip['place_names']}")

                    # Pobierz szczegóły dla PDF
                    trip_details = db.get_trip_details(trip['id']) if hasattr(db, 'get_trip_details') else None

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        if st.button("Zrealizowano", key=f"c_{trip['id']}", use_container_width=True, type="primary"):
                            db.complete_trip(trip['id'])
                            st.toast("🎉 Wycieczka zrealizowana!")
                            trigger_refresh()
                            st.rerun()
                    with c2:
                        if trip_details and trip_details.get('places'):
                            places = trip_details['places']
                            stats = calculate_trip_stats_detailed(places)
                            pdf_bytes = generate_trip_pdf(
                                trip['name'],
                                places,
                                stats,
                                HOME_LOCATION['address']
                            )
                            st.download_button(
                                label="PDF",
                                data=pdf_bytes,
                                file_name=f"{trip['name'].lower().replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                key=f"pdf_trip_{trip['id']}",
                                use_container_width=True
                            )
                    with c3:
                        if trip_details and trip_details.get('places'):
                            maps_url = generate_google_maps_url(trip_details['places'], HOME_LOCATION)
                            st.link_button("Maps", maps_url, use_container_width=True)
                    with c4:
                        if st.button("Usuń", key=f"d_{trip['id']}", use_container_width=True):
                            db.delete_trip(trip['id'])
                            st.toast("🗑️ Plan usunięty")
                            trigger_refresh()
                            st.rerun()
        else:
            render_empty_state("no_active_trips")

        st.markdown("---")
        st.markdown("**Zrealizowane**")
        if completed:
            for trip in completed:
                with st.expander(f"{trip['name']} ({trip['place_count']} miejsc)"):
                    st.markdown(f"**Miejsca:** {trip['place_names']}")
                    if st.button("Usuń z historii", key=f"dc_{trip['id']}"):
                        db.delete_trip(trip['id'])
                        st.toast("🗑️ Usunięto z historii")
                        trigger_refresh()
                        st.rerun()
        else:
            render_empty_state("no_completed_trips")
    else:
        render_empty_state("no_trips")

# ============================================
# TAB 4: DODAJ MIEJSCE
# ============================================
with tab4:
    st.markdown('<p class="section-title">Dodaj nowe miejsce</p>', unsafe_allow_html=True)

    with st.form("add_place"):
        # Podstawowe info - pełna szerokość na mobile
        new_name = st.text_input("Nazwa *", placeholder="np. Zamek Książ")

        col_cat_loc = st.columns(2)
        with col_cat_loc[0]:
            new_category = st.selectbox("Kategoria *", ["Natura", "Przygoda", "Historia", "Nauka", "Architektura", "Relaks", "Punkt widokowy", "Inne"])
        with col_cat_loc[1]:
            new_location = st.text_input("Miejscowość *", placeholder="np. Wałbrzych")

        # Współrzędne GPS
        st.caption("Współrzędne GPS")
        col_gps = st.columns(2)
        with col_gps[0]:
            new_lat = st.number_input("Szerokość", 49.0, 52.0, 50.9, 0.0001, format="%.4f")
        with col_gps[1]:
            new_lon = st.number_input("Długość", 14.0, 18.0, 15.7, 0.0001, format="%.4f")

        # Dodatkowe info
        col_extra = st.columns(2)
        with col_extra[0]:
            new_time = st.text_input("Czas zwiedzania", placeholder="np. 2-3h")
        with col_extra[1]:
            new_season = st.text_input("Dostępność", placeholder="Cały rok")

        new_vibe = st.text_input("Hashtagi", placeholder="#historyczne #zamki #rodzinnie")
        new_desc = st.text_area("Opis", placeholder="Krótki opis atrakcji...", height=80)

        if st.form_submit_button("Dodaj miejsce", use_container_width=True, type="primary"):
            if new_name and new_location:
                place_id = db.add_place(new_name, new_category, new_location, new_lat, new_lon,
                                        new_vibe or "", new_time or "1-2h", new_desc or "", new_season or "Cały rok")
                if place_id:
                    st.toast(f"📍 Dodano '{new_name}'!")
                    trigger_refresh()
                    st.rerun()
            else:
                st.toast("⚠️ Wypełnij wymagane pola!", icon="⚠️")

    st.markdown("---")
    st.markdown("**Podgląd lokalizacji**")
    dist = haversine_distance(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'], new_lat, new_lon)
    st.caption(f"Odległość od domu: {dist:.1f} km")

    preview = folium.Map(location=[new_lat, new_lon], zoom_start=11, tiles='cartodbpositron')
    folium.Marker([HOME_LOCATION['latitude'], HOME_LOCATION['longitude']], tooltip="Dom",
                  icon=folium.Icon(color='darkred', icon='home', prefix='fa')).add_to(preview)
    folium.Marker([new_lat, new_lon], tooltip=new_name or "Nowe miejsce",
                  icon=folium.Icon(color='red', icon='star', prefix='fa')).add_to(preview)
    folium.PolyLine([(HOME_LOCATION['latitude'], HOME_LOCATION['longitude']), (new_lat, new_lon)],
                    weight=2, color='gray', dash_array='5').add_to(preview)
    st_folium(preview, height=350, use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("Nasza Mapa Przygód · Wersja 4.2 · Punkt startowy: Jelenia Góra")