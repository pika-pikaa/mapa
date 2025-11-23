"""
Database Manager - Kompletna warstwa danych dla aplikacji Nasza Mapa Przygód
Obsługa SQLite, import CSV, zarządzanie miejscami i wycieczkami
"""

import sqlite3
import pandas as pd
import os
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re


class DatabaseManager:
    """Główny manager bazy danych SQLite - thread-safe"""

    _lock = threading.Lock()

    def __init__(self, db_path: str = "data/places.db"):
        """
        Inicjalizacja połączenia z bazą danych

        Args:
            db_path: Ścieżka do pliku bazy danych SQLite
        """
        self.db_path = db_path
        self._ensure_data_dir()
        self.init_database()

    def _ensure_data_dir(self):
        """Upewnia się że katalog data istnieje"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else "data", exist_ok=True)

    def _get_connection(self):
        """Tworzy nowe połączenie dla każdego wątku"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Inicjalizuje strukturę bazy danych"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Tabela miejsc
                cursor.execute('''
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
                cursor.execute('''
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
                cursor.execute('''
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
                cursor.execute('''
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
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_visited ON places(is_visited)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_category ON places(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_trips_completed ON trips(is_completed)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_galleries_type ON galleries(gallery_type)')

                conn.commit()
            except Exception as e:
                print(f"Błąd podczas tworzenia struktury bazy: {e}")
                raise
            finally:
                conn.close()

    def import_from_csv(self, csv_path: str = "data/baza-lokalizacji.csv") -> bool:
        """
        Importuje dane z pliku CSV do bazy danych
        """
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Sprawdź czy dane już istnieją
                cursor.execute("SELECT COUNT(*) FROM places")
                if cursor.fetchone()[0] > 0:
                    return True

                # Wczytaj dane z CSV
                df = pd.read_csv(csv_path)

                # Przetwórz każdy wiersz
                for _, row in df.iterrows():
                    gps = row['GPS']
                    latitude, longitude = self._parse_gps_coordinates(gps)

                    cursor.execute('''
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
                        False
                    ))

                conn.commit()
                print(f"Zaimportowano {len(df)} miejsc do bazy danych.")
                return True

            except Exception as e:
                print(f"Błąd podczas importu CSV: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

    def _parse_gps_coordinates(self, gps_string: str) -> Tuple[float, float]:
        """Parsuje współrzędne GPS z formatu string"""
        try:
            gps_clean = gps_string.strip().strip('"').strip("'")
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
        """Pobiera wszystkie miejsca z bazy"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if include_visited:
                    query = "SELECT * FROM places ORDER BY lp"
                else:
                    query = "SELECT * FROM places WHERE is_visited = 0 ORDER BY lp"

                cursor.execute(query)
                results = []
                for row in cursor.fetchall():
                    d = dict(row)
                    d['is_visited'] = bool(d.get('is_visited', 0))
                    results.append(d)
                return results
            except Exception as e:
                print(f"Błąd pobierania miejsc: {e}")
                return []
            finally:
                conn.close()

    def get_places_by_filters(self, categories: List[str] = None,
                            vibes: List[str] = None,
                            hide_visited: bool = False) -> List[Dict]:
        """Pobiera miejsca według filtrów"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                query = "SELECT * FROM places WHERE 1=1"
                params = []

                if categories and len(categories) > 0:
                    category_conditions = []
                    for cat in categories:
                        category_conditions.append("category LIKE ?")
                        params.append(f"%{cat}%")
                    query += f" AND ({' OR '.join(category_conditions)})"

                if vibes and len(vibes) > 0:
                    vibe_conditions = []
                    for vibe in vibes:
                        vibe_conditions.append("vibe LIKE ?")
                        params.append(f"%{vibe}%")
                    query += f" AND ({' OR '.join(vibe_conditions)})"

                if hide_visited:
                    query += " AND is_visited = 0"

                query += " ORDER BY lp"

                cursor.execute(query, params)
                results = []
                for row in cursor.fetchall():
                    d = dict(row)
                    d['is_visited'] = bool(d.get('is_visited', 0))
                    results.append(d)
                return results

            except Exception as e:
                print(f"Błąd filtrowania miejsc: {e}")
                return []
            finally:
                conn.close()

    def mark_as_visited(self, place_id: int) -> bool:
        """Oznacza miejsce jako odwiedzone"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE places SET is_visited = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (place_id,)
                )
                conn.commit()
                return True
            except Exception as e:
                print(f"Błąd oznaczania miejsca jako odwiedzone: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

    def mark_as_unvisited(self, place_id: int) -> bool:
        """Oznacza miejsce jako nieodwiedzone"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE places SET is_visited = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (place_id,)
                )
                conn.commit()
                return True
            except Exception as e:
                print(f"Błąd oznaczania miejsca jako nieodwiedzone: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

    def add_place(self, name: str, category: str, location: str,
                  latitude: float, longitude: float, vibe: str,
                  time_needed: str, description: str,
                  season_hours: str) -> Optional[int]:
        """Dodaje nowe miejsce do bazy"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(lp) FROM places")
                max_lp = cursor.fetchone()[0] or 0

                cursor.execute('''
                    INSERT INTO places (
                        lp, name, category, location, latitude, longitude,
                        vibe, time_needed, description, season_hours
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    max_lp + 1, name, category, location, latitude, longitude,
                    vibe, time_needed, description, season_hours
                ))

                conn.commit()
                return cursor.lastrowid

            except Exception as e:
                print(f"Błąd dodawania miejsca: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()

    def create_trip(self, name: str, place_ids: List[int],
                   description: str = "") -> Optional[int]:
        """Tworzy nową wycieczkę"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                total_time = self._calculate_total_time_internal(cursor, place_ids)

                cursor.execute('''
                    INSERT INTO trips (name, description, total_time_hours)
                    VALUES (?, ?, ?)
                ''', (name, description, total_time))

                trip_id = cursor.lastrowid

                for index, place_id in enumerate(place_ids):
                    cursor.execute('''
                        INSERT INTO trip_places (trip_id, place_id, order_index)
                        VALUES (?, ?, ?)
                    ''', (trip_id, place_id, index))

                conn.commit()
                return trip_id

            except Exception as e:
                print(f"Błąd tworzenia wycieczki: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()

    def _calculate_total_time_internal(self, cursor, place_ids: List[int]) -> float:
        """Oblicza całkowity czas wycieczki (wewnętrzna metoda)"""
        try:
            if not place_ids:
                return 0.0

            placeholders = ','.join(['?' for _ in place_ids])
            cursor.execute(
                f"SELECT time_needed FROM places WHERE id IN ({placeholders})",
                place_ids
            )

            total = 0.0
            for row in cursor.fetchall():
                time_str = row[0]
                if time_str:
                    total += self._parse_time_string(time_str)

            return total

        except Exception as e:
            print(f"Błąd obliczania czasu: {e}")
            return 0.0

    def _parse_time_string(self, time_str: str) -> float:
        """Parsuje string z czasem na liczbę godzin"""
        try:
            time_str = time_str.lower().strip()

            if '-' in time_str:
                parts = time_str.split('-')
                if len(parts) == 2:
                    time_str = parts[1].strip()

            if 'min' in time_str:
                minutes = float(re.findall(r'[\d.]+', time_str)[0])
                return minutes / 60.0
            elif 'h' in time_str or 'godz' in time_str:
                hours = float(re.findall(r'[\d.]+', time_str)[0])
                return hours
            elif 'd' in time_str:
                days = float(re.findall(r'[\d.]+', time_str)[0])
                return days * 8.0
            else:
                return float(re.findall(r'[\d.]+', time_str)[0])

        except Exception:
            return 1.0

    def get_all_trips(self) -> List[Dict]:
        """Pobiera wszystkie wycieczki"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.*,
                        COUNT(tp.place_id) as place_count,
                        GROUP_CONCAT(p.name, ', ') as place_names
                    FROM trips t
                    LEFT JOIN trip_places tp ON t.id = tp.trip_id
                    LEFT JOIN places p ON tp.place_id = p.id
                    GROUP BY t.id
                    ORDER BY t.created_at DESC
                ''')

                return [dict(row) for row in cursor.fetchall()]

            except Exception as e:
                print(f"Błąd pobierania wycieczek: {e}")
                return []
            finally:
                conn.close()

    def complete_trip(self, trip_id: int) -> bool:
        """Oznacza wycieczkę jako zrealizowaną"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE trips
                    SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (trip_id,))

                cursor.execute('''
                    UPDATE places
                    SET is_visited = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id IN (
                        SELECT place_id FROM trip_places WHERE trip_id = ?
                    )
                ''', (trip_id,))

                conn.commit()
                return True

            except Exception as e:
                print(f"Błąd realizacji wycieczki: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

    def get_trip_details(self, trip_id: int) -> Optional[Dict]:
        """Pobiera szczegóły wycieczki"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                trip = dict(row)

                cursor.execute('''
                    SELECT p.*
                    FROM places p
                    JOIN trip_places tp ON p.id = tp.place_id
                    WHERE tp.trip_id = ?
                    ORDER BY tp.order_index
                ''', (trip_id,))

                trip['places'] = [dict(row) for row in cursor.fetchall()]
                return trip

            except Exception as e:
                print(f"Błąd pobierania szczegółów wycieczki: {e}")
                return None
            finally:
                conn.close()

    def delete_trip(self, trip_id: int) -> bool:
        """Usuwa wycieczkę"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trip_places WHERE trip_id = ?", (trip_id,))
                cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Błąd usuwania wycieczki: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

    def get_categories(self) -> List[str]:
        """Pobiera unikalne kategorie"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM places WHERE category IS NOT NULL")
                categories = []
                for row in cursor.fetchall():
                    cat_list = row[0].split('/')
                    categories.extend([cat.strip() for cat in cat_list])

                return sorted(list(set(categories)))

            except Exception as e:
                print(f"Błąd pobierania kategorii: {e}")
                return []
            finally:
                conn.close()

    def get_vibes(self) -> List[str]:
        """Pobiera unikalne vibe'y (hashtagi)"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT vibe FROM places WHERE vibe IS NOT NULL")
                vibes = []
                for row in cursor.fetchall():
                    vibe_list = re.findall(r'#\w+', row[0])
                    vibes.extend(vibe_list)

                return sorted(list(set(vibes)))

            except Exception as e:
                print(f"Błąd pobierania vibe'ów: {e}")
                return []
            finally:
                conn.close()

    def get_statistics(self) -> Dict:
        """Pobiera statystyki aplikacji"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                stats = {}

                cursor.execute("SELECT COUNT(*) FROM places")
                stats['total_places'] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM places WHERE is_visited = 1")
                stats['visited_places'] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM trips")
                stats['total_trips'] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM trips WHERE is_completed = 1")
                stats['completed_trips'] = cursor.fetchone()[0]

                return stats

            except Exception as e:
                print(f"Błąd pobierania statystyk: {e}")
                return {'total_places': 0, 'visited_places': 0, 'total_trips': 0, 'completed_trips': 0}
            finally:
                conn.close()

    # ============================================
    # METODY DLA GALERII HANDLOWYCH
    # ============================================

    def import_galleries_from_csv(self, csv_path: str = "data/baza-galerii.csv") -> bool:
        """Importuje galerie handlowe z pliku CSV"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM galleries")
                if cursor.fetchone()[0] > 0:
                    return True

                df = pd.read_csv(csv_path)

                for _, row in df.iterrows():
                    gps = row['GPS']
                    latitude, longitude = self._parse_gps_coordinates(gps)

                    cursor.execute('''
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

                conn.commit()
                print(f"Zaimportowano {len(df)} galerii do bazy danych.")
                return True

            except Exception as e:
                print(f"Błąd podczas importu galerii z CSV: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

    def get_all_galleries(self) -> List[Dict]:
        """Pobiera wszystkie galerie handlowe"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM galleries ORDER BY lp")
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                print(f"Błąd pobierania galerii: {e}")
                return []
            finally:
                conn.close()

    def get_gallery_types(self) -> List[str]:
        """Pobiera unikalne typy galerii"""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT gallery_type FROM galleries WHERE gallery_type IS NOT NULL")
                return sorted([row[0] for row in cursor.fetchall()])
            except Exception as e:
                print(f"Błąd pobierania typów galerii: {e}")
                return []
            finally:
                conn.close()

    def import_wielkopolska_from_csv(self, csv_path: str = "data/baza-wielkopolska.csv") -> bool:
        """
        Importuje atrakcje Wielkopolski z pliku CSV
        """
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Sprawdź czy dane z Wielkopolski już istnieją (po nazwie)
                cursor.execute("SELECT COUNT(*) FROM places WHERE name LIKE '%Poznań%' OR location = 'Poznań'")
                if cursor.fetchone()[0] > 10:  # Jeśli jest dużo miejsc z Poznania
                    return True

                # Znajdź najwyższy LP
                cursor.execute("SELECT MAX(lp) FROM places")
                max_lp = cursor.fetchone()[0] or 0

                # Wczytaj dane z CSV
                df = pd.read_csv(csv_path)

                imported = 0
                for _, row in df.iterrows():
                    # Sprawdź czy miejsce już istnieje
                    cursor.execute("SELECT id FROM places WHERE name = ?", (row['Nazwa'],))
                    if cursor.fetchone():
                        continue

                    gps = row['GPS']
                    latitude, longitude = self._parse_gps_coordinates(gps)

                    max_lp += 1
                    cursor.execute('''
                        INSERT INTO places (
                            lp, name, category, location, latitude, longitude,
                            vibe, time_needed, description, season_hours, is_visited
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        max_lp,
                        row['Nazwa'],
                        row['Kategoria'],
                        row['Lokalizacja'],
                        latitude,
                        longitude,
                        row['Vibe'],
                        row['Czas'],
                        row['Opis'],
                        row['Sezon/Godziny'],
                        False
                    ))
                    imported += 1

                conn.commit()
                if imported > 0:
                    print(f"Zaimportowano {imported} atrakcji z Wielkopolski.")
                return True

            except Exception as e:
                print(f"Błąd podczas importu Wielkopolski: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
