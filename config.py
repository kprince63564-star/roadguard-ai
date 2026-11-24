"""
ROADGUARD AI - System Configuration
Centralized configuration for application settings, AI model paths,
severity scoring parameters, database, and UI theme.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
DATABASE_DIR = BASE_DIR / "database"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = DATABASE_DIR / "roadguard.db"

# Ensure runtime directories exist
for directory in [MODELS_DIR, UPLOADS_DIR, OUTPUTS_DIR, REPORTS_DIR, DATABASE_DIR, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default Model Configuration
DEFAULT_MODEL_PATH = MODELS_DIR / "best.pt"
FALLBACK_MODEL_NAME = "yolov8n.pt"  # Pretrained weights as base/fallback
CONFIDENCE_THRESHOLD = 0.35
IOU_THRESHOLD = 0.45

# Damage Classes & Color Codes
DAMAGE_CLASSES = {
    0: {"name": "Pothole", "color": "#EF4444", "base_severity": 45, "type": "Pothole"},
    1: {"name": "Longitudinal Crack", "color": "#F59E0B", "base_severity": 25, "type": "Crack"},
    2: {"name": "Transverse Crack", "color": "#FBBF24", "base_severity": 20, "type": "Crack"},
    3: {"name": "Alligator Crack", "color": "#DC2626", "base_severity": 40, "type": "Crack"},
    4: {"name": "Manhole Cover Issue", "color": "#3B82F6", "base_severity": 30, "type": "Surface"},
    5: {"name": "Road Surface Patch / Rutting", "color": "#8B5CF6", "base_severity": 22, "type": "Surface"},
}

# Priority Bands
PRIORITY_BANDS = {
    "LOW": {"min": 0, "max": 39, "label": "Low Priority", "color": "#10B981", "badge_class": "badge-low"},
    "MEDIUM": {"min": 40, "max": 69, "label": "Medium Priority", "color": "#F59E0B", "badge_class": "badge-medium"},
    "HIGH": {"min": 70, "max": 100, "label": "High Priority", "color": "#EF4444", "badge_class": "badge-high"},
}

# Report Status Lifecycle
REPORT_STATUSES = [
    "New",
    "Under Review",
    "Inspection Scheduled",
    "Repair in Progress",
    "Resolved"
]

STATUS_COLORS = {
    "New": "#FB923C",               # Warm Tangerine
    "Under Review": "#F59E0B",      # Amber
    "Inspection Scheduled": "#EAB308", # Traffic Yellow
    "Repair in Progress": "#EA580C", # Deep Safety Orange
    "Resolved": "#10B981"           # Emerald Green
}

# Scoring Weights
SCORING_WEIGHTS = {
    "class_severity": 0.35,      # Impact of most severe detected class
    "area_ratio": 0.30,          # Impact of damaged pixel area relative to image
    "count_factor": 0.15,        # Multiplier for multiple damage clusters
    "confidence_factor": 0.10,   # High detection certainty increases priority
    "context_modifier": 0.10     # Road type, traffic density, wet condition
}

# Context Modifiers
ROAD_TYPE_MODIFIERS = {
    "Highway / Expressway": 1.25,
    "Arterial / Main City Road": 1.15,
    "Residential / Suburb Street": 1.0,
    "Rural / Service Road": 0.85
}

TRAFFIC_VOLUME_MODIFIERS = {
    "Heavy (Trucks / Public Transit)": 1.2,
    "Moderate": 1.0,
    "Low / Local Access Only": 0.85
}

# Map Defaults
DEFAULT_MAP_CENTER = [28.6139, 77.2090]  # Standard default center
DEFAULT_MAP_ZOOM = 12

# File Upload Rules
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 20
