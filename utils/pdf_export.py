"""
Eksport wycieczek do PDF
Nasza Mapa Przygód
"""

from io import BytesIO
from typing import List, Dict
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class TripPDFExporter:
    """Klasa do generowania PDF z wycieczką"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Konfiguruje style PDF"""
        # Styl tytułu
        self.styles.add(ParagraphStyle(
            name='TripTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2563eb')
        ))

        # Styl podtytułu
        self.styles.add(ParagraphStyle(
            name='TripSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280')
        ))

        # Styl nagłówka miejsca
        self.styles.add(ParagraphStyle(
            name='PlaceTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=5,
            textColor=colors.HexColor('#1e293b')
        ))

        # Styl opisu
        self.styles.add(ParagraphStyle(
            name='PlaceDescription',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            textColor=colors.HexColor('#475569')
        ))

        # Styl informacji
        self.styles.add(ParagraphStyle(
            name='PlaceInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#94a3b8')
        ))

    def generate_pdf(self, trip_name: str, places: List[Dict], stats: Dict,
                     start_location: str = "Dom") -> bytes:
        """
        Generuje PDF z wycieczką.

        Args:
            trip_name: Nazwa wycieczki
            places: Lista miejsc
            stats: Statystyki trasy
            start_location: Nazwa punktu startowego

        Returns:
            Bajty pliku PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Nagłówek
        story.append(Paragraph("Nasza Mapa Przygód", self.styles['TripTitle']))
        story.append(Paragraph(trip_name, self.styles['TripSubtitle']))
        story.append(Paragraph(
            f"Wygenerowano: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            self.styles['TripSubtitle']
        ))
        story.append(Spacer(1, 20))

        # Statystyki
        stats_data = [
            ['Statystyki trasy', ''],
            ['Liczba miejsc:', str(stats.get('place_count', len(places)))],
            ['Całkowity czas:', f"{stats.get('total_time', 0):.1f}h"],
            ['Czas zwiedzania:', f"{stats.get('visit_time', 0):.1f}h"],
            ['Czas dojazdu:', f"{stats.get('travel_time', 0):.1f}h"],
            ['Całkowity dystans:', f"{stats.get('total_distance', 0):.1f} km"],
        ]

        stats_table = Table(stats_data, colWidths=[8*cm, 6*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 20))

        # Lista miejsc
        story.append(Paragraph("Plan wycieczki", self.styles['Heading2']))
        story.append(Spacer(1, 10))

        # Punkt startowy
        story.append(Paragraph(f"Start: {start_location}", self.styles['PlaceInfo']))
        story.append(Spacer(1, 10))

        # Miejsca
        for i, place in enumerate(places, 1):
            is_gallery = place.get('_is_gallery', False)
            icon = "🛒" if is_gallery else "📍"

            story.append(Paragraph(
                f"{i}. {icon} {place['name']}",
                self.styles['PlaceTitle']
            ))

            # Informacje o miejscu
            category = place.get('_gallery_type', place.get('category', ''))
            location = place.get('location', '')
            time_needed = place.get('time_needed', '')

            story.append(Paragraph(
                f"<b>Kategoria:</b> {category} | <b>Lokalizacja:</b> {location}",
                self.styles['PlaceInfo']
            ))
            story.append(Paragraph(
                f"<b>Czas:</b> {time_needed}",
                self.styles['PlaceInfo']
            ))

            # Opis
            description = place.get('description', '')
            if description:
                story.append(Paragraph(description, self.styles['PlaceDescription']))

            # Godziny otwarcia
            hours = place.get('season_hours', place.get('opening_hours', ''))
            if hours:
                story.append(Paragraph(f"Godziny: {hours}", self.styles['PlaceInfo']))

            story.append(Spacer(1, 5))

        # Powrót
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Powrót do: {start_location}", self.styles['PlaceInfo']))

        # Stopka
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            "Wygenerowano przez Nasza Mapa Przygód | naszamapaprzygod.streamlit.app",
            self.styles['PlaceInfo']
        ))

        # Buduj PDF
        doc.build(story)

        buffer.seek(0)
        return buffer.getvalue()


def generate_trip_pdf(trip_name: str, places: List[Dict], stats: Dict,
                      start_location: str = "Dom") -> bytes:
    """
    Funkcja pomocnicza do generowania PDF.

    Args:
        trip_name: Nazwa wycieczki
        places: Lista miejsc
        stats: Statystyki trasy
        start_location: Nazwa punktu startowego

    Returns:
        Bajty pliku PDF
    """
    exporter = TripPDFExporter()
    return exporter.generate_pdf(trip_name, places, stats, start_location)
