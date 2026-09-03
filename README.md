# DF Preventive Maintenance & Robot SOP System

An intelligent inspection and reporting engine for autonomous mobile robots (AMRs), chargers, and payload handlers across the **DF Automation & Robotics** product ecosystem.

---

## 🌟 Key Features

- **Dynamic AGV Model Discovery (`AGV_type/`)**: Dynamically scans `AGV_type/` for robot families. Adding a new robot family or payload handler JSON template makes it instantly available in the UI without modifying Python code.
- **Official Source Form Templates**:
  - `Zalpha V3.3 Standard AMR Maintenance Form` (`FRM/CS/015-V1.0`)
  - `Auto Charger Inspection Form` (`FRM/CS/004-V1.3`)
  - `Zalpha Hooking Payload Handler (Zalpha-HW01)` (`FRM/CS/014-V1.0`)
  - `Zalpha Towing Payload Handler (Zalpha-TW01)` (`FRM/CS/013-V1.0`)
- **Step-by-Step SOP Wizard**: Guides engineers through hardware checks, sensor verifications, voltage readings, wear thicknesses, and part replacement requests with interval guidelines.
- **Exact Replica PDF & HTML Export**: Generates pixel-accurate ReportLab PDFs matching the official company maintenance forms, complete with digital sign-off and scheduled next service dates.
- **Wi-Fi / LAN Network Accessible**: Runs with Waitress multi-threaded WSGI on port `8000`.

---

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Application
```bash
# Production server (Waitress WSGI on port 8000)
python3 scripts/run_server.py

# Or development server
python3 app.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📁 Directory Structure

```
preventive-maintenance/
├── app.py                      # Flask API & dynamic SOP engine
├── report_generator.py         # Official ReportLab PDF form generator
├── AGV_type/                   # Dynamic AGV model family schemas
│   └── Zalpha/                 # Zalpha AGV series folder
│       ├── zalpha_v3_3_robot.json   # FRM/CS/015-V1.0
│       ├── auto_charger.json        # FRM/CS/004-V1.3
│       ├── hooking_payload.json     # FRM/CS/014-V1.0
│       └── towing_payload.json      # FRM/CS/013-V1.0
├── data/                       # Runtime storage (.gitignored)
│   ├── uploads/                # Uploaded photos
│   └── db.json                 # Saved inspection logs
├── scripts/run_server.py       # Production server launcher (Waitress)
└── templates/
    ├── index.html              # Responsive Tailwind web interface
    └── report_print.html       # Printable HTML replica of official forms
```
