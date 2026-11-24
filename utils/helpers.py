"""
ROADGUARD AI - Helper Functions
ID generators, timestamp formatters, CSV converters, and UI badge utilities.
"""

import random
import string
from datetime import datetime
from typing import List, Dict, Any, Optional
import io
import pandas as pd

from config import PRIORITY_BANDS, STATUS_COLORS

def generate_report_id() -> str:
    """Generates a standardized report ID, e.g. RGD-2026-4B8F."""
    year = datetime.now().year
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"RGD-{year}-{suffix}"

def format_datetime(iso_str: Optional[str] = None) -> str:
    """Formats ISO datetime string into user-friendly format."""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y - %H:%M")
    except Exception:
        return str(iso_str)

def get_priority_badge_html(priority_band: str, score: Optional[float] = None) -> str:
    """Generates modern colored HTML badge for priority."""
    band = priority_band.upper()
    info = PRIORITY_BANDS.get(band, PRIORITY_BANDS["LOW"])
    color = info["color"]
    score_str = f" ({score:.1f})" if score is not None else ""
    return (
        f'<span style="background-color: {color}22; color: {color}; '
        f'border: 1px solid {color}66; padding: 3px 10px; border-radius: 9999px; '
        f'font-size: 0.78rem; font-weight: 700; letter-spacing: 0.03em; display: inline-block;">'
        f'{band}{score_str}'
        f'</span>'
    )

def get_status_badge_html(status: str) -> str:
    """Generates modern colored HTML badge for status."""
    color = STATUS_COLORS.get(status, "#94A3B8")
    return (
        f'<span style="background-color: {color}20; color: {color}; '
        f'border: 1px solid {color}55; padding: 3px 10px; border-radius: 9999px; '
        f'font-size: 0.78rem; font-weight: 600; display: inline-block;">'
        f'{status}'
        f'</span>'
    )

def reports_to_csv_bytes(reports: List[Dict[str, Any]]) -> bytes:
    """Converts a list of report dictionaries to downloadable CSV bytes."""
    if not reports:
        return b"Report ID,Date,Damage Type,Priority Score,Status,Location\n"

    df = pd.DataFrame(reports)
    # Filter and reorder key fields
    cols_order = [
        "id", "created_at", "damage_type", "primary_class", "detection_count",
        "priority_score", "priority_band", "urgency_level", "status",
        "latitude", "longitude", "location_address", "location_source",
        "road_type", "traffic_volume", "weather_condition", "notes", "is_demo_data"
    ]
    present_cols = [c for c in cols_order if c in df.columns]
    remaining = [c for c in df.columns if c not in cols_order and not c.endswith("_json")]
    final_df = df[present_cols + remaining]

    csv_buffer = io.StringIO()
    final_df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")
