"""
Funkcje pomocnicze dla tras i wycieczek
Nasza Mapa Przygód
"""

import math
import re
from typing import List, Dict, Tuple, Optional

from utils.constants import HOME_LOCATION, CATEGORY_COLORS


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Oblicza odległość między dwoma punktami (wzór Haversine)"""
    R = 6371  # Promień Ziemi w km
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def estimate_travel_time(distance_km: float, speed_kmh: float = 50) -> float:
    """Szacuje czas podróży w godzinach"""
    return distance_km / speed_kmh


def parse_time_for_display(time_str: str) -> float:
    """Parsuje string czasu na wartość w godzinach"""
    if not time_str:
        return 1.0
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
    """Zwraca kolor dla kategorii miejsca"""
    main_cat = category.split('/')[0]
    return CATEGORY_COLORS.get(main_cat, "#6b7280")


def optimize_route_nearest_neighbor(places: List[Dict], start_lat: float, start_lon: float) -> List[Dict]:
    """Optymalizuje trasę algorytmem Nearest Neighbor"""
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


def calculate_route_distance(places: List[Dict], start_lat: float, start_lon: float) -> float:
    """Oblicza całkowitą długość trasy (z powrotem do startu)"""
    if not places:
        return 0.0

    total = 0.0
    prev_lat, prev_lon = start_lat, start_lon

    for place in places:
        total += haversine_distance(prev_lat, prev_lon, place['latitude'], place['longitude'])
        prev_lat, prev_lon = place['latitude'], place['longitude']

    # Powrót do punktu startowego
    total += haversine_distance(prev_lat, prev_lon, start_lat, start_lon)

    return total


def optimize_route_2opt(places: List[Dict], start_lat: float, start_lon: float,
                        max_iterations: int = 100) -> List[Dict]:
    """
    Optymalizuje trasę algorytmem 2-opt.

    2-opt jest algorytmem poprawy lokalnej, który iteracyjnie zamienia
    krawędzie w trasie, jeśli prowadzi to do skrócenia całkowitej długości.

    Args:
        places: Lista miejsc do odwiedzenia
        start_lat: Szerokość geograficzna punktu startowego
        start_lon: Długość geograficzna punktu startowego
        max_iterations: Maksymalna liczba iteracji bez poprawy

    Returns:
        Zoptymalizowana lista miejsc
    """
    if len(places) < 3:
        return places.copy()

    # Rozpocznij od rozwiązania Nearest Neighbor
    route = optimize_route_nearest_neighbor(places, start_lat, start_lon)
    best_distance = calculate_route_distance(route, start_lat, start_lon)

    improved = True
    iterations_without_improvement = 0

    while improved and iterations_without_improvement < max_iterations:
        improved = False

        for i in range(len(route) - 1):
            for j in range(i + 2, len(route)):
                # Spróbuj odwrócić segment między i a j
                new_route = route[:i+1] + route[i+1:j+1][::-1] + route[j+1:]
                new_distance = calculate_route_distance(new_route, start_lat, start_lon)

                if new_distance < best_distance:
                    route = new_route
                    best_distance = new_distance
                    improved = True
                    iterations_without_improvement = 0
                    break

            if improved:
                break

        if not improved:
            iterations_without_improvement += 1
            improved = iterations_without_improvement < max_iterations

    return route


def optimize_route(places: List[Dict], start_lat: float, start_lon: float,
                   algorithm: str = "2opt") -> List[Dict]:
    """
    Optymalizuje trasę wybranym algorytmem.

    Args:
        places: Lista miejsc do odwiedzenia
        start_lat: Szerokość geograficzna punktu startowego
        start_lon: Długość geograficzna punktu startowego
        algorithm: Algorytm optymalizacji ("nearest_neighbor" lub "2opt")

    Returns:
        Zoptymalizowana lista miejsc
    """
    if not places:
        return []

    if algorithm == "2opt":
        return optimize_route_2opt(places, start_lat, start_lon)
    else:
        return optimize_route_nearest_neighbor(places, start_lat, start_lon)


def calculate_trip_stats_detailed(places: List[Dict]) -> Dict:
    """Oblicza szczegółowe statystyki trasy z czasami dojazdu między punktami"""
    if not places:
        return {'total_time': 0, 'total_distance': 0, 'visit_time': 0, 'travel_time': 0,
                'place_count': 0, 'segments': []}

    visit_time = sum(parse_time_for_display(p['time_needed']) for p in places)
    total_distance = 0.0
    segments = []

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


def generate_smart_trip(all_places: List[Dict], categories: List[str] = None,
                       max_places: int = 5, max_hours: float = 8.0,
                       prefer_unvisited: bool = True, variant: int = 0,
                       algorithm: str = "2opt") -> Tuple[List[Dict], Dict]:
    """
    Generuje wycieczkę. variant=0-4 różne zakresy odległości

    Args:
        all_places: Lista wszystkich miejsc
        categories: Lista kategorii do filtrowania
        max_places: Maksymalna liczba miejsc
        max_hours: Maksymalny czas wycieczki w godzinach
        prefer_unvisited: Czy preferować nieodwiedzone miejsca
        variant: Wariant odległości (0-4)
        algorithm: Algorytm optymalizacji ("2opt" lub "nearest_neighbor")

    Returns:
        Tuple (lista miejsc, statystyki)
    """
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
        selected = optimize_route(selected, HOME_LOCATION['latitude'], HOME_LOCATION['longitude'], algorithm)

    return selected, calculate_trip_stats_detailed(selected)


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
        margin = 0.2  # ~20km margines
        if not (min_lat - margin <= g_lat <= max_lat + margin and
                min_lon - margin <= g_lon <= max_lon + margin):
            continue

        # Oblicz odległość od centroidu trasy
        dist_from_centroid = haversine_distance(centroid_lat, centroid_lon, g_lat, g_lon)

        # Oblicz minimalny detour
        min_detour = float('inf')
        best_insert_index = 0

        for i, (lat, lon) in enumerate(route_points[:-1]):
            next_lat, next_lon = route_points[i + 1]

            dist_to_current = haversine_distance(lat, lon, g_lat, g_lon)
            dist_to_next = haversine_distance(next_lat, next_lon, g_lat, g_lon)
            original_dist = haversine_distance(lat, lon, next_lat, next_lon)
            new_dist = dist_to_current + dist_to_next
            detour = new_dist - original_dist

            if detour < min_detour:
                min_detour = detour
                best_insert_index = i + 1

        # Odrzuć jeśli detour za duży
        if min_detour > max_detour_km:
            continue

        # Scoring
        gallery_size_bonus = 0
        if 'Mega' in gallery.get('gallery_type', '') or 'Hyper' in gallery.get('gallery_type', ''):
            gallery_size_bonus = -2
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
