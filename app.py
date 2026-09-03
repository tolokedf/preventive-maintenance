"""
DF Preventive Maintenance & Robot SOP Application (Python / Flask)
Port: 8000
"""
import os
import sys
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory, Response, make_response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from report_generator import generate_maintenance_pdf

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "df-preventive-maintenance-secret-2026")
PORT = int(os.environ.get("PORT", 8000))

DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "reports"
DB_FILE = DATA_DIR / "db.json"
AGV_TYPE_DIR = BASE_DIR / "AGV_type"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(AGV_TYPE_DIR, exist_ok=True)

def read_db():
    if not DB_FILE.exists():
        initial = {"reports": []}
        write_db(initial)
        return initial
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        initial = {"reports": []}
        write_db(initial)
        return initial

def write_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def discover_agv_types():
    """Dynamically scans AGV_type/ folder for available AGV families and form templates."""
    types_list = []
    if not AGV_TYPE_DIR.exists():
        return types_list

    for family_folder in sorted(AGV_TYPE_DIR.iterdir()):
        if family_folder.is_dir() and not family_folder.name.startswith("."):
            family_name = family_folder.name
            forms = []
            
            for json_file in sorted(family_folder.glob("*.json")):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        form_data = json.load(f)
                        forms.append({
                            "formId": form_data.get("formId", json_file.stem),
                            "formCode": form_data.get("formCode", "FRM/CS/001"),
                            "formTitle": form_data.get("formTitle", "Maintenance Form"),
                            "subtitle": form_data.get("subtitle", json_file.stem.replace("_", " ").title()),
                            "agvFamily": family_name,
                            "filename": json_file.name
                        })
                except Exception as e:
                    print(f"Error reading template {json_file}: {e}")
            
            types_list.append({
                "name": family_name,
                "formsCount": len(forms),
                "forms": forms
            })
            
    return types_list

def load_template(agv_family: str, form_id: str):
    """Loads a specific form JSON template."""
    family_dir = AGV_TYPE_DIR / agv_family
    if not family_dir.exists():
        return None
        
    for json_file in family_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("formId") == form_id or json_file.stem == form_id:
                    return data
        except Exception:
            continue
    return None

# ==================== WEB PAGES ====================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(str(UPLOADS_DIR), filename)

# ==================== REST APIS ====================

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "preventive-maintenance", "port": PORT})

@app.route("/api/agv-types", methods=["GET"])
def get_agv_types():
    """Returns list of discovered AGV families and forms from AGV_type directory."""
    return jsonify(discover_agv_types())

@app.route("/api/templates/<agv_family>/<form_id>", methods=["GET"])
def get_form_template(agv_family, form_id):
    tpl = load_template(agv_family, form_id)
    if not tpl:
        return jsonify({"error": f"Template not found for {agv_family} / {form_id}"}), 404
    return jsonify(tpl)

@app.route("/api/reports", methods=["GET", "POST"])
def reports_handler():
    db = read_db()
    if request.method == "GET":
        sorted_reports = sorted(db.get("reports", []), key=lambda r: r.get("updatedAt", r.get("createdAt", "")), reverse=True)
        return jsonify(sorted_reports)
        
    elif request.method == "POST":
        data = request.get_json(force=True) or {}
        report_id = data.get("id") or f"pm_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        
        data["id"] = report_id
        data["createdAt"] = data.get("createdAt") or datetime.utcnow().isoformat() + "Z"
        data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
        
        reports = db.setdefault("reports", [])
        existing_idx = next((i for i, r in enumerate(reports) if r.get("id") == report_id), None)
        if existing_idx is not None:
            reports[existing_idx] = data
        else:
            reports.append(data)
            
        write_db(db)
        return jsonify(data), 200 if existing_idx is not None else 201

@app.route("/api/reports/<report_id>", methods=["GET", "PUT", "DELETE"])
def single_report(report_id):
    db = read_db()
    reports = db.get("reports", [])
    idx = next((i for i, r in enumerate(reports) if r.get("id") == report_id), None)
    
    if request.method == "GET":
        if idx is None:
            return jsonify({"error": "Report not found"}), 404
        return jsonify(reports[idx])
        
    elif request.method == "PUT":
        if idx is None:
            return jsonify({"error": "Report not found"}), 404
        data = request.get_json(force=True) or {}
        reports[idx].update(data)
        reports[idx]["id"] = report_id
        reports[idx]["updatedAt"] = datetime.utcnow().isoformat() + "Z"
        write_db(db)
        return jsonify(reports[idx])
        
    elif request.method == "DELETE":
        if idx is None:
            return jsonify({"error": "Report not found"}), 404
        reports.pop(idx)
        write_db(db)
        return jsonify({"success": True, "message": "Report deleted successfully"})

@app.route("/api/upload-photo", methods=["POST"])
def upload_photo():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "No file selected"}), 400
        
    safe_fn = secure_filename(file.filename) or "photo.jpg"
    unique_fn = f"pm-{int(time.time())}-{uuid.uuid4().hex[:6]}-{safe_fn}"
    save_path = UPLOADS_DIR / unique_fn
    file.save(str(save_path))
    
    return jsonify({
        "url": f"/uploads/{unique_fn}",
        "filename": unique_fn,
        "originalName": file.filename
    }), 201

@app.route("/api/reports/<report_id>/pdf", methods=["GET"])
def export_pdf(report_id):
    db = read_db()
    report = next((r for r in db.get("reports", []) if r.get("id") == report_id), None)
    if not report:
        return jsonify({"error": "Report not found"}), 404
        
    try:
        pdf_bytes = generate_maintenance_pdf(report)
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        filename = f"Maintenance_Report_{report.get('formCode', 'FRM')}_{report.get('id', 'rep')}.pdf".replace("/", "_")
        response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@app.route("/api/reports/<report_id>/html", methods=["GET"])
def export_html(report_id):
    db = read_db()
    report = next((r for r in db.get("reports", []) if r.get("id") == report_id), None)
    if not report:
        return "Report not found", 404
    return render_template("report_print.html", report=report)

if __name__ == "__main__":
    print(f"🛠️ Starting Preventive Maintenance Server on http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
