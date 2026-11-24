# ROADGUARD AI 🛡️
### Smart Road Health & Damage Intelligence Platform

**ROADGUARD AI** is an AI-powered road damage detection, geospatial intelligence, and municipal maintenance prioritization platform. It bridges the gap between raw citizen/inspection imagery and structured civil engineering action by combining computer vision detection, explainable hazard triage scoring, interactive GIS mapping, and automated PDF work order generation.

---

## 🌟 Key Features

1. **AI Road Damage Detection (Ultralytics YOLO)**
   - Upload high-resolution road photos (JPG, PNG) or capture live road imagery via device camera.
   - Detects critical surface defects including **Potholes**, **Alligator Cracks**, **Longitudinal Cracks**, **Transverse Cracks**, and **Manhole Cover Defects**.
   - Side-by-side visual comparison between original road photos and AI-annotated bounding box overlays with class tags and confidence percentages.

2. **Explainable Visual Priority Scoring (0–100)**
   - Algorithmic, multi-variable hazard ranking designed for municipal triage:
     - **Class Baseline Severity:** Accounts for high-impact cavity hazards vs surface hair cracks.
     - **Damaged Surface Area Ratio:** Computes total bounding box pixel coverage relative to image size.
     - **Region Multiplicity & Cluster Density:** Detects cluster degradation.
     - **AI Confidence Weight:** Calibrates score based on detection certainty.
     - **Site & Roadway Context:** Multipliers for highway/expressway vs residential corridors, heavy truck traffic, and wet/rainy pavement.
   - Categorized into clear priority bands:
     - **High Priority (70–100):** Immediate field triage required (24–48 hours).
     - **Medium Priority (40–69):** Scheduled weekly maintenance.
     - **Low Priority (0–39):** Routine quarterly monitoring.
   - *Engineering Disclaimer:* Visual priority scores reflect 2D surface degradation to guide human inspection triage; 2D photos cannot determine physical core depth or pavement structural load capacity.

3. **Geospatial Intelligence & Interactive GIS Map**
   - Built with Folium and OpenStreetMap with modern dark cartography tiles.
   - Automatic GPS coordinate extraction from photo EXIF metadata (when captured on GPS-enabled smartphones).
   - Color-coded priority pins (Red: High, Amber: Medium, Green: Low) with click-through diagnostic popups.
   - Clustered incident views and filter layers (by damage category, status, priority).
   - Strict coordinate safety: Reports without verified GPS coordinates are never placed at arbitrary map locations and are triaged in a dedicated "Unlocated Incidents" list.

4. **Maintenance Priority Queue (Authority-Facing)**
   - Dynamically ranks pending road defects from highest to lowest visual priority score.
   - Displays granular algorithmic reasoning explaining why each incident appears near the top.
   - Fast-action work order dispatch with customizable audit comments.

5. **Lifecycle Status Audit & History**
   - Full status lifecycle: `New` ➔ `Under Review` ➔ `Inspection Scheduled` ➔ `Repair in Progress` ➔ `Resolved`.
   - Immutable audit logging tracking who changed the status, when, and work order notes.

6. **Executive Dashboard & Longitudinal Analytics**
   - Real-time KPI metric cards (Total reports, potholes, cracks, awaiting inspection, repaired, average priority).
   - Interactive Plotly visualizations: Damage type distribution, priority score distribution, lifecycle pipeline, and high-incident corridor rankings.

7. **Official Municipal PDF Work Orders & CSV Exports**
   - Instant PDF compilation via ReportLab formatted as official municipal road health reports with branding, coordinates, AI metrics, embedded imagery, inspector notes, and civil sign-off lines.
   - One-click CSV database export for GIS, AutoCAD, and municipal asset management software.

8. **Role-Based Access Control (RBAC)**
   - **Municipal Authority:** Accesses the maintenance queue, updates status lifecycle, and compiles official PDF work orders.
   - **Citizen Reporter:** Captures and reports road hazards, views public live damage map.
   - Built-in rapid role switcher for demonstrations.

---

## 🏗️ System Architecture & Project Structure

```
ROADGUARD-AI/
├── app.py                      # Main Streamlit application & navigation router
├── config.py                   # Centralized configuration, paths, scoring weights, & classes
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation & setup guide
├── .gitignore                  # Git exclusions for environments, binaries, & local cache
│
├── models/                     # Checkpoint weights directory
│   └── best.pt                 # Place your trained YOLO road damage weights here
│
├── detection/                  # Computer vision inference package
│   ├── __init__.py
│   └── detector.py             # Ultralytics YOLO loader, inference, & bounding box renderer
│
├── severity/                   # Triage & severity scoring package
│   ├── __init__.py
│   └── scoring.py              # Explainable 0-100 visual priority scoring engine
│
├── database/                   # SQLite relational persistence package
│   ├── __init__.py
│   └── db.py                   # Thread-safe SQLite CRUD, audit history, & user auth
│
├── dashboard/                  # Modular UI navigation views
│   ├── __init__.py
│   ├── overview.py             # Executive KPI dashboard & interactive charts
│   ├── detect.py               # AI detection, camera capture, & report registration
│   ├── reports_view.py         # Full reports management, filtering, & status updates
│   ├── map_view.py             # Live interactive Folium GIS map
│   ├── queue_view.py           # Authority maintenance priority triage queue
│   ├── analytics_view.py       # Deep statistical analytics & correlation charts
│   ├── export_view.py          # PDF work order generation & CSV database export
│   └── settings_view.py        # Model diagnostics, weights loader, & RBAC controls
│
├── utils/                      # Helper libraries
│   ├── __init__.py
│   ├── image_processing.py     # EXIF GPS extraction, image validation, & storage
│   ├── pdf_generator.py        # ReportLab municipal PDF work order generator
│   ├── helpers.py              # ID generator, formatters, HTML badge renderers
│   └── auth.py                 # Session state authentication & role utilities
│
├── assets/                     # UI styling & test media
│   ├── logo.png                # High-resolution platform shield emblem
│   ├── styles.css              # Custom GovTech SaaS dark theme
│   └── sample_road.jpg         # Sample test asphalt image with simulated damage
│
├── uploads/                    # Persisted original user-submitted road photos
├── outputs/                    # AI-annotated visual inspection outputs
│   └── reports/                # Generated PDF inspection work orders
└── tests/                      # Automated unit test suite
    ├── __init__.py
    └── test_core.py            # Comprehensive tests for database, scoring, PDF, & detector
```

---

## ⚡ Quick Start & Execution Guide

### 1. Prerequisites
- Python 3.10 or 3.11 installed.
- Git (optional, for cloning).

### 2. Installation
Open your terminal in the project directory:

```bash
# Optional: Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Launch Application
Start the Streamlit web application:

```bash
streamlit run app.py
```

The application will launch automatically in your browser at `http://localhost:8501`.

---

## 🤖 AI Model Integration (`models/best.pt`)

ROADGUARD AI is architected with a modular model loader that accepts any PyTorch Ultralytics YOLO checkpoint.

### How to Add Your Trained Weights:
1. Obtain or fine-tune a YOLO model on a road damage dataset such as:
   - **RDD2022 (Road Damage Dataset):** Global multi-national dataset featuring labeled potholes and crack classes (`D00` Pothole, `D10` Alligator Crack, `D20` Longitudinal Crack, `D40` Transverse Crack).
   - **Roboflow Road Damage Projects:** Pre-annotated road condition datasets.
2. Rename your exported weights file to `best.pt`.
3. Place it in the `models/` directory:
   ```
   ROADGUARD-AI/
   └── models/
       └── best.pt
   ```
4. ROADGUARD AI will automatically detect the checkpoint and switch from diagnostic mode to live inference mode.
5. You can also specify any custom path dynamically in the **Settings / About** tab using the model switcher.

### Demonstration & Fallback Mode:
If you do not have trained weights installed yet:
- The platform **will not fabricate fake results or claim unmeasured accuracy metrics**.
- A clear diagnostic notice will inform you that weights are missing.
- You can enable the **Clearly Labeled Demo Simulation Mode** checkbox to test the complete user experience, including image upload, bounding box visualization, priority scoring, database persistence, GIS mapping, and PDF compilation. All records created in this mode are prominently stamped with `[DEMO SIMULATION]` to maintain data integrity.

---

## 🧪 Running Automated Unit Tests

To run the automated verification test suite:

```bash
python -m unittest tests/test_core.py
```

The test suite validates:
- ✅ **Scoring Engine:** Mathematical calculations, edge cases, zero detections, and priority band classifications.
- ✅ **Database Relational Operations:** Foreign key constraints, CRUD persistence, and status history audit trails.
- ✅ **Detector Diagnostics:** Proper detection fallback behavior and checkpoint discovery.
- ✅ **PDF Work Order Generation:** ReportLab compilation, element geometry, and document output.
- ✅ **CSV Serializer:** Correct tabular data export.
- ✅ **Authentication:** Password hashing with cryptographic salts and role validation.

---

## 📋 Default Credentials

For testing and demonstration, default accounts are pre-seeded:

| Role | Username | Password |
|---|---|---|
| **Municipal Road Engineer (Admin)** | `admin` | `admin123` |
| **Citizen Reporter** | `citizen` | `citizen123` |

You can also toggle between roles at any time using the **Switch User Role** widget in the sidebar.

---

## ⚖️ Engineering & Safety Notice

*ROADGUARD AI provides automated visual triage to help municipal authorities prioritize field inspections. It does not replace on-site physical geotechnical assessments, non-destructive radar pavement evaluation, or core drilling. Municipalities should always conduct certified civil engineering inspections prior to committing major resurfacing funds.*
