# Nasza Mapa Przygód

## Opis projektu
Aplikacja webowa do eksploracji i planowania wycieczek do ciekawych miejsc na Dolnym Śląsku i okolicach. Projekt wykorzystuje interaktywną mapę do wizualizacji lokalizacji turystycznych, umożliwia filtrowanie według kategorii i planowanie tras.

## Funkcjonalności
- Interaktywna mapa z punktami POI (Points of Interest)
- Filtrowanie lokalizacji według kategorii (Natura, Przygoda, Historia, Nauka, etc.)
- Wyświetlanie szczegółów miejsca (opis, czas zwiedzania, godziny otwarcia)
- Planowanie tras między wybranymi punktami
- Wyszukiwanie miejsc po nazwie i opisie

## Technologie
- **Backend**: Python 3.11+
- **Framework**: Streamlit
- **Mapa**: Folium + Streamlit-Folium
- **Dane**: Pandas
- **Geokodowanie**: Geopy
- **Deployment**: Pyngrok (dla tunelu lokalnego)

## Struktura projektu
```
baza-lokalizacji/
│
├── data/                 # Dane aplikacji
│   └── baza-lokalizacji.csv
│
├── utils/               # Funkcje pomocnicze
│   └── db_manager.py   # Zarządzanie danymi
│
├── app.py              # Główna aplikacja Streamlit
├── requirements.txt    # Zależności Python
├── .gitignore         # Pliki ignorowane przez Git
├── README.md          # Ten plik
└── BACKLOG.md         # Plan rozwoju (SCRUM)
```

## Instalacja

1. Klonuj repozytorium:
```bash
git clone <repo-url>
cd baza-lokalizacji
```

2. Stwórz wirtualne środowisko:
```bash
python -m venv venv
```

3. Aktywuj wirtualne środowisko:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
streamlit run app.py
```

Aplikacja będzie dostępna pod adresem: http://localhost:8501

## Dane
Baza zawiera 49 lokalizacji turystycznych z następującymi informacjami:
- Nazwa miejsca
- Kategoria (typ atrakcji)
- Lokalizacja (miasto/miejscowość)
- Współrzędne GPS
- Charakterystyka miejsca (vibes/hashtagi)
- Sugerowany czas zwiedzania
- Krótki opis
- Informacje o dostępności czasowej

## Rozwój
Szczegółowy plan rozwoju aplikacji znajduje się w pliku [BACKLOG.md](BACKLOG.md).

## Licencja
Do określenia

## Autorzy
Zespół deweloperski projektu "Nasza Mapa Przygód"