# Preventive Maintenance SOP System — Project Context

## 1. Overview
The **Preventive Maintenance System** provides standard operating procedure (SOP) inspection workflows, dynamic model templates, and official audit generation for DF AMRs, chargers, and payload mechanisms.

## 2. Technical Stack
- **Backend**: Python 3 / Flask
- **Server**: Waitress WSGI (Multi-threaded worker pool on Port 8000)
- **PDF Engine**: ReportLab 5.0 (Reconstructs official DF corporate maintenance forms `FRM/CS/xxx`)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JS
- **Storage**: `data/db.json` and `data/uploads/` (strictly isolated and gitignored)

## 3. Dynamic Model Architecture (`AGV_type/`)
- Backend dynamically discovers model families by scanning subfolders in `AGV_type/`.
- Each subfolder contains `.json` template schemas defining fields, replacement guidelines, and inspection sections.
- When new AGV models or variants are introduced, adding their JSON schemas to `AGV_type/<Family>/` automatically surfaces them in the application.

## 4. Endpoints
- `GET /` — Interactive maintenance wizard
- `GET /api/agv-types` — Returns discovered AGV families and form list
- `GET /api/templates/<family>/<form_id>` — Returns specific form template
- `GET /api/reports` — Lists past maintenance logs
- `GET /api/reports/<id>` — Fetches a single maintenance report
- `POST /api/reports` — Saves a completed maintenance audit
- `DELETE /api/reports/<id>` — Deletes a report
- `POST /api/upload-photo` — Uploads an inspection photo
- `GET /api/reports/<id>/pdf` — Generates and downloads the official PDF report
- `GET /api/reports/<id>/html` — Renders the printable HTML view
