"""
ROADGUARD AI - Image Processing Utilities
Handles safe image validation, EXIF GPS coordinate extraction,
file persistence, and image transformations.
"""

import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
import io
import base64
from PIL import Image, ExifTags

from config import UPLOADS_DIR, OUTPUTS_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

def validate_uploaded_image(uploaded_file) -> Tuple[bool, str]:
    """
    Validates uploaded file against size limits, file extensions,
    and checks for image corruption.
    """
    if uploaded_file is None:
        return False, "No file uploaded."

    # Check size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB (Uploaded: {file_size_mb:.1f}MB)."

    # Check extension
    filename = uploaded_file.name.lower()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported format (.{ext}). Allowed formats: {', '.join(ALLOWED_EXTENSIONS).upper()}."

    # Validate image bytes
    try:
        image_bytes = uploaded_file.getvalue()
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # Verifies file integrity
    except Exception as e:
        return False, f"Corrupted or invalid image file: {str(e)}"

    return True, "Valid"

def extract_exif_gps(image_bytes: bytes) -> Optional[Tuple[float, float]]:
    """
    Extracts latitude and longitude from photo EXIF metadata if present.
    Returns (lat, lon) in decimal degrees or None.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_raw = img._getexif()
        if not exif_raw:
            return None

        gps_info = {}
        for tag_id, value in exif_raw.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if tag_name == "GPSInfo":
                for gps_tag_id, gps_val in value.items():
                    gps_tag_name = ExifTags.GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag_name] = gps_val

        if not gps_info:
            return None

        def _convert_to_degrees(value):
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)

        lat = None
        lon = None

        if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info:
            lat = _convert_to_degrees(gps_info["GPSLatitude"])
            if gps_info["GPSLatitudeRef"] != "N":
                lat = -lat

        if "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
            lon = _convert_to_degrees(gps_info["GPSLongitude"])
            if gps_info["GPSLongitudeRef"] != "E":
                lon = -lon

        if lat is not None and lon is not None:
            # Validate valid lat/lon ranges
            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                return round(lat, 6), round(lon, 6)

    except Exception:
        pass
    return None

def save_image_to_disk(
    image: Image.Image,
    report_id: str,
    category: str = "orig"
) -> str:
    """
    Saves image to uploads or outputs directory with a safe timestamped filename.
    Returns absolute file path as string.
    """
    target_dir = UPLOADS_DIR if category == "orig" else OUTPUTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    date_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_id = "".join(c for c in report_id if c.isalnum() or c in ("-", "_"))
    filename = f"{date_prefix}_{clean_id}_{category}.jpg"
    dest_path = target_dir / filename

    # Save as high-quality JPEG
    rgb_img = image.convert("RGB")
    rgb_img.save(dest_path, "JPEG", quality=90)
    return str(dest_path)

def image_to_base64(image: Image.Image) -> str:
    """Converts a PIL image to a base64 string for embedding."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
