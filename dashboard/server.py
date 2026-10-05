"""
Zero-dependency local HTTP server for Smart Irrigation Copilot Visual Cockpit.
Serves dashboard/index.html on http://localhost:8060 and opens default browser.
"""

import sys
import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# UTF-8 encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 8060
DASHBOARD_DIR = Path(__file__).resolve().parent

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


def run():
    os.chdir(DASHBOARD_DIR)
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, CustomHandler)
    url = f"http://localhost:{PORT}/index.html"
    print("=" * 60)
    print("  💧 Smart Irrigation Copilot · Apple-Style Visual Cockpit")
    print("=" * 60)
    print(f"  Servidor iniciado en: {url}")
    print("  Presiona CTRL+C en esta ventana para detener el servidor.")
    print("=" * 60)
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor cerrado correctamente.")
        httpd.server_close()


if __name__ == "__main__":
    run()
