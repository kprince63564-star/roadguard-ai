"""
ROADGUARD AI - Database Operations
Thread-safe SQLite database manager for reports, detections, status audit trails, and authentication.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import hashlib
import os

from config import DB_PATH, REPORT_STATUSES, STATUS_COLORS

logger = logging.getLogger("roadguard.database")

def get_connection() -> sqlite3.Connection:
    """Creates and returns a connection to SQLite with row factory set."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a password with SHA-256 and salt."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${hashed}", salt

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a plain password against stored salt$hash."""
    try:
        salt, _ = stored_hash.split("$", 1)
        expected, _ = hash_password(password, salt)
        return expected == stored_hash
    except Exception:
        return False

def init_db():
    """Initializes SQLite database schema and indices."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'citizen',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Damage Reports Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        damage_type TEXT NOT NULL,
        primary_class TEXT NOT NULL,
        detection_count INTEGER NOT NULL DEFAULT 0,
        max_confidence REAL NOT NULL DEFAULT 0.0,
        avg_confidence REAL NOT NULL DEFAULT 0.0,
        priority_score REAL NOT NULL DEFAULT 0.0,
        priority_band TEXT NOT NULL DEFAULT 'LOW',
        urgency_level TEXT NOT NULL DEFAULT 'Routine Monitoring',
        latitude REAL,
        longitude REAL,
        location_address TEXT,
        location_source TEXT DEFAULT 'Not Provided',
        road_type TEXT DEFAULT 'Arterial / Main City Road',
        traffic_volume TEXT DEFAULT 'Moderate',
        weather_condition TEXT DEFAULT 'Dry / Clear',
        original_image_path TEXT,
        annotated_image_path TEXT,
        status TEXT NOT NULL DEFAULT 'New',
        reporter_name TEXT DEFAULT 'Citizen Reporter',
        reporter_role TEXT DEFAULT 'citizen',
        notes TEXT,
        score_breakdown_json TEXT,
        is_demo_data INTEGER DEFAULT 0
    );
    """)

    # Detection Bounding Boxes Details Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT NOT NULL,
        class_id INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        confidence REAL NOT NULL,
        box_x1 REAL NOT NULL,
        box_y1 REAL NOT NULL,
        box_x2 REAL NOT NULL,
        box_y2 REAL NOT NULL,
        area_ratio REAL NOT NULL,
        FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
    );
    """)

    # Status Audit History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT NOT NULL,
        previous_status TEXT,
        new_status TEXT NOT NULL,
        changed_by TEXT NOT NULL,
        comments TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
    );
    """)

    # Indices for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_priority ON reports(priority_score DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_detections_report ON detections(report_id);")

    conn.commit()

    # Seed Default Users if none exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pwd_hash, _ = hash_password("admin123")
        citizen_pwd_hash, _ = hash_password("citizen123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?), (?, ?, ?, ?)
        """, (
            "admin", admin_pwd_hash, "Municipal Road Engineer (Admin)", "authority",
            "citizen", citizen_pwd_hash, "Citizen Reporter", "citizen"
        ))
        conn.commit()

    conn.close()

def create_user(username: str, password: str, full_name: str, role: str = "citizen") -> bool:
    """Creates a new user with hashed password."""
    conn = get_connection()
    try:
        pwd_hash, _ = hash_password(password)
        conn.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, (username.strip().lower(), pwd_hash, full_name.strip(), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates credentials against stored password hashes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, full_name, role FROM users WHERE username = ?", (username.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    if row and verify_password(password, row["password_hash"]):
        return {
            "id": row["id"],
            "username": row["username"],
            "full_name": row["full_name"],
            "role": row["role"]
        }
    return None

def add_report(report_data: Dict[str, Any], detections: List[Dict[str, Any]]) -> str:
    """Inserts a new damage report and its child detections."""
    conn = get_connection()
    cursor = conn.cursor()

    report_id = report_data["id"]
    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO reports (
            id, created_at, updated_at, damage_type, primary_class,
            detection_count, max_confidence, avg_confidence,
            priority_score, priority_band, urgency_level,
            latitude, longitude, location_address, location_source,
            road_type, traffic_volume, weather_condition,
            original_image_path, annotated_image_path,
            status, reporter_name, reporter_role, notes, score_breakdown_json, is_demo_data
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?, ?, ?
        )
    """, (
        report_id,
        report_data.get("created_at", now),
        now,
        report_data.get("damage_type", "Unknown"),
        report_data.get("primary_class", "General Defect"),
        report_data.get("detection_count", 0),
        report_data.get("max_confidence", 0.0),
        report_data.get("avg_confidence", 0.0),
        report_data.get("priority_score", 0.0),
        report_data.get("priority_band", "LOW"),
        report_data.get("urgency_level", "Routine Monitoring"),
        report_data.get("latitude"),
        report_data.get("longitude"),
        report_data.get("location_address", "Location not specified"),
        report_data.get("location_source", "Not Provided"),
        report_data.get("road_type", "Arterial / Main City Road"),
        report_data.get("traffic_volume", "Moderate"),
        report_data.get("weather_condition", "Dry / Clear"),
        report_data.get("original_image_path", ""),
        report_data.get("annotated_image_path", ""),
        report_data.get("status", "New"),
        report_data.get("reporter_name", "Citizen Reporter"),
        report_data.get("reporter_role", "citizen"),
        report_data.get("notes", ""),
        json.dumps(report_data.get("score_breakdown", {})),
        1 if report_data.get("is_demo_data") else 0
    ))

    # Insert individual detections
    for det in detections:
        cursor.execute("""
            INSERT INTO detections (
                report_id, class_id, class_name, confidence,
                box_x1, box_y1, box_x2, box_y2, area_ratio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            det.get("class_id", 0),
            det.get("class_name", "Damage"),
            det.get("confidence", 0.0),
            det.get("box_x1", 0.0),
            det.get("box_y1", 0.0),
            det.get("box_x2", 0.0),
            det.get("box_y2", 0.0),
            det.get("area_ratio", 0.0)
        ))

    # Initial status history entry
    cursor.execute("""
        INSERT INTO status_history (report_id, previous_status, new_status, changed_by, comments, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        report_id,
        None,
        report_data.get("status", "New"),
        report_data.get("reporter_name", "System"),
        "Report created and registered in database",
        now
    ))

    conn.commit()
    conn.close()
    return report_id

def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full report details including detections and history."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    report = dict(row)
    if report.get("score_breakdown_json"):
        try:
            report["score_breakdown"] = json.loads(report["score_breakdown_json"])
        except Exception:
            report["score_breakdown"] = {}
    else:
        report["score_breakdown"] = {}

    # Detections
    cursor.execute("SELECT * FROM detections WHERE report_id = ?", (report_id,))
    report["detections"] = [dict(d) for d in cursor.fetchall()]

    # History
    cursor.execute("SELECT * FROM status_history WHERE report_id = ? ORDER BY timestamp DESC", (report_id,))
    report["history"] = [dict(h) for h in cursor.fetchall()]

    conn.close()
    return report

def get_all_reports(limit: int = 500) -> List[Dict[str, Any]]:
    """Returns all reports sorted by created_at DESC."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_filtered_reports(
    damage_type: Optional[str] = None,
    priority_band: Optional[str] = None,
    status: Optional[str] = None,
    search_query: Optional[str] = None,
    sort_by: str = "date_desc"
) -> List[Dict[str, Any]]:
    """Retrieves reports based on user filter criteria."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM reports WHERE 1=1"
    params: List[Any] = []

    if damage_type and damage_type != "All":
        query += " AND (damage_type LIKE ? OR primary_class LIKE ?)"
        params.extend([f"%{damage_type}%", f"%{damage_type}%"])

    if priority_band and priority_band != "All":
        query += " AND priority_band = ?"
        params.append(priority_band)

    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    if search_query and search_query.strip():
        term = f"%{search_query.strip()}%"
        query += " AND (id LIKE ? OR location_address LIKE ? OR notes LIKE ? OR primary_class LIKE ?)"
        params.extend([term, term, term, term])

    # Sorting
    if sort_by == "priority_desc":
        query += " ORDER BY priority_score DESC, created_at DESC"
    elif sort_by == "priority_asc":
        query += " ORDER BY priority_score ASC, created_at DESC"
    elif sort_by == "date_asc":
        query += " ORDER BY created_at ASC"
    else:  # date_desc
        query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def update_report_status(report_id: str, new_status: str, changed_by: str, comments: str = "") -> bool:
    """Updates a report's lifecycle status and logs the audit event."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    old_status = row["status"]
    now = datetime.now().isoformat()

    cursor.execute("""
        UPDATE reports
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (new_status, now, report_id))

    cursor.execute("""
        INSERT INTO status_history (report_id, previous_status, new_status, changed_by, comments, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (report_id, old_status, new_status, changed_by, comments, now))

    conn.commit()
    conn.close()
    return True

def delete_report(report_id: str) -> bool:
    """Deletes a report and associated file references."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT original_image_path, annotated_image_path FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    # Attempt to remove images if they exist
    for p in [row["original_image_path"], row["annotated_image_path"]]:
        if p and Path(p).exists():
            try:
                Path(p).unlink()
            except Exception:
                pass

    cursor.execute("DELETE FROM detections WHERE report_id = ?", (report_id,))
    cursor.execute("DELETE FROM status_history WHERE report_id = ?", (report_id,))
    cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))

    conn.commit()
    conn.close()
    return True

def get_dashboard_stats() -> Dict[str, Any]:
    """Computes real-time aggregated metrics from database records."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM reports")
    total_reports = cursor.fetchone()[0]

    if total_reports == 0:
        conn.close()
        return {
            "total_reports": 0,
            "total_potholes": 0,
            "total_cracks": 0,
            "high_priority_count": 0,
            "awaiting_inspection": 0,
            "marked_repaired": 0,
            "avg_priority_score": 0.0,
            "resolved_count": 0
        }

    cursor.execute("SELECT COUNT(*) FROM reports WHERE damage_type LIKE '%Pothole%' OR primary_class LIKE '%Pothole%'")
    potholes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE damage_type LIKE '%Crack%' OR primary_class LIKE '%Crack%'")
    cracks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE priority_band = 'HIGH'")
    high_priority = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE status IN ('New', 'Under Review', 'Inspection Scheduled')")
    awaiting_inspection = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE status = 'Resolved'")
    repaired = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(priority_score) FROM reports")
    avg_score = cursor.fetchone()[0] or 0.0

    conn.close()

    return {
        "total_reports": total_reports,
        "total_potholes": potholes,
        "total_cracks": cracks,
        "high_priority_count": high_priority,
        "awaiting_inspection": awaiting_inspection,
        "marked_repaired": repaired,
        "avg_priority_score": round(float(avg_score), 1),
        "resolved_count": repaired
    }

def get_recent_reports(limit: int = 10) -> List[Dict[str, Any]]:
    """Returns the most recent reports for dashboard widgets."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, damage_type, location_address, priority_score, priority_band, status, created_at, is_demo_data
        FROM reports
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def seed_demo_data_if_empty():
    """Seeds realistic municipal sample reports clearly marked as demo/sample data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reports")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    sample_reports = [
        {
            "id": "RGD-2026-0101",
            "damage_type": "Pothole",
            "primary_class": "Pothole",
            "detection_count": 2,
            "max_confidence": 0.91,
            "avg_confidence": 0.88,
            "priority_score": 88.5,
            "priority_band": "HIGH",
            "urgency_level": "Immediate Action Required",
            "latitude": 28.6129,
            "longitude": 77.2295,
            "location_address": "Near India Gate Roundabout, Rajpath Sector",
            "location_source": "Device GPS",
            "road_type": "Arterial / Main City Road",
            "traffic_volume": "Heavy (Trucks / Public Transit)",
            "weather_condition": "Dry / Clear",
            "original_image_path": "",
            "annotated_image_path": "",
            "status": "Inspection Scheduled",
            "reporter_name": "Field Officer Sharma",
            "reporter_role": "authority",
            "notes": "Severe deep crater on outer ring lane causing vehicle deceleration. Marked as demo record.",
            "is_demo_data": 1,
            "score_breakdown": {
                "class_severity_points": 35.0,
                "area_points": 24.5,
                "count_points": 12.0,
                "confidence_points": 9.0,
                "context_multiplier": 1.15
            }
        },
        {
            "id": "RGD-2026-0102",
            "damage_type": "Alligator Crack",
            "primary_class": "Alligator Crack",
            "detection_count": 3,
            "max_confidence": 0.84,
            "avg_confidence": 0.79,
            "priority_score": 74.0,
            "priority_band": "HIGH",
            "urgency_level": "Immediate Action Required",
            "latitude": 28.6315,
            "longitude": 77.2167,
            "location_address": "Outer Connaught Circus, Lane 4",
            "location_source": "Manual Coords",
            "road_type": "Arterial / Main City Road",
            "traffic_volume": "Heavy (Trucks / Public Transit)",
            "weather_condition": "Dry / Clear",
            "original_image_path": "",
            "annotated_image_path": "",
            "status": "Repair in Progress",
            "reporter_name": "Citizen Patrol",
            "reporter_role": "citizen",
            "notes": "Extensive structural alligator pattern across right carriageway. Marked as demo record.",
            "is_demo_data": 1,
            "score_breakdown": {
                "class_severity_points": 30.0,
                "area_points": 22.0,
                "count_points": 14.0,
                "confidence_points": 8.0,
                "context_multiplier": 1.15
            }
        },
        {
            "id": "RGD-2026-0103",
            "damage_type": "Longitudinal Crack",
            "primary_class": "Longitudinal Crack",
            "detection_count": 1,
            "max_confidence": 0.76,
            "avg_confidence": 0.76,
            "priority_score": 48.0,
            "priority_band": "MEDIUM",
            "urgency_level": "Scheduled Maintenance",
            "latitude": 28.5983,
            "longitude": 77.1895,
            "location_address": "Chanakyapuri Avenue, Shantipath",
            "location_source": "Device GPS",
            "road_type": "Residential / Suburb Street",
            "traffic_volume": "Moderate",
            "weather_condition": "Dry / Clear",
            "original_image_path": "",
            "annotated_image_path": "",
            "status": "Under Review",
            "reporter_name": "Civic Watcher Alex",
            "reporter_role": "citizen",
            "notes": "Long center crack along joint boundary, no loose aggregate yet.",
            "is_demo_data": 1,
            "score_breakdown": {
                "class_severity_points": 20.0,
                "area_points": 14.0,
                "count_points": 6.0,
                "confidence_points": 8.0,
                "context_multiplier": 1.0
            }
        },
        {
            "id": "RGD-2026-0104",
            "damage_type": "Transverse Crack",
            "primary_class": "Transverse Crack",
            "detection_count": 1,
            "max_confidence": 0.72,
            "avg_confidence": 0.72,
            "priority_score": 32.5,
            "priority_band": "LOW",
            "urgency_level": "Routine Monitoring",
            "latitude": 28.5355,
            "longitude": 77.2600,
            "location_address": "Jasola Vihar Pocket 9 Service Road",
            "location_source": "Map Pin",
            "road_type": "Rural / Service Road",
            "traffic_volume": "Low / Local Access Only",
            "weather_condition": "Dry / Clear",
            "original_image_path": "",
            "annotated_image_path": "",
            "status": "Resolved",
            "reporter_name": "PWD Inspector Verma",
            "reporter_role": "authority",
            "notes": "Crack filled with polymer modified bitumen emulsion on Nov 20, 2026.",
            "is_demo_data": 1,
            "score_breakdown": {
                "class_severity_points": 15.0,
                "area_points": 10.0,
                "count_points": 4.0,
                "confidence_points": 7.0,
                "context_multiplier": 0.85
            }
        },
        {
            "id": "RGD-2026-0105",
            "damage_type": "Pothole",
            "primary_class": "Pothole",
            "detection_count": 1,
            "max_confidence": 0.94,
            "avg_confidence": 0.94,
            "priority_score": 82.0,
            "priority_band": "HIGH",
            "urgency_level": "Immediate Action Required",
            "latitude": 28.5700,
            "longitude": 77.2400,
            "location_address": "Ring Road Flyover Descent, Lajpat Nagar",
            "location_source": "Device GPS",
            "road_type": "Highway / Expressway",
            "traffic_volume": "Heavy (Trucks / Public Transit)",
            "weather_condition": "Wet / Rainy",
            "original_image_path": "",
            "annotated_image_path": "",
            "status": "New",
            "reporter_name": "Commuter Rahul",
            "reporter_role": "citizen",
            "notes": "Sharp edges near descent curve, high collision hazard.",
            "is_demo_data": 1,
            "score_breakdown": {
                "class_severity_points": 35.0,
                "area_points": 21.0,
                "count_points": 8.0,
                "confidence_points": 9.5,
                "context_multiplier": 1.25
            }
        }
    ]

    for s in sample_reports:
        add_report(s, [
            {
                "class_id": 0 if "Pothole" in s["primary_class"] else 1,
                "class_name": s["primary_class"],
                "confidence": s["max_confidence"],
                "box_x1": 0.2, "box_y1": 0.3, "box_x2": 0.6, "box_y2": 0.7,
                "area_ratio": 0.16
            }
        ])

    conn.close()
