"""
Generator kodów QR dla wycieczek
Nasza Mapa Przygód
"""

from io import BytesIO
from typing import List, Dict
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer


def generate_qr_code(data: str, box_size: int = 10, border: int = 4) -> bytes:
    """
    Generuje kod QR jako PNG.

    Args:
        data: Dane do zakodowania w QR
        box_size: Rozmiar każdego "piksela" QR
        border: Szerokość obramowania (w pikselach QR)

    Returns:
        Bajty obrazu PNG
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()


def generate_google_maps_url(places: List[Dict], start_location: Dict = None) -> str:
    """
    Generuje URL do Google Maps z trasą.

    Args:
        places: Lista miejsc z latitude i longitude
        start_location: Punkt startowy (opcjonalny)

    Returns:
        URL do Google Maps
    """
    if not places:
        return ""

    # Bazowy URL Google Maps Directions
    base_url = "https://www.google.com/maps/dir/"

    waypoints = []

    # Punkt startowy
    if start_location:
        waypoints.append(f"{start_location['latitude']},{start_location['longitude']}")

    # Miejsca
    for place in places:
        waypoints.append(f"{place['latitude']},{place['longitude']}")

    # Powrót do startu
    if start_location:
        waypoints.append(f"{start_location['latitude']},{start_location['longitude']}")

    return base_url + "/".join(waypoints)


def generate_trip_qr(places: List[Dict], trip_name: str = "",
                     start_location: Dict = None) -> bytes:
    """
    Generuje QR kod z linkiem do Google Maps dla wycieczki.

    Args:
        places: Lista miejsc
        trip_name: Nazwa wycieczki (nieużywane, dla kompatybilności)
        start_location: Punkt startowy

    Returns:
        Bajty obrazu PNG z kodem QR
    """
    maps_url = generate_google_maps_url(places, start_location)
    return generate_qr_code(maps_url)


def generate_trip_text_qr(places: List[Dict], trip_name: str = "",
                          stats: Dict = None) -> bytes:
    """
    Generuje QR kod z tekstem opisującym wycieczkę.

    Args:
        places: Lista miejsc
        trip_name: Nazwa wycieczki
        stats: Statystyki trasy

    Returns:
        Bajty obrazu PNG z kodem QR
    """
    lines = []

    if trip_name:
        lines.append(f"Wycieczka: {trip_name}")
        lines.append("")

    if stats:
        lines.append(f"Dystans: {stats.get('total_distance', 0):.0f} km")
        lines.append(f"Czas: {stats.get('total_time', 0):.1f}h")
        lines.append("")

    lines.append("Trasa:")
    for i, place in enumerate(places, 1):
        lines.append(f"{i}. {place['name']}")

    text = "\n".join(lines)
    return generate_qr_code(text)
