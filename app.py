"""
DF Preventive Maintenance Report Application
Port: 8000
"""
import os
from flask import Flask, render_template_string, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8000))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DF Preventive Maintenance Report</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-8">
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-8">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xl font-bold">🛠️</div>
        <div>
          <h1 class="text-2xl font-bold">Preventive Maintenance Report App</h1>
          <p class="text-xs text-slate-400">Periodic AMR Audit, Component Wear & Checklist Generator</p>
        </div>
      </div>
      <a href="http://localhost:8080" class="text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
        &larr; Back to Portal
      </a>
    </div>

    <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
      <h2 class="text-lg font-semibold mb-4 text-emerald-400">Robot Maintenance Checklists</h2>
      <p class="text-sm text-slate-400 mb-6">
        App scaffold initialized. Configure inspections, hardware checks, and generate AI-enhanced maintenance PDF summaries.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <h3 class="font-bold text-sm text-slate-200 mb-1">Chassis & Drive Wheels</h3>
          <p class="text-xs text-slate-400">Tire wear, suspension tension, motor temperature</p>
        </div>
        <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <h3 class="font-bold text-sm text-slate-200 mb-1">Sensors & LiDARs</h3>
          <p class="text-xs text-slate-400">Lens cleanliness, calibration offset, emergency stops</p>
        </div>
        <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <h3 class="font-bold text-sm text-slate-200 mb-1">Battery & Power Unit</h3>
          <p class="text-xs text-slate-400">Cycle count, health percentage, charging contact wear</p>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "preventive-maintenance", "port": PORT})

if __name__ == "__main__":
    print(f"🛠️ Starting Preventive Maintenance Server on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
