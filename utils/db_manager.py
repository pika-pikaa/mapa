"""
Database Manager - Kompletna warstwa danych dla aplikacji Nasza Mapa Przygód
Obsługa SQLite, import CSV, zarządzanie miejscami i wycieczkami
"""

import sqlite3
import pandas as pd
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re


class DatabaseManager:
    """Główny manager bazy danych SQLite"""

    def __init__(self, db_path: str = "data/places.db"):
        """
        Inicjalizacja połączenia z bazą danych

        Args:
            db_path: Ścieżka do pliku bazy danych SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.init_database()

    def connect(self):
        """Nawiązuje połączenie z bazą danych"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Błąd połączenia z bazą danych: {e}")
            raise

    def init_database(self):
        """Inicjalizuje strukturę bazy danych"""
        try:
            # Tabela miejsc
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS places (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lp INTEGER,
                    name TEXT NOT NULL,
                    category TEXT,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    vibe TEXT,
                    time_needed TEXT,
                    description TEXT,
                    season_hours TEXT,
                    is_visited BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabela wycieczek
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    total_time_hours REAL,
                    is_completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')

            # Tabela relacji wycieczka-miejsce
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS trip_places (
                    trip_id INTEGER,
                    place_id INTEGER,
                    order_index INTEGER,
                    FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE,
                    FOREIGN KEY (place_id) REFERENCES places (id) ON DELETE CASCADE,
                    PRIMARY KEY (trip_id, place_id)
                )
            ''')

            # Tabela galerii handlowych
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS galleries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lp INTEGER,
                    name TEXT NOT NULL,
                    gallery_type TEXT,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    vibe TEXT,
                    time_needed TEXT,
                    description TEXT,
                    opening_hours TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Indeksy dla wydajności
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_visited ON places(is_visited)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_category ON places(category)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_trips_completed ON trips(is_completed)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_galleries_type ON galleries(gallery_type)')

            self.conn.commit()
        except Exception as e:
            print(f"Błąd podczas tworzenia struktury bazy: {e}")
            raise

    def import_from_csv(self, csv_path: str = "data/baza-lokalizacji.csv") -> bool:
        """
        Importuje dane z pliku CSV do bazy danych

        Args:
            csv_path: Ścieżka do pliku CSV

        Returns:
            True jeśli import się powiódł, False w przeciwnym przypadku
        """
        try:
            # Sprawdź czy dane już istnieją
            self.cursor.execute("SELECT COUNT(*) FROM places")
            if self.cursor.fetchone()[0] > 0:
                print("Dane już istnieją w bazie. Pomijam import.")
                return True

            # Wczytaj dane z CSV
            df = pd.read_csv(csv_path)

            # Przetwórz każdy wiersz
            for _, row in df.iterrows():
                # Parsuj współrzędne GPS
                gps = row['GPS']
                latitude, longitude = self._parse_gps_coordinates(gps)

                # Wstaw dane do bazy
                self.cursor.execute('''
                    INSERT INTO places (
                        lp, name, category, location, latitude, longitude,
                        vibe, time_needed, description, season_hours, is_visited
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['LP'],
                    row['Nazwa'],
                    row['Kategoria'],
                    row['Lokalizacja'],
                    latitude,
                    longitude,
                    row['Vibe'],
                    row['Czas'],
                    row['Opis'],
                    row['Sezon/Godziny'],
                    False  # Domyślnie nieodwiedzone
                ))

            self.conn.commit()
            print(f"Zaimportowano {len(df)} miejsc do bazy danych.")
            return True

        except Exception as e:
            print(f"Błąd podczas importu CSV: {e}")
            self.conn.rollback()
            return False

    def _parse_gps_coordinates(self, gps_string: str) -> Tuple[float, float]:
        """
        Parsuje współrzędne GPS z formatu string

        Args:
            gps_string: String w formacie "lat, lon"

        Returns:
            Tuple (latitude, longitude) jako floats
        """
        try:
            # Usuń cudzysłowy i białe znaki
            gps_clean = gps_string.strip().strip('"').strip("'")
            # Rozdziel po przecinku
            parts = gps_clean.split(',')
            if len(parts) != 2:
                raise ValueError(f"Nieprawidłowy format GPS: {gps_string}")

            latitude = float(parts[0].strip())
            longitude = float(parts[1].strip())

            return latitude, longitude
        except Exception as e:
            print(f"Błąd parsowania GPS '{gps_string}': {e}")
            return 0.0, 0.0

    def get_all_places(self, include_visited: bool = True) -> List[Dict]:
        """
        Pobiera wszystkie miejsca z bazy

        Args:
            include_visited: Czy uwzględnić odwiedzone miejsca

        Returns:
            Lista słowników z danymi miejsc
        """
        try:
            if include_visited:
                query = "SELECT * FROM places ORDER BY lp"
            else:
                query = "SELECT * FROM places WHERE is_visited = 0 ORDER BY lp"

            self.cursor.execute(query)
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Błąd pobierania miejsc: {e}")
            return []

    def get_places_by_filters(self, categories: List[str] = None,
                            vibes: List[str] = None,
                            hide_visited: bool = False) -> List[Dict]:
        """
        Pobiera miejsca według filtrów

        Args:
            categories: Lista kategorii do filtrowania
            vibes: Lista vibe'ów (hashtagów) do filtrowania
            hide_visited: Czy ukryć odwiedzone miejsca

        Returns:
            Lista przefiltrowanych miejsc
        """
        try:
            query = "SELECT * FROM places WHERE 1=1"
            params = []

            # Filtr kategorii
            if categories and len(categories) > 0:
                category_conditions = []
                for cat in categories:
                    category_conditions.append("category LIKE ?")
                    params.append(f"%{cat}%")
                query += f" AND ({' OR '.join(category_conditions)})"

            # Filtr vibe'ów
            if vibes and len(vibes) > 0:
                vibe_conditions = []
                for vibe in vibes:
                    vibe_conditions.append("vibe LIKE ?")
                    params.append(f"%{vibe}%")
                query += f" AND ({' OR '.join(vibe_conditions)})"

            # Filtr odwiedzonych
            if hide_visited:
                query += " AND is_visited = 0"

            query += " ORDER BY lp"

            self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]

        except Exception as e:
            print(f"Błąd filtrowania miejsc: {e}")
            return []

    def mark_as_visited(self, place_id: int) -> bool:
        """
        Oznacza miejsce jako odwiedzone

        Args:
            place_id: ID miejsca do oznaczenia

        Returns:
            True jeśli operacja się powiodła
        """
        try:
            self.cursor.execute(
                "UPDATE places SET is_visited = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (place_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Błąd oznaczania miejsca jako odwiedzone: {e}")
            self.conn.rollback()
            return False

    def mark_as_unvisited(self, place_id: int) -> bool:
        """
        Oznacza miejsce jako nieodwiedzone

        Args:
            place_id: ID miejsca

        Returns:
            True jeśli operacja się powiodła
        """
        try:
            self.cursor.execute(
                "UPDATE places SET is_visited = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (place_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Błąd oznaczania miejsca jako nieodwiedzone: {e}")
            self.conn.rollback()
            return False

    def add_place(self, name: str, category: str, location: str,
                  latitude: float, longitude: float, vibe: str,
                  time_needed: str, description: str,
                  season_hours: str) -> Optional[int]:
        """
        Dodaje nowe miejsce do bazy

        Returns:
            ID nowego miejsca lub None w przypadku błędu
        """
        try:
            # Znajdź najwyższy LP
            self.cursor.execute("SELECT MAX(lp) FROM places")
            max_lp = self.cursor.fetchone()[0] or 0

            self.cursor.execute('''
                INSERT INTO places (
                    lp, name, category, location, latitude, longitude,
                    vibe, time_needed, description, season_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                max_lp + 1, name, category, location, latitude, longitude,
                vibe, time_needed, description, season_hours
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            print(f"Błąd dodawania miejsca: {e}")
            self.conn.rollback()
            return None

    def create_trip(self, name: str, place_ids: List[int],
                   description: str = "") -> Optional[int]:
        """
        Tworzy nową wycieczkę

        Args:
            name: Nazwa wycieczki
            place_ids: Lista ID miejsc w wycieczce
            description: Opis wycieczki

        Returns:
            ID nowej wycieczki lub None
        """
        try:
            # Oblicz całkowity czas
            total_time = self._calculate_total_time(place_ids)

            # Utwórz wycieczkę
            self.cursor.execute('''
                INSERT INTO trips (name, description, total_time_hours)
                VALUES (?, ?, ?)
            ''', (name, description, total_time))

            trip_id = self.cursor.lastrowid

            # Dodaj miejsca do wycieczki
            for index, place_id in enumerate(place_ids):
                self.cursor.execute('''
                    INSERT INTO trip_places (trip_id, place_id, order_index)
                    VALUES (?, ?, ?)
                ''', (trip_id, place_id, index))

            self.conn.commit()
            return trip_id

        except Exception as e:
            print(f"Błąd tworzenia wycieczki: {e}")
            self.conn.rollback()
            return None

    def _calculate_total_time(self, place_ids: List[int]) -> float:
        """
        Oblicza całkowity czas wycieczki

        Args:
            place_ids: Lista ID miejsc

        Returns:
            Całkowity czas w godzinach
        """
        try:
            if not place_ids:
                return 0.0

            placeholders = ','.join(['?' for _ in place_ids])
            self.cursor.execute(
                f"SELECT time_needed FROM places WHERE id IN ({placeholders})",
                place_ids
            )

            total = 0.0
            for row in self.cursor.fetchall():
                time_str = row[0]
                if time_str:
                    total += self._parse_time_string(time_str)

            return total

        except Exception as e:
            print(f"Błąd obliczania czasu: {e}")
            return 0.0

    def _parse_time_string(self, time_str: str) -> float:
        """
        Parsuje string z czasem na liczbę godzin

        Args:
            time_str: String typu "2-3h", "1.5h", "30min"

        Returns:
            Liczba godzin jako float
        """
        try:
            time_str = time_str.lower().strip()

            # Obsługa zakresów (np. "2-3h")
            if '-' in time_str:
                parts = time_str.split('-')
                if len(parts) == 2:
                    # Weź górną granicę
                    time_str = parts[1].strip()

            # Usuń jednostki i konwertuj
            if 'min' in time_str:
                minutes = float(re.findall(r'[\d.]+', time_str)[0])
                return minutes / 60.0
            elif 'h' in time_str or 'godz' in time_str:
                hours = float(re.findall(r'[\d.]+', time_str)[0])
                return hours
            elif 'd' in time_str:
                days = float(re.findall(r'[\d.]+', time_str)[0])
                return days * 8.0  # Zakładamy 8h zwiedzania dziennie
            else:
                # Spróbuj jako liczba godzin
                return float(re.findall(r'[\d.]+', time_str)[0])

        except Exception:
            return 1.0  # Domyślna wartość

    def get_all_trips(self) -> List[Dict]:
        """
        Pobiera wszystkie wycieczki

        Returns:
            Lista wycieczek ze szczegółami
        """
        try:
            self.cursor.execute('''
                SELECT t.*,
                    COUNT(tp.place_id) as place_count,
                    GROUP_CONCAT(p.name, ', ') as place_names
                FROM trips t
                LEFT JOIN trip_places tp ON t.id = tp.trip_id
                LEFT JOIN places p ON tp.place_id = p.id
                GROUP BY t.id
                ORDER BY t.created_at DESC
            ''')

            return [dict(row) for row in self.cursor.fetchall()]

        except Exception as e:
            print(f"Błąd pobierania wycieczek: {e}")
            return []

    def complete_trip(self, trip_id: int) -> bool:
        """
        Oznacza wycieczkę jako zrealizowaną i wszystkie jej miejsca jako odwiedzone

        Args:
            trip_id: ID wycieczki

        Returns:
            True jeśli operacja się powiodła
        """
        try:
            # Oznacz wycieczkę jako zrealizowaną
            self.cursor.execute('''
                UPDATE trips
                SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (trip_id,))

            # Oznacz wszystkie miejsca jako odwiedzone
            self.cursor.execute('''
                UPDATE places
                SET is_visited = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id IN (
                    SELECT place_id FROM trip_places WHERE trip_id = ?
                )
            ''', (trip_id,))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Błąd realizacji wycieczki: {e}")
            self.conn.rollback()
            return False

    def get_trip_details(self, trip_id: int) -> Optional[Dict]:
        """
        Pobiera szczegóły wycieczki wraz z miejscami

        Args:
            trip_id: ID wycieczki

        Returns:
            Słownik ze szczegółami wycieczki
        """
        try:
            # Pobierz dane wycieczki
            self.cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
            trip = dict(self.cursor.fetchone())

            # Pobierz miejsca
            self.cursor.execute('''
                SELECT p.*
                FROM places p
                JOIN trip_places tp ON p.id = tp.place_id
                WHERE tp.trip_id = ?
                ORDER BY tp.order_index
            ''', (trip_id,))

            trip['places'] = [dict(row) for row in self.cursor.fetchall()]

            return trip

        except Exception as e:
            print(f"Błąd pobierania szczegółów wycieczki: {e}")
            return None

    def delete_trip(self, trip_id: int) -> bool:
        """
        Usuwa wycieczkę

        Args:
            trip_id: ID wycieczki do usunięcia

        Returns:
            True jeśli operacja się powiodła
        """
        try:
            self.cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Błąd usuwania wycieczki: {e}")
            self.conn.rollback()
            return False

    def get_categories(self) -> List[str]:
        """
        Pobiera unikalne kategorie

        Returns:
            Lista unikalnych kategorii
        """
        try:
            self.cursor.execute("SELECT DISTINCT category FROM places WHERE category IS NOT NULL")
            categories = []
            for row in self.cursor.fetchall():
                # Rozdziel kategorie złożone
                cat_list = row[0].split('/')
                categories.extend([cat.strip() for cat in cat_list])

            return sorted(list(set(categories)))

        except Exception as e:
            print(f"Błąd pobierania kategorii: {e}")
            return []

    def get_vibes(self) -> List[str]:
        """
        Pobiera unikalne vibe'y (hashtagi)

        Returns:
            Lista unikalnych hashtagów
        """
        try:
            self.cursor.execute("SELECT DISTINCT vibe FROM places WHERE vibe IS NOT NULL")
            vibes = []
            for row in self.cursor.fetchall():
                # Wyodrębnij hashtagi
                vibe_list = re.findall(r'#\w+', row[0])
                vibes.extend(vibe_list)

            return sorted(list(set(vibes)))

        except Exception as e:
            print(f"Błąd pobierania vibe'ów: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        Pobiera statystyki aplikacji

        Returns:
            Słownik ze statystykami
        """
        try:
            stats = {}

            # Liczba miejsc
            self.cursor.execute("SELECT COUNT(*) FROM places")
            stats['total_places'] = self.cursor.fetchone()[0]

            # Liczba odwiedzonych
            self.cursor.execute("SELECT COUNT(*) FROM places WHERE is_visited = 1")
            stats['visited_places'] = self.cursor.fetchone()[0]

            # Liczba wycieczek
            self.cursor.execute("SELECT COUNT(*) FROM trips")
            stats['total_trips'] = self.cursor.fetchone()[0]

            # Liczba zrealizowanych wycieczek
            self.cursor.execute("SELECT COUNT(*) FROM trips WHERE is_completed = 1")
            stats['completed_trips'] = self.cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"Błąd pobierania statystyk: {e}")
            return {}

    def close(self):
        """Zamyka połączenie z bazą danych"""
        if self.conn:
            self.conn.close()

    # ============================================
    # METODY DLA GALERII HANDLOWYCH
    # ============================================

    def import_galleries_from_csv(self, csv_path: str = "data/baza-galerii.csv") -> bool:
        """
        Importuje galerie handlowe z pliku CSV

        Args:
            csv_path: Ścieżka do pliku CSV

        Returns:
            True jeśli import się powiódł
        """
        try:
            # Sprawdź czy dane już istnieją
            self.cursor.execute("SELECT COUNT(*) FROM galleries")
            if self.cursor.fetchone()[0] > 0:
                print("Galerie już istnieją w bazie. Pomijam import.")
                return True

            # Wczytaj dane z CSV
            df = pd.read_csv(csv_path)

            # Przetwórz każdy wiersz
            for _, row in df.iterrows():
                # Parsuj współrzędne GPS
                gps = row['GPS']
                latitude, longitude = self._parse_gps_coordinates(gps)

                # Wstaw dane do bazy
                self.cursor.execute('''
                    INSERT INTO galleries (
                        lp, name, gallery_type, location, latitude, longitude,
                        vibe, time_needed, description, opening_hours
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['LP'],
                    row['Nazwa'],
                    row['Typ Galerii'],
                    row['Lokalizacja'],
                    latitude,
                    longitude,
                    row['Vibe'],
                    row['Czas zwiedzania'],
                    row['Opis'],
                    row['Godziny otwarcia']
                ))

            self.conn.commit()
            print(f"Zaimportowano {len(df)} galerii do bazy danych.")
            return True

        except Exception as e:
            print(f"Błąd podczas importu galerii z CSV: {e}")
            self.conn.rollback()
            return False

    def get_all_galleries(self) -> List[Dict]:
        """
        Pobiera wszystkie galerie handlowe

        Returns:
            Lista słowników z danymi galerii
        """
        try:
            self.cursor.execute("SELECT * FROM galleries ORDER BY lp")
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Błąd pobierania galerii: {e}")
            return []

    def get_gallery_types(self) -> List[str]:
        """
        Pobiera unikalne typy galerii

        Returns:
            Lista typów galerii
        """
        try:
            self.cursor.execute("SELECT DISTINCT gallery_type FROM galleries WHERE gallery_type IS NOT NULL")
            return sorted([row[0] for row in self.cursor.fetchall()])
        except Exception as e:
            print(f"Błąd pobierania typów galerii: {e}")
            return []