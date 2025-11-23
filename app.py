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
# STAŁE KONFIGURACYJNE
# ============================================
HOME_LOCATION = {
    "name": "Dom (Jelenia Góra, ul. Ptasia 12)",
    "latitude": 50.9044,
    "longitude": 15.7194,
    "address": "Jelenia Góra, ul. Ptasia 12"
}

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


# ============================================
# VIEWPORT META TAG DLA MOBILE
# ============================================
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# ============================================
# MINIMALISTYCZNE STYLE CSS
# ============================================
st.markdown("""
<style>
    /* ===== IMPORT FONTÓW ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* ===== ZMIENNE CSS - MINIMALISTYCZNA PALETA ===== */
    :root {
        --primary: #2563eb;
        --primary-hover: #1d4ed8;
        --success: #16a34a;
        --warning: #ca8a04;
        --error: #dc2626;
        --bg: #ffffff;
        --bg-subtle: #f9fafb;
        --text: #111827;
        --text-secondary: #6b7280;
        --text-muted: #9ca3af;
        --border: #e5e7eb;
        --border-hover: #d1d5db;
        --radius: 8px;
    }

    /* ===== PODSTAWY ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    /* Globalne wymuszenie wysokości iframe (mapa) */
    iframe {
        min-height: 500px !important;
    }

    /* Wymuszenie jasnego motywu */
    .stApp, .stApp > div, .main, .block-container {
        background-color: var(--bg) !important;
    }

    /* Tekst w głównej części */
    .stApp p, .stApp span, .stApp div, .stApp label {
        color: var(--text);
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* ===== NAGŁÓWEK ===== */
    .app-header {
        padding: 2rem 0 1.5rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
    }

    .app-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text);
        margin: 0 0 0.25rem 0;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* ===== STATYSTYKI ===== */
    .stats-row {
        display: flex;
        gap: 2rem;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid var(--border);
    }

    .stat-item {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
    }

    .stat-number {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text);
    }

    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
    }

    /* ===== TABY ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid var(--border);
        gap: 0;
        padding: 0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        padding: 0.75rem 1.25rem;
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--text-secondary);
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text);
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        background: transparent !important;
        border-bottom: 2px solid var(--primary) !important;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: var(--bg-subtle);
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text);
    }

    .sidebar-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin: 1.5rem 0 0.75rem;
    }

    /* ===== KARTY MIEJSC ===== */
    .place-card {
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.15s;
    }

    .place-card:hover {
        border-color: var(--border-hover);
    }

    .place-name {
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--text);
        margin: 0 0 0.25rem 0;
    }

    .place-location {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin: 0;
    }

    .place-meta {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    /* ===== BADGE KATEGORII ===== */
    .category-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.25rem 0.625rem;
        background: var(--bg-subtle);
        border: 1px solid var(--border);
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
    }

    /* ===== PRZYCISKI ===== */
    .stButton > button {
        border-radius: var(--radius);
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
        border: 1px solid var(--border);
        background: var(--bg);
        color: var(--text);
        transition: all 0.15s;
    }

    .stButton > button:hover {
        background: var(--bg-subtle);
        border-color: var(--border-hover);
    }

    .stButton > button[kind="primary"] {
        background: var(--primary);
        border-color: var(--primary);
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--primary-hover);
        border-color: var(--primary-hover);
    }

    /* ===== INPUTY - JASNE TŁO ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg) !important;
        color: var(--text) !important;
        border-radius: var(--radius);
        border: 1px solid var(--border) !important;
        font-size: 0.9rem;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 1px var(--primary);
    }

    /* ===== SELECTBOX I MULTISELECT - JASNE TŁO ===== */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg) !important;
        border-radius: var(--radius);
    }

    .stSelectbox [data-baseweb="select"] > div,
    .stMultiSelect [data-baseweb="select"] > div {
        background: var(--bg) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }

    .stSelectbox [data-baseweb="select"] span,
    .stMultiSelect [data-baseweb="select"] span {
        color: var(--text) !important;
    }

    /* Dropdown menu */
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"] {
        background: var(--bg) !important;
        border: 1px solid var(--border) !important;
    }

    [data-baseweb="menu"] li {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    [data-baseweb="menu"] li:hover {
        background: var(--bg-subtle) !important;
    }

    /* Number input */
    .stNumberInput > div > div > input {
        background: var(--bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }

    /* ===== EXPANDERY - PEŁNE STYLE ===== */
    /* Nowe selektory Streamlit */
    [data-testid="stExpander"] {
        background: var(--bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }

    [data-testid="stExpander"] summary {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p {
        color: var(--text) !important;
    }

    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: var(--bg) !important;
    }

    [data-testid="stExpander"] [data-testid="stExpanderDetails"] p,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] span,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] div {
        color: var(--text) !important;
    }

    /* Stare selektory dla kompatybilności */
    .streamlit-expanderHeader {
        background: var(--bg) !important;
        border-radius: var(--radius);
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--text) !important;
        border: 1px solid var(--border);
    }

    .streamlit-expanderContent {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    /* Wszystkie elementy w expander */
    details {
        background: var(--bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        margin-bottom: 0.5rem;
    }

    details summary {
        color: var(--text) !important;
        padding: 0.75rem 1rem;
        cursor: pointer;
    }

    details summary:hover {
        background: var(--bg-subtle) !important;
    }

    details[open] > div {
        padding: 0 1rem 1rem;
        background: var(--bg) !important;
    }

    details svg {
        fill: var(--text) !important;
        stroke: var(--text) !important;
    }

    /* ===== INFO/ALERT BOXES ===== */
    [data-testid="stAlert"] {
        background: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
        border-radius: var(--radius) !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div {
        color: #1e40af !important;
    }

    /* Success alert */
    [data-testid="stAlert"][data-baseweb*="success"],
    .stSuccess {
        background: #f0fdf4 !important;
        border-color: #bbf7d0 !important;
    }

    .stSuccess p, .stSuccess span {
        color: #166534 !important;
    }

    /* Error alert */
    [data-testid="stAlert"][data-baseweb*="error"],
    .stError {
        background: #fef2f2 !important;
        border-color: #fecaca !important;
    }

    .stError p, .stError span {
        color: #991b1b !important;
    }

    /* Caption */
    [data-testid="stCaptionContainer"],
    .stCaption {
        color: var(--text-secondary) !important;
    }

    [data-testid="stCaptionContainer"] p {
        color: var(--text-secondary) !important;
    }

    /* ===== METRYKI ===== */
    [data-testid="stMetric"] {
        background: var(--bg-subtle);
        padding: 0.75rem;
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }

    [data-testid="stMetricValue"] {
        font-weight: 600;
        font-size: 1.25rem;
        color: var(--text);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }

    /* ===== KARTY WYCIECZEK ===== */
    .trip-card {
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .trip-card.completed {
        background: var(--bg-subtle);
    }

    /* ===== LEGENDA ===== */
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0;
        font-size: 0.8rem;
        color: var(--text-secondary);
    }

    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }

    /* ===== SEKCJE ===== */
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text);
        margin: 0 0 1rem 0;
    }

    /* ===== MAPA - PROPORCJE ===== */
    /* Wszystkie możliwe selektory dla mapy Folium */
    iframe[title="streamlit_folium.st_folium"],
    iframe[src*="streamlit_folium"],
    .element-container iframe,
    [data-testid="stCustomComponentV1"] iframe,
    div[data-testid="stCustomComponentV1"] > div > iframe {
        min-height: 500px !important;
        height: 500px !important;
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }

    /* Kontener komponentu */
    [data-testid="stCustomComponentV1"],
    [data-testid="stCustomComponentV1"] > div {
        min-height: 500px !important;
        height: auto !important;
    }

    /* Kontener element */
    .element-container:has(iframe) {
        min-height: 500px !important;
    }

    /* ===== RADIO BUTTONS ===== */
    .stRadio > label {
        color: var(--text) !important;
    }

    .stRadio [data-baseweb="radio"] > div {
        color: var(--text) !important;
    }

    .stRadio p, .stRadio span {
        color: var(--text) !important;
    }

    /* ===== CHECKBOXY ===== */
    .stCheckbox > label {
        color: var(--text) !important;
    }

    .stCheckbox p, .stCheckbox span {
        color: var(--text) !important;
    }

    /* ===== SLIDERY ===== */
    .stSlider > label {
        color: var(--text) !important;
    }

    .stSlider p {
        color: var(--text) !important;
    }

    .stSlider [data-baseweb="slider"] div {
        color: var(--text) !important;
    }

    /* Slider track i wartości */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: var(--text-secondary) !important;
    }

    /* ===== LABELS OGÓLNE ===== */
    .stSelectbox > label,
    .stMultiSelect > label,
    .stTextInput > label,
    .stTextArea > label,
    .stNumberInput > label {
        color: var(--text) !important;
        font-weight: 500;
    }

    /* ===== CAPTION I HELPER TEXT ===== */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--text-secondary) !important;
    }

    /* ===== MARKDOWN TEKST ===== */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: var(--text);
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: var(--text);
    }

    /* ===== INFO/SUCCESS/ERROR BOXES ===== */
    .stAlert p {
        color: inherit;
    }

    /* ===== RESPONSYWNOŚĆ - TABLET ===== */
    @media (max-width: 768px) {
        .stats-row {
            flex-wrap: wrap;
            gap: 0.75rem;
        }

        .stat-item {
            flex: 1 1 45%;
        }

        .app-title {
            font-size: 1.5rem;
        }

        .section-title {
            font-size: 0.95rem;
        }
    }

    /* ===== RESPONSYWNOŚĆ - MOBILE (iPhone 12/13 Mini: 375px) ===== */
    @media (max-width: 480px) {
        /* Główny kontener */
        .block-container {
            padding: 1rem 0.75rem !important;
        }

        /* Nagłówek */
        .app-header {
            padding: 1rem 0 0.75rem;
            margin-bottom: 1rem;
        }

        .app-title {
            font-size: 1.25rem;
            line-height: 1.3;
        }

        .app-subtitle {
            font-size: 0.85rem;
        }

        /* Statystyki */
        .stats-row {
            flex-direction: row;
            flex-wrap: wrap;
            gap: 0.5rem;
            padding: 0.75rem 0;
            margin-bottom: 1rem;
        }

        .stat-item {
            flex: 1 1 45%;
            min-width: 0;
        }

        .stat-number {
            font-size: 1.25rem;
        }

        .stat-label {
            font-size: 0.75rem;
        }

        /* Taby */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: nowrap;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
            gap: 0;
        }

        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.75rem;
            font-size: 0.8rem;
            white-space: nowrap;
            flex-shrink: 0;
        }

        /* Sidebar na mobile */
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }

        section[data-testid="stSidebar"] > div {
            padding: 1rem 0.75rem;
        }

        .sidebar-title {
            font-size: 0.7rem;
            margin: 1rem 0 0.5rem;
        }

        /* Sekcje */
        .section-title {
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }

        /* Expandery/Lista miejsc */
        details {
            margin-bottom: 0.5rem;
        }

        details summary {
            padding: 0.625rem 0.75rem;
            font-size: 0.85rem;
        }

        details[open] > div {
            padding: 0 0.75rem 0.75rem;
            font-size: 0.85rem;
        }

        /* Karty miejsc */
        .place-card {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .place-name {
            font-size: 0.9rem;
        }

        .place-location {
            font-size: 0.75rem;
        }

        .place-meta {
            font-size: 0.75rem;
            gap: 0.5rem;
        }

        /* Formularze */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            font-size: 16px !important; /* Zapobiega zoom na iOS */
            padding: 0.625rem !important;
        }

        .stSelectbox [data-baseweb="select"] > div,
        .stMultiSelect [data-baseweb="select"] > div {
            min-height: 42px;
        }

        /* Przyciski */
        .stButton > button {
            padding: 0.625rem 1rem;
            font-size: 0.85rem;
            min-height: 44px; /* Apple HIG minimum touch target */
        }

        /* Metryki */
        [data-testid="stMetric"] {
            padding: 0.625rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.1rem;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.7rem;
        }

        /* Slidery */
        .stSlider {
            padding: 0 0.25rem;
        }

        .stSlider p {
            font-size: 0.85rem !important;
        }

        /* Checkboxy i Radio */
        .stCheckbox, .stRadio {
            font-size: 0.85rem;
        }

        .stRadio > div {
            flex-direction: column !important;
            gap: 0.5rem;
        }

        /* Alerty/Info */
        [data-testid="stAlert"] {
            padding: 0.75rem !important;
            font-size: 0.85rem;
        }

        /* Caption */
        [data-testid="stCaptionContainer"] p {
            font-size: 0.75rem !important;
        }

        /* Mapa - zwiększona wysokość na mobile */
        iframe,
        [data-testid="stCustomComponentV1"] iframe {
            min-height: 400px !important;
            height: 400px !important;
        }

        /* Kolumny - stack na mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        /* Legenda */
        .legend-item {
            padding: 0.2rem 0;
            font-size: 0.75rem;
        }

        .legend-dot {
            width: 8px;
            height: 8px;
        }

        /* Footer */
        .stCaption {
            font-size: 0.75rem !important;
            text-align: center;
        }
    }

    /* ===== BARDZO MAŁE EKRANY (iPhone SE: 320px) ===== */
    @media (max-width: 360px) {
        .block-container {
            padding: 0.75rem 0.5rem !important;
        }

        .app-title {
            font-size: 1.1rem;
        }

        .stat-number {
            font-size: 1.1rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0.4rem 0.5rem;
            font-size: 0.75rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1rem;
        }
    }

    /* ===== TOUCH-FRIENDLY ===== */
    @media (hover: none) and (pointer: coarse) {
        /* Większe dotykowe cele */
        .stButton > button,
        .stCheckbox label,
        details summary {
            min-height: 44px;
        }

        /* Usunięcie efektów hover */
        .stButton > button:hover,
        details summary:hover,
        .place-card:hover {
            transform: none;
        }
    }

    /* ===== DODATKOWE MOBILNE STYLE ===== */

    /* Smooth scrolling dla całej strony */
    html {
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
    }

    /* Lepsza widoczność aktywnych elementów */
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 2px solid var(--primary);
        outline-offset: 2px;
    }

    /* Optymalizacja obrazów i iframe */
    img, iframe {
        max-width: 100%;
        height: auto;
    }

    /* Zapobieganie poziomemu scrollowi */
    .main .block-container {
        overflow-x: hidden;
    }

    /* Propozycje wycieczek - mobile */
    @media (max-width: 480px) {
        /* Taby propozycji - poziomy scroll */
        .stTabs [role="tablist"] {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            padding-bottom: 2px;
        }

        /* Metryki w jednej linii na mobile */
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            min-width: 0 !important;
        }

        /* Mniejsze metryki */
        [data-testid="stMetric"] {
            text-align: center;
        }

        /* Form na pełną szerokość */
        .stForm {
            padding: 0 !important;
        }

        /* Divider */
        hr {
            margin: 1rem 0 !important;
        }

        /* Info/caption tekst */
        .stMarkdown h4 {
            font-size: 1rem !important;
            margin-top: 1rem !important;
        }

        /* Radio buttons w kolumnie */
        .stRadio [role="radiogroup"] {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }

        /* Multiselect tagi */
        [data-baseweb="tag"] {
            font-size: 0.75rem !important;
            padding: 0.25rem 0.5rem !important;
        }
    }

    /* Landscape na telefonie */
    @media (max-height: 500px) and (orientation: landscape) {
        .app-header {
            padding: 0.5rem 0;
            margin-bottom: 0.5rem;
        }

        .stats-row {
            padding: 0.5rem 0;
            margin-bottom: 0.5rem;
        }
    }

</style>
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

# ============================================
# SESSION STATE
# ============================================
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0
if 'trip_proposals' not in st.session_state:
    st.session_state.trip_proposals = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

def trigger_refresh():
    st.session_state.refresh_trigger += 1

# ============================================
# FUNKCJE POMOCNICZE
# ============================================

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

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def estimate_travel_time(distance_km: float, speed_kmh: float = 50) -> float:
    return distance_km / speed_kmh

def optimize_route_nearest_neighbor(places: List[Dict], start_lat: float, start_lon: float) -> List[Dict]:
    if not places:
        return []
    remaining = places.copy()
    optimized = []
    current_lat, current_lon = start_lat, start_lon
    while remaining:
        nearest = min(remaining, key=lambda p: haversine_distance(current_lat, current_lon, p['latitude'], p['longitude']))
        optimized.append(nearest)
        remaining.remove(nearest)
        current_lat, current_lon = nearest['latitude'], nearest['longitude']
    return optimized

def generate_smart_trip(all_places: List[Dict], categories: List[str] = None,
                       max_places: int = 5, max_hours: float = 8.0,
                       prefer_unvisited: bool = True, variant: int = 0) -> Tuple[List[Dict], Dict]:
    """Generuje wycieczkę. variant=0-4 różne zakresy odległości"""
    candidates = all_places.copy()
    if prefer_unvisited:
        unvisited = [p for p in candidates if not p['is_visited']]
        if len(unvisited) >= max_places:
            candidates = unvisited
    if categories:
        candidates = [p for p in candidates if any(cat in p['category'] for cat in categories)]
    if not candidates:
        return [], {}

    candidates_with_dist = [(p, haversine_distance(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'],
                                                    p['latitude'], p['longitude'])) for p in candidates]
    candidates_with_dist.sort(key=lambda x: x[1])

    # Różne warianty - różne zakresy odległości (5 wariantów)
    n = len(candidates_with_dist)
    if variant == 0:  # Najbliższe miejsca
        pass  # już posortowane od najbliższych
    elif variant == 1:  # Blisko-średnie
        quarter = n // 4
        candidates_with_dist = candidates_with_dist[quarter:quarter*2] + candidates_with_dist[:quarter]
    elif variant == 2:  # Średnie odległości
        mid = n // 3
        candidates_with_dist = candidates_with_dist[mid:mid*2] + candidates_with_dist[:mid]
    elif variant == 3:  # Średnio-daleko
        quarter = n // 4
        candidates_with_dist = candidates_with_dist[quarter*2:quarter*3] + candidates_with_dist[quarter:quarter*2]
    elif variant == 4:  # Dalsze miejsca
        candidates_with_dist = candidates_with_dist[::-1]

    selected = []
    selected_categories = set()
    total_time = 0.0

    for place, dist in candidates_with_dist:
        if len(selected) >= max_places:
            break
        place_time = parse_time_for_display(place['time_needed'])
        travel_time = estimate_travel_time(dist)
        if total_time + place_time + travel_time > max_hours and selected:
            continue
        place_cat = place['category'].split('/')[0]
        if place_cat not in selected_categories or len(selected) < 2:
            selected.append(place)
            selected_categories.add(place_cat)
            total_time += place_time

    if selected:
        selected = optimize_route_nearest_neighbor(selected, HOME_LOCATION['latitude'], HOME_LOCATION['longitude'])

    return selected, calculate_trip_stats_detailed(selected)

def calculate_trip_stats_detailed(places: List[Dict]) -> Dict:
    """Oblicza szczegółowe statystyki trasy z czasami dojazdu między punktami"""
    if not places:
        return {'total_time': 0, 'total_distance': 0, 'visit_time': 0, 'travel_time': 0,
                'place_count': 0, 'segments': []}

    visit_time = sum(parse_time_for_display(p['time_needed']) for p in places)
    total_distance = 0.0
    segments = []  # Lista odcinków z czasami

    # Od domu do pierwszego punktu
    prev_lat, prev_lon = HOME_LOCATION['latitude'], HOME_LOCATION['longitude']
    prev_name = "Dom"

    for place in places:
        dist = haversine_distance(prev_lat, prev_lon, place['latitude'], place['longitude'])
        travel = estimate_travel_time(dist)
        segments.append({
            'from': prev_name,
            'to': place['name'],
            'distance': dist,
            'travel_time': travel
        })
        total_distance += dist
        prev_lat, prev_lon = place['latitude'], place['longitude']
        prev_name = place['name']

    # Powrót do domu
    dist_home = haversine_distance(prev_lat, prev_lon, HOME_LOCATION['latitude'], HOME_LOCATION['longitude'])
    travel_home = estimate_travel_time(dist_home)
    segments.append({
        'from': prev_name,
        'to': "Dom",
        'distance': dist_home,
        'travel_time': travel_home
    })
    total_distance += dist_home

    travel_time = sum(s['travel_time'] for s in segments)

    return {
        'total_time': visit_time + travel_time,
        'visit_time': visit_time,
        'travel_time': travel_time,
        'total_distance': total_distance,
        'place_count': len(places),
        'segments': segments
    }

def calculate_trip_stats(places: List[Dict]) -> Dict:
    """Wersja podstawowa dla kompatybilności"""
    stats = calculate_trip_stats_detailed(places)
    return {k: v for k, v in stats.items() if k != 'segments'}


def find_best_gallery_for_trip(trip_places: List[Dict], all_galleries: List[Dict],
                                max_detour_km: float = 15.0, gallery_types: List[str] = None) -> Optional[Dict]:
    """
    Znajduje najlepszą galerię handlową dla danej trasy wycieczki.
    Wybiera galerię która:
    1. Jest blisko trasy (minimalne odchylenie)
    2. Pasuje do preferencji typu galerii
    3. Jest w optymalnym miejscu na trasie (środek lub koniec)

    Args:
        trip_places: Lista miejsc w wycieczce
        all_galleries: Lista wszystkich galerii
        max_detour_km: Maksymalny dodatkowy dystans (km)
        gallery_types: Preferowane typy galerii

    Returns:
        Najlepsza galeria lub None
    """
    if not trip_places or not all_galleries:
        return None

    # Oblicz środek ciężkości trasy (centroid)
    route_points = [(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'])]
    for place in trip_places:
        route_points.append((place['latitude'], place['longitude']))
    route_points.append((HOME_LOCATION['latitude'], HOME_LOCATION['longitude']))  # Powrót

    # Centroid trasy
    centroid_lat = sum(p[0] for p in route_points) / len(route_points)
    centroid_lon = sum(p[1] for p in route_points) / len(route_points)

    # Oblicz "bounding box" trasy
    min_lat = min(p[0] for p in route_points)
    max_lat = max(p[0] for p in route_points)
    min_lon = min(p[1] for p in route_points)
    max_lon = max(p[1] for p in route_points)

    # Filtruj galerie według typu jeśli podano
    candidates = all_galleries
    if gallery_types:
        candidates = [g for g in all_galleries if g['gallery_type'] in gallery_types]

    if not candidates:
        candidates = all_galleries  # Fallback do wszystkich

    # Oceń każdą galerię
    scored_galleries = []
    for gallery in candidates:
        g_lat, g_lon = gallery['latitude'], gallery['longitude']

        # Sprawdź czy galeria jest w rozsądnym zakresie od trasy
        # (w bounding box + margines)
        margin = 0.2  # ~20km margines
        if not (min_lat - margin <= g_lat <= max_lat + margin and
                min_lon - margin <= g_lon <= max_lon + margin):
            continue

        # Oblicz odległość od centroidu trasy
        dist_from_centroid = haversine_distance(centroid_lat, centroid_lon, g_lat, g_lon)

        # Oblicz minimalny detour - odległość do najbliższego punktu na trasie
        min_detour = float('inf')
        best_insert_index = 0

        for i, (lat, lon) in enumerate(route_points[:-1]):
            next_lat, next_lon = route_points[i + 1]

            # Odległość do tego odcinka (uproszczona - do punktów)
            dist_to_current = haversine_distance(lat, lon, g_lat, g_lon)
            dist_to_next = haversine_distance(next_lat, next_lon, g_lat, g_lon)

            # Aktualny dystans odcinka
            original_dist = haversine_distance(lat, lon, next_lat, next_lon)

            # Nowy dystans przez galerię
            new_dist = dist_to_current + dist_to_next

            # Dodatkowy dystans (detour)
            detour = new_dist - original_dist

            if detour < min_detour:
                min_detour = detour
                best_insert_index = i + 1

        # Odrzuć jeśli detour za duży
        if min_detour > max_detour_km:
            continue

        # Scoring: mniejszy detour = lepiej, bonus za większe galerie
        gallery_size_bonus = 0
        if 'Mega' in gallery.get('gallery_type', '') or 'Hyper' in gallery.get('gallery_type', ''):
            gallery_size_bonus = -2  # Bonus (ujemny bo sortujemy rosnąco)
        elif 'Outlet' in gallery.get('gallery_type', ''):
            gallery_size_bonus = -1

        score = min_detour + gallery_size_bonus

        scored_galleries.append({
            'gallery': gallery,
            'score': score,
            'detour_km': min_detour,
            'insert_index': best_insert_index,
            'dist_from_centroid': dist_from_centroid
        })

    if not scored_galleries:
        return None

    # Wybierz najlepszą
    scored_galleries.sort(key=lambda x: x['score'])
    best = scored_galleries[0]

    # Dodaj metadane do galerii
    result = best['gallery'].copy()
    result['_detour_km'] = best['detour_km']
    result['_insert_index'] = best['insert_index']
    result['_is_gallery'] = True

    return result


def insert_gallery_into_trip(trip_places: List[Dict], gallery: Dict) -> List[Dict]:
    """
    Wstawia galerię w optymalne miejsce na trasie

    Args:
        trip_places: Lista miejsc
        gallery: Galeria do wstawienia

    Returns:
        Nowa lista z galerią
    """
    if not gallery:
        return trip_places

    insert_idx = gallery.get('_insert_index', len(trip_places))

    # Konwertuj galerię na format miejsca
    gallery_as_place = {
        'id': f"gallery_{gallery['id']}",
        'name': f"🛒 {gallery['name']}",
        'category': 'Zakupy',
        'location': gallery['location'],
        'latitude': gallery['latitude'],
        'longitude': gallery['longitude'],
        'time_needed': gallery['time_needed'],
        'description': gallery['description'],
        'season_hours': gallery['opening_hours'],
        'is_visited': False,
        '_is_gallery': True,
        '_gallery_type': gallery['gallery_type'],
        '_detour_km': gallery.get('_detour_km', 0)
    }

    # Wstaw w odpowiednie miejsce
    result = trip_places.copy()
    insert_idx = min(insert_idx, len(result))
    result.insert(insert_idx, gallery_as_place)

    return result

def parse_time_for_display(time_str: str) -> float:
    if not time_str:
        return 1.0
    import re
    time_str = time_str.lower().strip()
    if '-' in time_str:
        parts = time_str.split('-')
        if len(parts) == 2:
            time_str = parts[1].strip()
    try:
        if 'dni' in time_str or 'd' in time_str:
            return float(re.findall(r'[\d.]+', time_str)[0]) * 8.0
        elif 'h' in time_str:
            return float(re.findall(r'[\d.]+', time_str)[0])
        elif 'min' in time_str:
            return float(re.findall(r'[\d.]+', time_str)[0]) / 60.0
        else:
            return float(re.findall(r'[\d.]+', time_str)[0])
    except:
        return 1.0

def get_category_color(category: str) -> str:
    main_cat = category.split('/')[0]
    return CATEGORY_COLORS.get(main_cat, "#6b7280")

def create_map(places: List[Dict], show_home: bool = True, show_route: bool = False,
               center_lat: float = 50.9, center_lon: float = 16.5, zoom: int = 9,
               galleries: List[Dict] = None) -> folium.Map:
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles='cartodbpositron',
                   width='100%', height='500px')

    if show_home:
        folium.Marker(
            location=[HOME_LOCATION['latitude'], HOME_LOCATION['longitude']],
            popup=folium.Popup(f"""
                <div style="font-family: 'Inter', sans-serif; padding: 10px; min-width: 200px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b;">Punkt startowy</h4>
                    <p style="margin: 0; color: #64748b;">{HOME_LOCATION['address']}</p>
                </div>
            """, max_width=250),
            tooltip="Punkt startowy",
            icon=folium.Icon(color='darkred', icon='home', prefix='fa')
        ).add_to(m)

    route_coords = [(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'])] if show_route else []

    for i, place in enumerate(places):
        is_gallery = place.get('_is_gallery', False)

        if is_gallery:
            # Marker dla galerii handlowej
            color = 'pink'
            icon_name = 'shopping-cart'
            category_display = place.get('_gallery_type', 'Galeria')
            category_color = '#ec4899'  # Pink for shopping
        else:
            color = 'gray' if place['is_visited'] else get_category_color(place['category']).replace('#', '')
            icon_name = 'check' if place['is_visited'] else 'map-marker'
            category_display = place['category']
            category_color = get_category_color(place['category'])

        number_html = f"<span style='background: #6366f1; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 600; margin-right: 8px;'>{i+1}</span>" if show_route else ""

        popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; padding: 12px; min-width: 280px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                {number_html}
                <h4 style="margin: 0; color: #1e293b; font-size: 16px;">{place['name']}</h4>
            </div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">
                <span style="background: {category_color}20; color: {category_color}; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 500;">{category_display}</span>
                <span style="background: #f1f5f9; color: #64748b; padding: 4px 10px; border-radius: 20px; font-size: 12px;">{place['time_needed']}</span>
            </div>
            <p style="margin: 0 0 8px 0; color: #475569; font-size: 13px; line-height: 1.5;">{place['description']}</p>
            <p style="margin: 0; color: #94a3b8; font-size: 12px;">{place['location']} · {place['season_hours']}</p>
        </div>
        """

        # Wybierz kolor markera
        if is_gallery:
            marker_color = 'pink'
        elif place['is_visited']:
            marker_color = 'gray'
        elif 'Natura' in place.get('category', ''):
            marker_color = 'green'
        elif 'Przygoda' in place.get('category', ''):
            marker_color = 'orange'
        elif 'Historia' in place.get('category', ''):
            marker_color = 'purple'
        else:
            marker_color = 'blue'

        folium.Marker(
            location=[place['latitude'], place['longitude']],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"{i+1}. {place['name']}" if show_route else place['name'],
            icon=folium.Icon(color=marker_color, icon=icon_name, prefix='fa')
        ).add_to(m)

        if show_route:
            route_coords.append((place['latitude'], place['longitude']))

    # Dodaj markery galerii handlowych
    if galleries:
        for gallery in galleries:
            gallery_popup = f"""
            <div style="font-family: 'Inter', sans-serif; padding: 12px; min-width: 250px;">
                <h4 style="margin: 0 0 8px 0; color: #ec4899; font-size: 15px;">🛒 {gallery['name']}</h4>
                <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">
                    <span style="background: #fdf2f8; color: #be185d; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 500;">{gallery['gallery_type']}</span>
                    <span style="background: #f1f5f9; color: #64748b; padding: 4px 10px; border-radius: 20px; font-size: 12px;">{gallery['time_needed']}</span>
                </div>
                <p style="margin: 0 0 8px 0; color: #475569; font-size: 13px; line-height: 1.5;">{gallery['description']}</p>
                <p style="margin: 0; color: #94a3b8; font-size: 12px;">{gallery['location']} · {gallery['opening_hours']}</p>
            </div>
            """
            folium.Marker(
                location=[gallery['latitude'], gallery['longitude']],
                popup=folium.Popup(gallery_popup, max_width=300),
                tooltip=f"🛒 {gallery['name']}",
                icon=folium.Icon(color='pink', icon='shopping-cart', prefix='fa')
            ).add_to(m)

    if show_route and len(route_coords) > 1:
        route_coords.append((HOME_LOCATION['latitude'], HOME_LOCATION['longitude']))
        folium.PolyLine(route_coords, weight=3, color='#6366f1', opacity=0.8, dash_array='10').add_to(m)

    return m

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
stats = db.get_statistics()

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
tab1, tab2, tab3, tab4 = st.tabs([
    "Mapa",
    "Kreator wycieczek",
    "Nasze plany",
    "Dodaj miejsce"
])

# ============================================
# TAB 1: MAPA I ODKRYWANIE
# ============================================
with tab1:
    with st.sidebar:
        st.markdown('<p class="sidebar-title">Filtry</p>', unsafe_allow_html=True)

        categories = db.get_categories()
        vibes = db.get_vibes()

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

    _ = st.session_state.refresh_trigger
    places = db.get_places_by_filters(
        categories=selected_categories if selected_categories else None,
        vibes=selected_vibes if selected_vibes else None,
        hide_visited=hide_visited
    )

    st.markdown(f'<p class="section-title">Mapa ({len(places)} miejsc)</p>', unsafe_allow_html=True)

    # Mapa - pełna szerokość na górze
    if places:
        all_galleries = db.get_all_galleries()
        m = create_map(places, show_home=True, galleries=all_galleries)
        st_folium(m, height=500, use_container_width=True, key="main_map")
    else:
        st.info("Nie znaleziono miejsc. Zmień kryteria wyszukiwania.")

    # Lista miejsc - pod mapą
    st.markdown('<p class="section-title">Lista miejsc</p>', unsafe_allow_html=True)
    search_query = st.text_input("Szukaj", placeholder="Wpisz nazwę miejsca", label_visibility="collapsed")

    filtered_places = places
    if search_query:
        filtered_places = [p for p in places if search_query.lower() in p['name'].lower()]

    st.caption(f"Wyświetlono {len(filtered_places)} miejsc")

    # Lista w 4 kolumnach
    cols = st.columns(4)

    for i, place in enumerate(filtered_places):
        dist = haversine_distance(HOME_LOCATION['latitude'], HOME_LOCATION['longitude'],
                                 place['latitude'], place['longitude'])

        expander_label = f"{place['name']} {'(odwiedzone)' if place['is_visited'] else ''}"

        # Rozłożenie na 4 kolumny
        with cols[i % 4]:
            with st.expander(expander_label, expanded=False):
                st.markdown(f"**{place['category']}** · {place['location']} · {dist:.1f} km")
                st.markdown(place['description'])
                st.caption(f"Czas: {place['time_needed']} | {place['season_hours']}")

                # Pogoda w danym miejscu
                place_weather = get_weather(place['latitude'], place['longitude'])
                if place_weather:
                    st.caption(f"Pogoda: {place_weather['temp']}°C, {place_weather['description']}")

                if not place['is_visited']:
                    if st.button("Oznacz jako odwiedzone", key=f"v_{place['id']}", use_container_width=True):
                        db.mark_as_visited(place['id'])
                        trigger_refresh()
                        st.rerun()
                else:
                    if st.button("Cofnij odwiedzenie", key=f"u_{place['id']}", use_container_width=True):
                        db.mark_as_unvisited(place['id'])
                        trigger_refresh()
                        st.rerun()

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
            options=db.get_categories(),
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
            all_places = db.get_all_places()

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
                        max_places, max_hours, prefer_unvisited, variant=i
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
                st.success(f"Wygenerowano {len(proposals)} propozycji!")
            else:
                st.error("Nie znaleziono miejsc. Zmień preferencje.")

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
                                    st.success(f"Zapisano '{trip_name}'!")
                                    st.session_state.trip_proposals = []
                                    st.rerun()

    else:
        st.markdown("#### Ręczne planowanie")
        all_places = db.get_all_places()
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
                        st.success(f"Zapisano '{trip_name}'!")
                else:
                    st.error("Podaj nazwę i wybierz miejsca!")

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

    _ = st.session_state.refresh_trigger
    trips = db.get_all_trips()

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
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Zrealizowano", key=f"c_{trip['id']}", use_container_width=True, type="primary"):
                            db.complete_trip(trip['id'])
                            trigger_refresh()
                            st.rerun()
                    with c2:
                        if st.button("Usuń", key=f"d_{trip['id']}", use_container_width=True):
                            db.delete_trip(trip['id'])
                            trigger_refresh()
                            st.rerun()
        else:
            st.info("Brak aktywnych planów. Stwórz nową wycieczkę!")

        st.markdown("---")
        st.markdown("**Zrealizowane**")
        if completed:
            for trip in completed:
                with st.expander(f"{trip['name']} ({trip['place_count']} miejsc)"):
                    st.markdown(f"**Miejsca:** {trip['place_names']}")
                    if st.button("Usuń z historii", key=f"dc_{trip['id']}"):
                        db.delete_trip(trip['id'])
                        trigger_refresh()
                        st.rerun()
        else:
            st.info("Brak zrealizowanych wycieczek.")
    else:
        st.info("Brak planów. Przejdź do Kreatora wycieczek!")

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
                    st.success(f"Dodano '{new_name}'!")
                    trigger_refresh()
            else:
                st.error("Wypełnij wymagane pola!")

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
st.caption("Nasza Mapa Przygód · Wersja 4.1 · Punkt startowy: Jelenia Góra")