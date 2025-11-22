# Product Backlog - Nasza Mapa Przygód

## Wizja Produktu
Aplikacja webowa umożliwiająca eksplorację i planowanie wycieczek do ciekawych miejsc na Dolnym Śląsku i okolicach. Użytkownicy mogą przeglądać lokalizacje na interaktywnej mapie, filtrować według kategorii, czytać opisy i planować trasy zwiedzania.

## Definition of Done (DoD)
- [ ] Kod jest napisany zgodnie z PEP 8
- [ ] Funkcjonalność działa bez błędów
- [ ] Interfejs jest responsywny i intuicyjny
- [ ] Kod jest skomentowany w kluczowych miejscach
- [ ] README jest zaktualizowane (jeśli potrzeba)
- [ ] Aplikacja uruchamia się lokalnie bez problemów

---

## SPRINT 1: Baza Danych i Zarządzanie Danymi (3 dni)
**Cel sprintu:** Stworzenie solidnej warstwy danych i logiki biznesowej

### User Stories:

#### 1.1 Jako deweloper, chcę mieć system zarządzania danymi
**Tasks:**
- [x] Utworzenie struktury projektu
- [x] Stworzenie klasy LocationManager w utils/db_manager.py
- [ ] Implementacja metod do ładowania danych z CSV
- [ ] Walidacja danych (współrzędne GPS, formaty)
- [ ] Testy jednostkowe dla LocationManager

**Acceptance Criteria:**
- Dane są wczytywane poprawnie z CSV
- Współrzędne GPS są parsowane do float
- Kategorie są wyodrębniane poprawnie
- Obsługa błędów przy brakującym pliku

#### 1.2 Jako użytkownik, chcę filtrować lokalizacje po kategoriach
**Tasks:**
- [ ] Implementacja metody filter_by_category()
- [ ] Obsługa wielu kategorii jednocześnie
- [ ] Parsowanie kategorii złożonych (np. "Natura/Relaks")

**Acceptance Criteria:**
- Możliwość wyboru wielu kategorii
- Poprawne filtrowanie dla kategorii złożonych
- Zwracanie pustego DataFrame gdy brak wyników

#### 1.3 Jako użytkownik, chcę wyszukiwać miejsca po nazwie
**Tasks:**
- [ ] Implementacja metody search_locations()
- [ ] Wyszukiwanie w nazwie, opisie i lokalizacji
- [ ] Wyszukiwanie case-insensitive

**Acceptance Criteria:**
- Wyszukiwanie działa dla częściowych dopasowań
- Ignorowanie wielkości liter
- Wyszukiwanie w wielu polach

#### 1.4 Jako deweloper, chcę mieć pomocnicze funkcje do przetwarzania danych
**Tasks:**
- [ ] Funkcja parse_gps_coordinates()
- [ ] Funkcja format_time_info()
- [ ] Funkcja extract_hashtags()
- [ ] Funkcja get_nearby_locations()

**Acceptance Criteria:**
- Poprawne parsowanie różnych formatów
- Obsługa błędnych danych
- Zwracanie sensownych wartości domyślnych

**Sprint Review:** Demonstracja działania warstwy danych w konsoli Python

---

## SPRINT 2: Interfejs i Mapa Interaktywna (4 dni)
**Cel sprintu:** Stworzenie funkcjonalnego interfejsu z mapą

### User Stories:

#### 2.1 Jako użytkownik, chcę widzieć wszystkie lokalizacje na mapie
**Tasks:**
- [ ] Integracja Folium ze Streamlit
- [ ] Wyświetlanie markerów dla wszystkich lokalizacji
- [ ] Centrowanie mapy na Dolnym Śląsku
- [ ] Różne ikony dla różnych kategorii

**Acceptance Criteria:**
- Mapa wyświetla się poprawnie
- Wszystkie 49 lokalizacji są widoczne
- Markery mają różne kolory/ikony według kategorii
- Mapa jest wycentrowana na regionie

#### 2.2 Jako użytkownik, chcę widzieć szczegóły po kliknięciu w marker
**Tasks:**
- [ ] Dodanie popup z informacjami
- [ ] Wyświetlanie: nazwa, opis, czas, godziny otwarcia
- [ ] Formatowanie popupów (HTML/CSS)
- [ ] Dodanie hashtagów z kolumny Vibe

**Acceptance Criteria:**
- Popup pojawia się po kliknięciu
- Informacje są czytelnie sformatowane
- Hashtagi są wyświetlane jako tagi
- Popupy działają na urządzeniach mobilnych

#### 2.3 Jako użytkownik, chcę panel boczny z filtrami
**Tasks:**
- [ ] Sidebar z checkboxami dla kategorii
- [ ] Pole wyszukiwania tekstowego
- [ ] Licznik wyświetlanych lokalizacji
- [ ] Przycisk "Wyczyść filtry"

**Acceptance Criteria:**
- Filtry działają natychmiastowo
- Można łączyć filtry (kategorie + wyszukiwanie)
- Licznik aktualizuje się dynamicznie
- Stan filtrów jest zachowany podczas sesji

#### 2.4 Jako użytkownik, chcę listę lokalizacji obok mapy
**Tasks:**
- [ ] Tabela/lista z lokalizacjami
- [ ] Sortowanie po nazwie, kategorii, czasie
- [ ] Synchronizacja z mapą (filtry działają na obie)
- [ ] Możliwość rozwinięcia szczegółów

**Acceptance Criteria:**
- Lista jest zsynchronizowana z mapą
- Sortowanie działa poprawnie
- Można rozwinąć szczegóły bez opuszczania strony
- Lista jest responsywna

**Sprint Review:** Demonstracja działającej mapy z filtrami

---

## SPRINT 3: Funkcje Zaawansowane i UX (3 dni)
**Cel sprintu:** Dodanie zaawansowanych funkcji i poprawa UX

### User Stories:

#### 3.1 Jako użytkownik, chcę planować trasę między punktami
**Tasks:**
- [ ] Możliwość zaznaczenia wielu punktów
- [ ] Dodanie punktów do "koszyka" trasy
- [ ] Zmiana kolejności punktów
- [ ] Eksport trasy (lista miejsc)

**Acceptance Criteria:**
- Można wybrać 2-10 punktów
- Kolejność można zmieniać drag&drop
- Eksport do formatu tekstowego
- Zachowanie trasy w sesji

#### 3.2 Jako użytkownik, chcę widzieć odległości i czasy
**Tasks:**
- [ ] Integracja z Geopy dla odległości
- [ ] Obliczanie przybliżonego czasu przejazdu
- [ ] Sumowanie czasów zwiedzania
- [ ] Wyświetlanie całkowitego czasu wycieczki

**Acceptance Criteria:**
- Odległości są realistyczne
- Czasy przejazdu uwzględniają typ drogi
- Suma czasów jest wyświetlana wyraźnie
- Możliwość wyboru środka transportu

#### 3.3 Jako użytkownik, chcę tryb ciemny
**Tasks:**
- [ ] Przycisk toggle dla trybu ciemnego
- [ ] Stylowanie CSS dla dark mode
- [ ] Zapisywanie preferencji w session state
- [ ] Dostosowanie mapy do trybu

**Acceptance Criteria:**
- Płynne przełączanie między trybami
- Wszystkie elementy są czytelne
- Preferencje są zapamiętane
- Mapa też zmienia styl

#### 3.4 Jako użytkownik, chcę udostępniać trasę
**Tasks:**
- [ ] Generowanie unikalnego linku do trasy
- [ ] Możliwość skopiowania linku
- [ ] Eksport do PDF (opcjonalnie)
- [ ] Integracja z mediami społecznościowymi

**Acceptance Criteria:**
- Link działa i odtwarza trasę
- Przycisk "Kopiuj link" działa
- Format eksportu jest czytelny
- Udostępnianie jest intuicyjne

#### 3.5 Jako użytkownik, chcę responsywny design
**Tasks:**
- [ ] Testowanie na różnych rozdzielczościach
- [ ] Dostosowanie layoutu dla mobile
- [ ] Optymalizacja mapy dla dotykowych ekranów
- [ ] Menu hamburger dla mobile

**Acceptance Criteria:**
- Aplikacja działa na telefonie
- Mapa jest użyteczna na małym ekranie
- Wszystkie funkcje są dostępne
- Czas ładowania < 3 sekundy

**Sprint Review:** Demonstracja pełnej aplikacji z wszystkimi funkcjami

---

## Backlog (Przyszłe funkcje)

### Priorytet Wysoki:
- [ ] Integracja z Google Maps dla nawigacji
- [ ] System ocen i recenzji użytkowników
- [ ] Zdjęcia lokalizacji (integracja z API)
- [ ] Zapisywanie ulubionych miejsc

### Priorytet Średni:
- [ ] Pogoda dla lokalizacji
- [ ] Kalendarz wydarzeń
- [ ] Sugestie tras na podstawie preferencji
- [ ] Tryb offline (PWA)

### Priorytet Niski:
- [ ] Gamifikacja (odznaki za odwiedzone miejsca)
- [ ] Forum/czat użytkowników
- [ ] Integracja z booking.com dla noclegów
- [ ] AR mode dla zwiedzania

---

## Metryki Sukcesu
- Czas ładowania aplikacji < 3s
- Wszystkie funkcje działają bez błędów
- Intuicyjny interfejs (test z 5 użytkownikami)
- Responsywność na wszystkich urządzeniach
- 100% lokalizacji poprawnie wyświetlonych na mapie

## Ryzyka
1. **Wydajność przy dużej liczbie markerów** - Mitygacja: Clustering markerów
2. **Dokładność współrzędnych GPS** - Mitygacja: Walidacja i korekta ręczna
3. **Kompatybilność przeglądarek** - Mitygacja: Testowanie na głównych przeglądarkach
4. **Limity API (Geopy)** - Mitygacja: Cache i optymalizacja zapytań

---

## Notatki
- Używamy Streamlit 1.40.2+ dla najnowszych funkcji
- Folium dla interaktywnych map
- Dane w formacie CSV dla prostoty
- Deploy początkowo lokalny, później możliwy Streamlit Cloud