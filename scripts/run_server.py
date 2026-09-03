"""
Preventive Maintenance Production Server (Waitress WSGI)
Runs on Port 8000
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import app, PORT

if __name__ == "__main__":
    try:
        from waitress import serve
        print("=" * 65)
        print(f"🛠️ Preventive Maintenance Server (Python / Waitress WSGI)")
        print(f"📍 Local Access:   http://localhost:{PORT}")
        print(f"🌐 Network Access: http://0.0.0.0:{PORT}")
        print("=" * 65)
        serve(app, host="0.0.0.0", port=PORT, threads=6)
    except ImportError:
        print("Waitress not installed, falling back to Flask development server...")
        app.run(host="0.0.0.0", port=PORT, debug=False)
