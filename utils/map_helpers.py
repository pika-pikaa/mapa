"""
Funkcje pomocnicze do tworzenia map
Nasza Mapa Przygód
"""

import folium
from typing import List, Dict

from utils.constants import HOME_LOCATION
from utils.trip_helpers import get_category_color


def create_map(places: List[Dict], show_home: bool = True, show_route: bool = False,
               center_lat: float = 50.9, center_lon: float = 16.5, zoom: int = 9,
               galleries: List[Dict] = None) -> folium.Map:
    """
    Tworzy mapę Folium z miejscami i opcjonalną trasą

    Args:
        places: Lista miejsc do wyświetlenia
        show_home: Czy pokazać marker domu
        show_route: Czy pokazać linię trasy
        center_lat: Szerokość geograficzna centrum mapy
        center_lon: Długość geograficzna centrum mapy
        zoom: Poziom powiększenia
        galleries: Lista galerii handlowych do wyświetlenia

    Returns:
        Obiekt mapy Folium
    """
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
