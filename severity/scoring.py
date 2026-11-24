"""
ROADGUARD AI - Visual Damage Severity & Priority Scoring Engine
Calculates transparent, explainable 0-100 visual priority scores
based on damage classification, pixel coverage ratio, cluster density,
AI confidence, and optional human-provided road context.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import math

from config import (
    PRIORITY_BANDS,
    SCORING_WEIGHTS,
    ROAD_TYPE_MODIFIERS,
    TRAFFIC_VOLUME_MODIFIERS
)

@dataclass
class PriorityAssessment:
    score: float                      # 0.0 to 100.0
    band: str                         # "LOW", "MEDIUM", "HIGH"
    label: str                        # "Low Priority", "Medium Priority", "High Priority"
    color: str                        # Hex color
    urgency: str                      # Recommended action timeline
    primary_category: str             # e.g., "Pothole", "Crack"
    factor_breakdown: Dict[str, Any]  # Granular points for each factor
    technical_disclaimer: str         # Clear engineering disclaimer

def get_class_base_severity(class_name: str) -> float:
    """Returns baseline severity weight (0-50) for a damage category."""
    name_lower = class_name.lower()
    if "pothole" in name_lower:
        return 45.0
    elif "alligator" in name_lower:
        return 40.0
    elif "longitudinal" in name_lower:
        return 26.0
    elif "transverse" in name_lower:
        return 22.0
    elif "manhole" in name_lower:
        return 32.0
    elif "rutting" in name_lower or "depression" in name_lower:
        return 28.0
    else:
        return 25.0

def calculate_visual_priority_score(
    detections: List[Dict[str, Any]],
    road_type: str = "Arterial / Main City Road",
    traffic_volume: str = "Moderate",
    weather_condition: str = "Dry / Clear"
) -> PriorityAssessment:
    """
    Computes an explainable 0-100 visual priority score for an analyzed road image.
    
    Factors considered:
    1. Highest damage class severity (up to 40 pts)
    2. Damaged area percentage relative to image (up to 30 pts)
    3. Detection cluster density / count (up to 15 pts)
    4. Model detection confidence / certainty (up to 15 pts)
    5. Context modifier multiplier (0.8x to 1.35x)
    """
    disclaimer = (
        "IMPORTANT: This is an estimated visual priority score based on 2D surface imagery. "
        "A single 2D photo cannot measure structural sub-base integrity, pavement thickness, "
        "or true cavity depth. It is intended solely to guide and expedite human inspection triage."
    )

    if not detections:
        return PriorityAssessment(
            score=0.0,
            band="LOW",
            label="Low Priority",
            color="#10B981",
            urgency="No immediate visual hazard detected - Normal routine schedule",
            primary_category="None Detected",
            factor_breakdown={
                "class_points": 0.0,
                "area_points": 0.0,
                "count_points": 0.0,
                "confidence_points": 0.0,
                "context_multiplier": 1.0,
                "total_area_ratio_pct": 0.0,
                "raw_score": 0.0
            },
            technical_disclaimer=disclaimer
        )

    # 1. Class Severity Base Points (Max 38 pts)
    max_class_val = 0.0
    primary_category = "Road Defect"
    for det in detections:
        c_name = det.get("class_name", "Defect")
        base_val = get_class_base_severity(c_name)
        if base_val > max_class_val:
            max_class_val = base_val
            primary_category = c_name

    class_points = min(38.0, (max_class_val / 45.0) * 38.0)

    # 2. Damaged Area Ratio Points (Max 28 pts)
    # Total combined bounding box area relative to 1.0
    total_area_ratio = sum(float(det.get("area_ratio", 0.0)) for det in detections)
    # Clip to avoid double-counting overlapping boxes beyond 100%
    clamped_area_ratio = min(1.0, total_area_ratio)
    # 15% damaged area is already visually huge on a road surface photo
    area_points = min(28.0, (clamped_area_ratio / 0.20) * 28.0)

    # 3. Defect Count / Multiplicity Points (Max 18 pts)
    count = len(detections)
    if count == 1:
        count_points = 6.0
    elif count == 2:
        count_points = 11.0
    elif count <= 4:
        count_points = 15.0
    else:
        count_points = 18.0

    # 4. Model Confidence Certainty (Max 16 pts)
    avg_conf = sum(float(det.get("confidence", 0.5)) for det in detections) / max(1, count)
    confidence_points = avg_conf * 16.0

    # Raw Subtotal before context
    raw_subtotal = class_points + area_points + count_points + confidence_points

    # 5. Context Modifiers
    road_mult = ROAD_TYPE_MODIFIERS.get(road_type, 1.0)
    traffic_mult = TRAFFIC_VOLUME_MODIFIERS.get(traffic_volume, 1.0)
    weather_mult = 1.15 if "wet" in weather_condition.lower() or "rain" in weather_condition.lower() else 1.0

    combined_context_mult = (road_mult * 0.45) + (traffic_mult * 0.40) + (weather_mult * 0.15)

    # Apply context multiplier and constrain to [0.0, 100.0]
    final_score = round(min(100.0, max(5.0, raw_subtotal * combined_context_mult)), 1)

    # Determine Priority Band
    if final_score >= 70.0:
        band = "HIGH"
        urgency = "High Urgency: Schedule physical inspection within 24-48 hours"
    elif final_score >= 40.0:
        band = "MEDIUM"
        urgency = "Moderate Urgency: Include in upcoming weekly maintenance cycle"
    else:
        band = "LOW"
        urgency = "Low Urgency: Flag for standard quarterly road monitoring"

    band_info = PRIORITY_BANDS[band]

    breakdown = {
        "class_points": round(class_points, 1),
        "area_points": round(area_points, 1),
        "count_points": round(count_points, 1),
        "confidence_points": round(confidence_points, 1),
        "raw_subtotal": round(raw_subtotal, 1),
        "road_multiplier": road_mult,
        "traffic_multiplier": traffic_mult,
        "weather_multiplier": weather_mult,
        "combined_context_multiplier": round(combined_context_mult, 2),
        "total_area_ratio_pct": round(clamped_area_ratio * 100.0, 2),
        "detection_count": count,
        "avg_confidence_pct": round(avg_conf * 100.0, 1)
    }

    return PriorityAssessment(
        score=final_score,
        band=band,
        label=band_info["label"],
        color=band_info["color"],
        urgency=urgency,
        primary_category=primary_category,
        factor_breakdown=breakdown,
        technical_disclaimer=disclaimer
    )
