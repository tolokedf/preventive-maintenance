# Preventive Maintenance SOP System — Project Context & Architecture

> **Document Purpose:** Persistent cross-session reference for Antigravity AI agents and engineers working on the `preventive-maintenance` module.

---

## 1. Important Rules & Development Guidelines

> [!IMPORTANT]
> **Strict Scope Directive:**
> **Do not add additional feature/button/text that did not mention in instruction.**
> Keep code changes, UI components, and logic strictly aligned with the exact requirements requested. Preserve all existing functionality.

---

## 2. System Overview
The **Preventive Maintenance System** is a standalone, dynamic web application designed for DF Automation & Robotics AMR field audits, checklist logs, and official form generation (`FRM/CS/xxx`).

- **Port:** `8000`
- **Backend:** Python 3 / Flask
- **Server:** Waitress WSGI (multi-threaded production server on port 8000)
- **PDF Engine:** ReportLab 5.0 (reconstructs pixel-accurate official corporate maintenance forms)
- **Frontend:** HTML5, Tailwind CSS, Google Sans / Roboto typography, Material Symbols Outlined icons
- **Theme:** Google Material Design 3 with Light / Dark / Follow System support (persisted via `df_theme_mode` in `localStorage`)

---

## 3. Core Architecture & Components

### 3.1. Dynamic Model Discovery (`AGV_type/`)
- Scans subfolders in `AGV_type/` (e.g., `AGV_type/Zalpha/`) for `.json` template schemas.
- Each JSON defines:
  - Form metadata (`formId`, `formCode`, `formTitle`, `subtitle`)
  - `machineFields` (model, serial number, mainboard, navwiz, odometer readings)
  - `recommendedReplacements` (guideline intervals, replacement checkboxes)
  - `sections` (checklists, 3-state rating matrix `1: OK`, `2: Future Attn`, `3: Immediate`, toggle items)
- Adding a new AGV schema to `AGV_type/<Family>/` automatically populates the form in the UI dropdown without modifying Python backend code.

### 3.2. Digital Signature System
- Interactive HTML5 `<canvas>` pad for both **Servicer Sign-off** and **Customer Acknowledgement**.
- Supports unified mouse, touch, and stylus pen drawing.
- Exports signatures as high-resolution PNG base64 (`data:image/png;base64,...`).
- **PDF Export:** Decodes base64 signatures and renders crisp vector/raster images in ReportLab tables.
- **HTML View:** Renders base64 signature image directly in the print layout.

### 3.3. Data Storage & Persistence
- **Database:** `data/db.json` (stores saved inspection reports with in-place upsert logic).
- **Attachments / Uploads:** `data/uploads/` (strictly gitignored).
- **Isolation:** Runtime data remains inside `data/` to avoid git conflicts during deployments.

---

## 4. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Interactive maintenance wizard & audit records dashboard |
| `GET` | `/api/health` | Service health status check |
| `GET` | `/api/agv-types` | Discovered AGV families and form list |
| `GET` | `/api/templates/<family>/<form_id>` | Form checklist template schema |
| `GET` | `/api/reports` | Lists all saved maintenance audits (sorted by date) |
| `GET` | `/api/reports/<id>` | Retrieves a single maintenance audit record |
| `POST` | `/api/reports` | Saves / upserts a maintenance audit record in-place (no duplicates) |
| `PUT` | `/api/reports/<id>` | Updates an existing maintenance audit record |
| `DELETE` | `/api/reports/<id>` | Deletes an audit record |
| `POST` | `/api/upload-photo` | Uploads an inspection photo attachment |
| `GET` | `/api/reports/<id>/pdf` | Generates and downloads the official ReportLab PDF form |
| `GET` | `/api/reports/<id>/html` | Renders the high-fidelity printable HTML view |

---

## 5. UI Theme & Design Tokens

- **Theme Key:** `df_theme_mode` (`'light'`, `'dark'`, `'system'`) in `localStorage`.
- **Light Surface:** `#f8fafd` canvas, `#ffffff` cards, `#dadce0` borders, `#202124` text.
- **Dark Surface:** `#131314` canvas, `#1e1f20` cards, `#3c4043` borders, `#e3e3e3` text.
- **Google 4-Color Accents:** Blue (`#1a73e8` / `#8ab4f8`), Red (`#d93025` / `#f28b82`), Yellow (`#f9ab00` / `#fdd663`), Green (`#1e8e3e` / `#81c995`).
- **Notifications:** Non-blocking Google Material 3 snackbar toasts.

---

## 6. Directory Structure

```
preventive-maintenance/
├── AGV_type/
│   └── Zalpha/
│       ├── zalpha_v3_3_robot.json
│       ├── auto_charger.json
│       ├── hooking_payload.json
│       └── towing_payload.json
├── data/                       # Gitignored runtime storage
│   ├── db.json
│   ├── reports/
│   └── uploads/
├── templates/
│   ├── index.html              # Main wizard & records dashboard
│   └── report_print.html       # Official printable form template
├── app.py                      # Flask REST API & routing
├── report_generator.py         # ReportLab PDF generator
├── requirements.txt            # Python dependencies
├── scripts/
│   └── run_server.py           # Production Waitress WSGI runner
├── README.md                   # User guide
└── PROJECT_CONTEXT.md          # Architectural reference (this file)
```
