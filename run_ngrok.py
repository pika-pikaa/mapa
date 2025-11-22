"""
Skrypt do uruchomienia aplikacji Streamlit z publicznym dostepem przez ngrok
"""

import subprocess
import sys
import time
import threading
import os

# Fix dla kodowania Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_streamlit():
    """Uruchamia aplikacje Streamlit w tle"""
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ])

def main():
    print("=" * 60)
    print("NASZA MAPA PRZYGOD - Uruchamianie aplikacji")
    print("=" * 60)

    # Uruchom Streamlit w osobnym watku
    print("\n[*] Uruchamiam aplikacje Streamlit...")
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    streamlit_thread.start()

    # Poczekaj na uruchomienie Streamlita
    print("[*] Czekam na uruchomienie serwera...")
    time.sleep(5)

    # Uruchom ngrok
    try:
        from pyngrok import ngrok

        print("\n[*] Tworze tunel ngrok...")
        public_url = ngrok.connect(8501)

        print("\n" + "=" * 60)
        print("APLIKACJA URUCHOMIONA!")
        print("=" * 60)
        print(f"\n>>> Lokalny adres:    http://localhost:8501")
        print(f">>> Publiczny adres:  {public_url}")
        print("\n[!] Udostepnij publiczny link znajomym!")
        print("\n[!] Nacisnij Ctrl+C, aby zakonczyc...")
        print("=" * 60)

        # Utrzymuj dzialanie
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[*] Zamykam tunel ngrok...")
            ngrok.disconnect(public_url)
            print("[OK] Do zobaczenia!")

    except ImportError:
        print("\n[ERROR] Nie znaleziono pyngrok")
        print("        Zainstaluj przez: pip install pyngrok")
        print("\n>>> Aplikacja dostepna lokalnie: http://localhost:8501")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[OK] Do zobaczenia!")

    except Exception as e:
        print(f"\n[ERROR] Blad ngrok: {e}")
        print("\n[INFO] Wskazowki:")
        print("   1. Zarejestruj sie na https://ngrok.com")
        print("   2. Pobierz authtoken z dashboardu")
        print("   3. Uruchom: ngrok config add-authtoken YOUR_TOKEN")
        print("\n>>> Aplikacja dostepna lokalnie: http://localhost:8501")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[OK] Do zobaczenia!")

if __name__ == "__main__":
    main()