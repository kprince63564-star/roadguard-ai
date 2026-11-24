"""
ROADGUARD AI - User Tutorial & Walkthrough Video Generator
Generates a high-definition 720p 30fps user walkthrough video (.mp4) explaining
how to use the app step-by-step: Capture/Upload, AI Detection, Map Pinning,
Priority Scoring, Database Tracking, GIS Telemetry, and PDF Export.
"""

import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from config import BASE_DIR, ASSETS_DIR, OUTPUTS_DIR

# Video parameters
WIDTH = 1280
HEIGHT = 720
FPS = 30
TOTAL_SECONDS = 72
TOTAL_FRAMES = TOTAL_SECONDS * FPS
OUTPUT_FILE = OUTPUTS_DIR / "roadguard_tutorial.mp4"

# Color Palette (Obsidian Charcoal & Safety Amber)
BG_COLOR = (12, 14, 18)             # #0C0E12 Obsidian
CARD_BG = (20, 23, 30)              # #14171E Slate Card
CARD_BORDER = (37, 41, 51)          # #252933 Border
AMBER = (249, 115, 22)              # #F97316 Safety Orange
GOLD = (245, 158, 11)               # #F59E0B Warm Amber
GREEN = (16, 185, 129)              # #10B981 Emerald
RED = (239, 68, 68)                 # #EF4444 Crimson
WHITE = (248, 250, 252)             # #F8FAFC Text
MUTED = (161, 161, 170)             # #A1A1AA Text
DARK_TEXT = (15, 23, 42)

# Load System Fonts
try:
    FONT_TITLE_XL = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46)
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)
    FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 19)
    FONT_BODY_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 19)
    FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    FONT_SMALL_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
    FONT_TAG = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
except Exception:
    FONT_TITLE_XL = ImageFont.load_default()
    FONT_TITLE = ImageFont.load_default()
    FONT_SUBTITLE = ImageFont.load_default()
    FONT_BODY = ImageFont.load_default()
    FONT_BODY_BOLD = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
    FONT_SMALL_BOLD = ImageFont.load_default()
    FONT_TAG = ImageFont.load_default()

# Load Media Assets
LOGO_IMG = None
logo_path = ASSETS_DIR / "logo.png"
if logo_path.exists():
    LOGO_IMG = Image.open(logo_path).convert("RGBA")

ROAD_IMG = None
road_path = ASSETS_DIR / "sample_road.jpg"
if road_path.exists():
    ROAD_IMG = Image.open(road_path).convert("RGB")

def create_base_frame(step_title: str, step_num: str, progress_ratio: float) -> Image.Image:
    """Draws technical background, header ribbon, and progress timeline."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Subtle background dot grid
    for x in range(30, WIDTH, 50):
        for y in range(40, HEIGHT - 20, 50):
            draw.point((x, y), fill=(26, 30, 39))

    # Top Brand Ribbon
    draw.line([(0, 48), (WIDTH, 48)], fill=(37, 41, 51), width=1)
    if LOGO_IMG:
        logo_mini = LOGO_IMG.resize((28, 28))
        img.paste(logo_mini, (24, 10), mask=logo_mini)
    draw.text((60, 14), "ROADGUARD AI", fill=AMBER, font=FONT_SMALL_BOLD)
    draw.text((195, 15), "|  App User Tutorial & Walkthrough Guide (एप उपयोग गाइड)", fill=MUTED, font=FONT_SMALL)

    # Step Pill on top right
    pill_text = f"TUTORIAL: {step_num.upper()}"
    bbox = draw.textbbox((0, 0), pill_text, font=FONT_TAG)
    pill_w = bbox[2] - bbox[0] + 18
    draw.rounded_rectangle([WIDTH - pill_w - 24, 12, WIDTH - 24, 36], radius=5, fill=(24, 27, 35), outline=AMBER, width=1)
    draw.text((WIDTH - pill_w - 15, 16), pill_text, fill=(255, 160, 87), font=FONT_TAG)

    # Bottom Progress Bar
    bar_y = HEIGHT - 8
    draw.rectangle([0, bar_y, WIDTH, HEIGHT], fill=(20, 23, 30))
    active_w = int(WIDTH * progress_ratio)
    if active_w > 0:
        draw.rectangle([0, bar_y, active_w, HEIGHT], fill=AMBER)

    return img

def render_scene_1(progress: float) -> Image.Image:
    """Scene 1: Tutorial Introduction."""
    img = create_base_frame("Introduction", "Overview", progress)
    draw = ImageDraw.Draw(img)

    # Main Center Card
    card_box = [180, 100, WIDTH - 180, HEIGHT - 80]
    draw.rounded_rectangle(card_box, radius=16, fill=CARD_BG, outline=CARD_BORDER, width=1)

    # Amber top accent bar on card
    draw.rounded_rectangle([180, 100, WIDTH - 180, 106], radius=3, fill=AMBER)

    if LOGO_IMG:
        logo_large = LOGO_IMG.resize((84, 84))
        img.paste(logo_large, (card_box[0] + 40, card_box[1] + 35), mask=logo_large)

    draw.text((card_box[0] + 145, card_box[1] + 35), "ROADGUARD AI", fill=WHITE, font=FONT_TITLE_XL)
    draw.text((card_box[0] + 145, card_box[1] + 90), "User Walkthrough & Operation Guide  •  उपयोग मार्गदर्शिका", fill=AMBER, font=FONT_SUBTITLE)

    draw.line([(card_box[0] + 40, card_box[1] + 145), (card_box[2] - 40, card_box[1] + 145)], fill=(37, 41, 51), width=1)

    desc_lines = [
        "Welcome! This quick tutorial shows how to use ROADGUARD AI to report road damage,",
        "localize potholes and cracks with AI, pin GPS coordinates, and track repair lifecycles.",
        "",
        "⚡ 3 Core Capabilities You Will Learn:",
        "  1. How to capture or upload road imagery directly from field devices.",
        "  2. How AI calculates an objective 0–100 civil engineering visual priority index.",
        "  3. How authorities and citizens monitor repair progress on interactive GIS maps."
    ]
    y_text = card_box[1] + 165
    for line in desc_lines:
        font = FONT_BODY_BOLD if line.startswith("⚡") else FONT_BODY
        color = GOLD if line.startswith("⚡") else (WHITE if line.startswith("  ") else MUTED)
        draw.text((card_box[0] + 40, y_text), line, fill=color, font=font)
        y_text += 32

    # Bottom Pill
    draw.rounded_rectangle([card_box[0] + 40, card_box[3] - 65, card_box[2] - 40, card_box[3] - 25], radius=8, fill=(28, 32, 42))
    draw.text((card_box[0] + 60, card_box[3] - 55), "⏱️ Duration: 70 Seconds  •  Works on Mobile, Tablet & Desktop  •  Hindi & English", fill=MUTED, font=FONT_SMALL)

    return img

def render_scene_2(progress: float) -> Image.Image:
    """Scene 2: Step 1 - Capture or Upload Road Imagery."""
    img = create_base_frame("Step 1", "Step 1 of 6", progress)
    draw = ImageDraw.Draw(img)

    # Left Column: Instructions
    left_box = [80, 90, 580, HEIGHT - 70]
    draw.rounded_rectangle(left_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.rounded_rectangle([left_box[0], left_box[1], left_box[0] + 6, left_box[3]], radius=3, fill=AMBER)

    draw.text((left_box[0] + 30, left_box[1] + 25), "STEP 1: CAPTURE OR UPLOAD", fill=AMBER, font=FONT_TAG)
    draw.text((left_box[0] + 30, left_box[1] + 45), "Input Road Surface Photo", fill=WHITE, font=FONT_TITLE)
    draw.text((left_box[0] + 30, left_box[1] + 90), "सड़क की तस्वीर लें या अपलोड करें", fill=MUTED, font=FONT_SMALL)

    draw.line([(left_box[0] + 30, left_box[1] + 115), (left_box[2] - 30, left_box[1] + 115)], fill=(37, 41, 51), width=1)

    steps = [
        ("📁 Upload Image File", "Select JPG, JPEG, or PNG photos from your computer or smartphone."),
        ("📸 Device Camera Capture", "Use your phone or inspection vehicle camera directly on site."),
        ("⚡ Sample Road Photo", "Click 'Load Sample Road Image' to test without taking a new photo."),
        ("🛰️ Automatic EXIF GPS", "If your camera geotags photos, coordinates are extracted automatically!")
    ]
    y_pos = left_box[1] + 135
    for title, desc in steps:
        draw.text((left_box[0] + 30, y_pos), title, fill=WHITE, font=FONT_BODY_BOLD)
        draw.text((left_box[0] + 30, y_pos + 26), desc, fill=MUTED, font=FONT_SMALL)
        y_pos += 80

    # Right Column: Visual Preview Card
    right_box = [620, 90, WIDTH - 80, HEIGHT - 70]
    draw.rounded_rectangle(right_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)

    if ROAD_IMG:
        road_scaled = ROAD_IMG.resize((right_box[2] - right_box[0] - 40, 360))
        img.paste(road_scaled, (right_box[0] + 20, right_box[1] + 20))
        # Draw camera viewfinder crosshairs
        draw.line([(right_box[0] + 40, right_box[1] + 40), (right_box[0] + 70, right_box[1] + 40)], fill=AMBER, width=3)
        draw.line([(right_box[0] + 40, right_box[1] + 40), (right_box[0] + 40, right_box[1] + 70)], fill=AMBER, width=3)
        draw.line([(right_box[2] - 40, right_box[1] + 40), (right_box[2] - 70, right_box[1] + 40)], fill=AMBER, width=3)
        draw.line([(right_box[2] - 40, right_box[1] + 40), (right_box[2] - 40, right_box[1] + 70)], fill=AMBER, width=3)

    draw.rounded_rectangle([right_box[0] + 20, right_box[1] + 400, right_box[2] - 20, right_box[3] - 20], radius=10, fill=(24, 28, 38))
    draw.text((right_box[0] + 40, right_box[1] + 420), "💡 Pro Tip:", fill=GOLD, font=FONT_SMALL_BOLD)
    draw.text((right_box[0] + 120, right_box[1] + 420), "High-angle daytime shots with good asphalt visibility yield highest AI accuracy.", fill=WHITE, font=FONT_SMALL)

    return img

def render_scene_3(progress: float) -> Image.Image:
    """Scene 3: Step 2 - AI Road Damage Detection."""
    img = create_base_frame("Step 2", "Step 2 of 6", progress)
    draw = ImageDraw.Draw(img)

    left_box = [80, 90, 580, HEIGHT - 70]
    draw.rounded_rectangle(left_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.rounded_rectangle([left_box[0], left_box[1], left_box[0] + 6, left_box[3]], radius=3, fill=AMBER)

    draw.text((left_box[0] + 30, left_box[1] + 25), "STEP 2: AI DETECTION", fill=AMBER, font=FONT_TAG)
    draw.text((left_box[0] + 30, left_box[1] + 45), "Ultralytics YOLO Vision", fill=WHITE, font=FONT_TITLE)
    draw.text((left_box[0] + 30, left_box[1] + 90), "गड्ढों और दरारों की स्वचालित पहचान", fill=MUTED, font=FONT_SMALL)

    draw.line([(left_box[0] + 30, left_box[1] + 115), (left_box[2] - 30, left_box[1] + 115)], fill=(37, 41, 51), width=1)

    bullets = [
        ("🚀 Tap 'Analyze Road Damage'", "Click the primary action button to run computer vision inference."),
        ("🎯 Multi-Defect Localization", "Detects Potholes, Alligator Cracks, Transverse Cracks, and Rutting."),
        ("📊 Bounding Boxes & Confidence", "Visual boxes display class labels and percentage confidence (e.g. 91%)."),
        ("⚖️ Side-by-Side Comparison", "Inspect original vs. annotated view with detected area ratios.")
    ]
    y_pos = left_box[1] + 135
    for t_text, d_text in bullets:
        draw.text((left_box[0] + 30, y_pos), t_text, fill=WHITE, font=FONT_BODY_BOLD)
        draw.text((left_box[0] + 30, y_pos + 26), d_text, fill=MUTED, font=FONT_SMALL)
        y_pos += 80

    # Right Column: Visual Simulated Detection Overlay
    right_box = [620, 90, WIDTH - 80, HEIGHT - 70]
    draw.rounded_rectangle(right_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)

    if ROAD_IMG:
        road_scaled = ROAD_IMG.resize((right_box[2] - right_box[0] - 40, 360))
        img.paste(road_scaled, (right_box[0] + 20, right_box[1] + 20))

        # Draw AI Bounding Boxes on simulated image
        # Box 1: Pothole
        bx1 = right_box[0] + 100
        by1 = right_box[1] + 120
        bx2 = bx1 + 220
        by2 = by1 + 160
        draw.rectangle([bx1, by1, bx2, by2], outline=RED, width=3)
        draw.rectangle([bx1, by1 - 24, bx1 + 150, by1], fill=RED)
        draw.text((bx1 + 8, by1 - 20), "Pothole: 91.4%", fill=WHITE, font=FONT_SMALL_BOLD)

        # Box 2: Alligator Crack
        cx1 = right_box[0] + 360
        cy1 = right_box[1] + 80
        cx2 = cx1 + 180
        cy2 = cy1 + 190
        draw.rectangle([cx1, cy1, cx2, cy2], outline=AMBER, width=3)
        draw.rectangle([cx1, cy1 - 24, cx1 + 175, cy1], fill=AMBER)
        draw.text((cx1 + 8, cy1 - 20), "Alligator Crack: 84.2%", fill=DARK_TEXT, font=FONT_SMALL_BOLD)

    # Detection Stat Pills
    draw.rounded_rectangle([right_box[0] + 20, right_box[1] + 400, right_box[0] + 280, right_box[3] - 20], radius=8, fill=(35, 18, 20), outline=RED, width=1)
    draw.text((right_box[0] + 35, right_box[1] + 415), "DETECTED DEFECTS: 2 REGIONS", fill=RED, font=FONT_SMALL_BOLD)
    draw.text((right_box[0] + 35, right_box[1] + 440), "Primary: Severe Asphalt Cavity", fill=MUTED, font=FONT_TAG)

    draw.rounded_rectangle([right_box[0] + 300, right_box[1] + 400, right_box[2] - 20, right_box[3] - 20], radius=8, fill=(30, 24, 18), outline=AMBER, width=1)
    draw.text((right_box[0] + 315, right_box[1] + 415), "AI INFERENCE LATENCY: 42ms", fill=AMBER, font=FONT_SMALL_BOLD)
    draw.text((right_box[0] + 315, right_box[1] + 440), "YOLOv8 Real-Time Processing", fill=MUTED, font=FONT_TAG)

    return img

def render_scene_4(progress: float) -> Image.Image:
    """Scene 4: Step 3 - Interactive Map Pinning & Location."""
    img = create_base_frame("Step 3", "Step 3 of 6", progress)
    draw = ImageDraw.Draw(img)

    left_box = [80, 90, 580, HEIGHT - 70]
    draw.rounded_rectangle(left_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.rounded_rectangle([left_box[0], left_box[1], left_box[0] + 6, left_box[3]], radius=3, fill=AMBER)

    draw.text((left_box[0] + 30, left_box[1] + 25), "STEP 3: LOCATION PINNING", fill=AMBER, font=FONT_TAG)
    draw.text((left_box[0] + 30, left_box[1] + 45), "Geospatial GIS Pinning", fill=WHITE, font=FONT_TITLE)
    draw.text((left_box[0] + 30, left_box[1] + 90), "सटीक स्थान चयन और जीपीएस मैपिंग", fill=MUTED, font=FONT_SMALL)

    draw.line([(left_box[0] + 30, left_box[1] + 115), (left_box[2] - 30, left_box[1] + 115)], fill=(37, 41, 51), width=1)

    points = [
        ("🗺️ Click Anywhere on Map", "Simply tap or click on the interactive Folium map to drop an incident pin."),
        ("⚡ Preset Location Shortcuts", "Quickly test major highway sectors (Delhi Ring Road, Western Express, etc.)."),
        ("📍 Street Address & Landmark", "Enter road name, milestone number, or cross-street landmark."),
        ("🛡️ Verified Origin Tagging", "Coordinates are labeled by source: Device GPS, Map Pin, or Manual.")
    ]
    y_pos = left_box[1] + 135
    for t_text, d_text in points:
        draw.text((left_box[0] + 30, y_pos), t_text, fill=WHITE, font=FONT_BODY_BOLD)
        draw.text((left_box[0] + 30, y_pos + 26), d_text, fill=MUTED, font=FONT_SMALL)
        y_pos += 80

    # Right Column: Visual Simulated Map Picker
    right_box = [620, 90, WIDTH - 80, HEIGHT - 70]
    draw.rounded_rectangle(right_box, radius=14, fill=(18, 20, 26), outline=CARD_BORDER, width=1)

    # Simulated Dark GIS Map Graphic
    map_box = [right_box[0] + 20, right_box[1] + 20, right_box[2] - 20, right_box[1] + 360]
    draw.rounded_rectangle(map_box, radius=10, fill=(10, 12, 16))

    # Road network simulation lines
    draw.line([(map_box[0] + 40, map_box[1] + 180), (map_box[2] - 40, map_box[1] + 180)], fill=(40, 45, 58), width=8)
    draw.line([(map_box[0] + 280, map_box[1] + 40), (map_box[0] + 280, map_box[3] - 40)], fill=(40, 45, 58), width=8)
    draw.line([(map_box[0] + 80, map_box[1] + 80), (map_box[2] - 80, map_box[3] - 80)], fill=(30, 35, 46), width=4)

    # Pin point at intersection
    pin_x = map_box[0] + 280
    pin_y = map_box[1] + 180
    # Radar pulse around pin
    draw.ellipse([pin_x - 30, pin_y - 30, pin_x + 30, pin_y + 30], outline=(249, 115, 22, 120), width=2)
    draw.ellipse([pin_x - 14, pin_y - 14, pin_x + 14, pin_y + 14], fill=AMBER)
    draw.ellipse([pin_x - 5, pin_y - 5, pin_x + 5, pin_y + 5], fill=WHITE)

    # Coordinate badge popup
    draw.rounded_rectangle([pin_x + 20, pin_y - 45, pin_x + 230, pin_y + 5], radius=6, fill=(24, 28, 38), outline=AMBER, width=1)
    draw.text((pin_x + 30, pin_y - 38), "Pinned Incident: 28.5700, 77.2400", fill=WHITE, font=FONT_SMALL_BOLD)
    draw.text((pin_x + 30, pin_y - 18), "Ring Road Corridor, Lajpat Nagar", fill=MUTED, font=FONT_TAG)

    # Bottom Coordinate Confirmation Box
    draw.rounded_rectangle([right_box[0] + 20, right_box[1] + 390, right_box[2] - 20, right_box[3] - 20], radius=8, fill=(24, 28, 38))
    draw.text((right_box[0] + 35, right_box[1] + 410), "CONFIRMED COORDINATES:", fill=GOLD, font=FONT_SMALL_BOLD)
    draw.text((right_box[0] + 35, right_box[1] + 435), "Latitude: 28.570000° N  |  Longitude: 77.240000° E  |  Source: Map Pin", fill=WHITE, font=FONT_SMALL)

    return img

def render_scene_5(progress: float) -> Image.Image:
    """Scene 5: Step 4 - Explainable Visual Priority Score."""
    img = create_base_frame("Step 4", "Step 4 of 6", progress)
    draw = ImageDraw.Draw(img)

    left_box = [80, 90, 580, HEIGHT - 70]
    draw.rounded_rectangle(left_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.rounded_rectangle([left_box[0], left_box[1], left_box[0] + 6, left_box[3]], radius=3, fill=AMBER)

    draw.text((left_box[0] + 30, left_box[1] + 25), "STEP 4: PRIORITY SCORING", fill=AMBER, font=FONT_TAG)
    draw.text((left_box[0] + 30, left_box[1] + 45), "Explainable 0–100 Triage", fill=WHITE, font=FONT_TITLE)
    draw.text((left_box[0] + 30, left_box[1] + 90), "पारदर्शी 0-100 प्राथमिकता सूचकांक", fill=MUTED, font=FONT_SMALL)

    draw.line([(left_box[0] + 30, left_box[1] + 115), (left_box[2] - 30, left_box[1] + 115)], fill=(37, 41, 51), width=1)

    breakdown = [
        ("⚖️ Defect Class Weight (35%)", "Potholes receive highest base hazard; surface cracks scaled accordingly."),
        ("📐 Damaged Surface Area (30%)", "Calculates pixel percentage of roadway damaged relative to entire frame."),
        ("🔢 Defect Region Multiplicity (15%)", "Multiple clustered potholes increase urgency multiplier."),
        ("🛣️ Road & Traffic Context (20%)", "Expressways & heavy truck corridors receive higher dispatch priority.")
    ]
    y_pos = left_box[1] + 135
    for t_text, d_text in breakdown:
        draw.text((left_box[0] + 30, y_pos), t_text, fill=WHITE, font=FONT_BODY_BOLD)
        draw.text((left_box[0] + 30, y_pos + 26), d_text, fill=MUTED, font=FONT_SMALL)
        y_pos += 80

    # Right Column: Priority Gauge Card
    right_box = [620, 90, WIDTH - 80, HEIGHT - 70]
    draw.rounded_rectangle(right_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)

    # Big Score Box
    score_card = [right_box[0] + 40, right_box[1] + 40, right_box[2] - 40, right_box[1] + 230]
    draw.rounded_rectangle(score_card, radius=12, fill=(28, 16, 18), outline=RED, width=2)

    draw.text((score_card[0] + 30, score_card[1] + 25), "HIGH PRIORITY HAZARD", fill=RED, font=FONT_BODY_BOLD)
    draw.text((score_card[0] + 30, score_card[1] + 55), "82.5", fill=RED, font=FONT_TITLE_XL)
    draw.text((score_card[0] + 160, score_card[1] + 75), "/ 100 Visual Index", fill=MUTED, font=FONT_SUBTITLE)
    draw.text((score_card[0] + 30, score_card[1] + 130), "Recommended Action: Immediate Inspection Within 24 Hours", fill=WHITE, font=FONT_BODY)
    draw.text((score_card[0] + 30, score_card[1] + 165), "High-speed vehicular hazard detected on Arterial Main Road.", fill=MUTED, font=FONT_SMALL)

    # 3 Priority Tier Indicators
    tiers = [
        ("0 - 39: LOW PRIORITY", GREEN, "Routine Maintenance / Monitor"),
        ("40 - 69: MEDIUM PRIORITY", GOLD, "Scheduled Repair Inspection"),
        ("70 - 100: HIGH PRIORITY", RED, "Urgent Public Safety Hazard")
    ]
    t_y = right_box[1] + 260
    for label, col, sub in tiers:
        draw.rounded_rectangle([right_box[0] + 40, t_y, right_box[2] - 40, t_y + 55], radius=8, fill=(20, 23, 30), outline=col, width=1)
        draw.text((right_box[0] + 60, t_y + 10), label, fill=col, font=FONT_SMALL_BOLD)
        draw.text((right_box[0] + 60, t_y + 30), sub, fill=MUTED, font=FONT_TAG)
        t_y += 65

    return img

def render_scene_6(progress: float) -> Image.Image:
    """Scene 6: Step 5 & 6 - Submit Report, Track Queue & GIS Map."""
    img = create_base_frame("Step 5 & 6", "Step 5 & 6 of 6", progress)
    draw = ImageDraw.Draw(img)

    left_box = [80, 90, 580, HEIGHT - 70]
    draw.rounded_rectangle(left_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.rounded_rectangle([left_box[0], left_box[1], left_box[0] + 6, left_box[3]], radius=3, fill=AMBER)

    draw.text((left_box[0] + 30, left_box[1] + 25), "STEP 5: SUBMIT & DISPATCH", fill=AMBER, font=FONT_TAG)
    draw.text((left_box[0] + 30, left_box[1] + 45), "Save & Track Lifecycle", fill=WHITE, font=FONT_TITLE)
    draw.text((left_box[0] + 30, left_box[1] + 90), "रिपोर्ट दर्ज करें और मरम्मत स्थिति ट्रैक करें", fill=MUTED, font=FONT_SMALL)

    draw.line([(left_box[0] + 30, left_box[1] + 115), (left_box[2] - 30, left_box[1] + 115)], fill=(37, 41, 51), width=1)

    steps_sub = [
        ("💾 One-Click Database Save", "Tap 'Save Official Road Damage Report' to assign tracking ID (RGD-2026-X)."),
        ("⚡ Maintenance Priority Queue", "Ranked triage table allows road engineers to dispatch repair trucks."),
        ("🔄 Real-Time Audit History", "Tracks: New ➔ Inspection Scheduled ➔ Repair in Progress ➔ Resolved."),
        ("🗺️ Live GIS Telemetry Map", "Every incident appears color-coded with photographic evidence popups.")
    ]
    y_pos = left_box[1] + 135
    for t_text, d_text in steps_sub:
        draw.text((left_box[0] + 30, y_pos), t_text, fill=WHITE, font=FONT_BODY_BOLD)
        draw.text((left_box[0] + 30, y_pos + 26), d_text, fill=MUTED, font=FONT_SMALL)
        y_pos += 80

    # Right Column: Step 7 - PDF Report Export
    right_box = [620, 90, WIDTH - 80, HEIGHT - 70]
    draw.rounded_rectangle(right_box, radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)

    draw.text((right_box[0] + 30, right_box[1] + 25), "STEP 7: COMPLIANT WORK ORDERS", fill=GREEN, font=FONT_TAG)
    draw.text((right_box[0] + 30, right_box[1] + 45), "Instant PDF Work Orders", fill=WHITE, font=FONT_TITLE)
    draw.text((right_box[0] + 30, right_box[1] + 90), "आधिकारिक रिपोर्टलैब पीडीएफ डाउनलोड", fill=MUTED, font=FONT_SMALL)

    draw.line([(right_box[0] + 30, right_box[1] + 115), (right_box[2] - 30, right_box[1] + 115)], fill=(37, 41, 51), width=1)

    # Simulated PDF Sheet Graphic
    pdf_box = [right_box[0] + 50, right_box[1] + 140, right_box[2] - 50, right_box[3] - 70]
    draw.rounded_rectangle(pdf_box, radius=8, fill=(245, 247, 250), outline=(200, 205, 215), width=2)

    # PDF Content Header
    draw.text((pdf_box[0] + 25, pdf_box[1] + 20), "ROADGUARD AI • MUNICIPAL WORK ORDER", fill=(15, 23, 42), font=FONT_SMALL_BOLD)
    draw.text((pdf_box[0] + 25, pdf_box[1] + 40), "INCIDENT ID: RGD-2026-4B8F  |  STATUS: DISPATCHED", fill=(71, 85, 105), font=FONT_TAG)
    draw.line([(pdf_box[0] + 25, pdf_box[1] + 65), (pdf_box[2] - 25, pdf_box[1] + 65)], fill=(203, 213, 225), width=1)

    draw.text((pdf_box[0] + 25, pdf_box[1] + 80), "DEFECT CLASSIFICATION: SEVERE ASPHALT POTHOLE", fill=(220, 38, 38), font=FONT_SMALL_BOLD)
    draw.text((pdf_box[0] + 25, pdf_box[1] + 105), "Location: Ring Road Corridor Flyover (28.5700, 77.2400)", fill=(30, 41, 59), font=FONT_TAG)
    draw.text((pdf_box[0] + 25, pdf_box[1] + 125), "Visual Priority Score: 82.5 / 100  (HIGH PRIORITY)", fill=(15, 23, 42), font=FONT_TAG)
    draw.text((pdf_box[0] + 25, pdf_box[1] + 145), "Assigned Contractor: PWD Rapid Patch Crew #04", fill=(30, 41, 59), font=FONT_TAG)

    # Stamp
    draw.rounded_rectangle([pdf_box[2] - 140, pdf_box[3] - 80, pdf_box[2] - 25, pdf_box[3] - 25], radius=6, outline=(220, 38, 38), width=2)
    draw.text((pdf_box[2] - 130, pdf_box[3] - 65), "APPROVED", fill=(220, 38, 38), font=FONT_SMALL_BOLD)
    draw.text((pdf_box[2] - 130, pdf_box[3] - 45), "CIVIL PWD", fill=(220, 38, 38), font=FONT_TAG)

    draw.text((right_box[0] + 60, right_box[3] - 40), "⬇️ Single-click PDF & CSV database exports available anytime in 'Generate Reports'.", fill=MUTED, font=FONT_TAG)

    return img

def render_scene_7(progress: float) -> Image.Image:
    """Scene 7: Summary & Ready to Use."""
    img = create_base_frame("Conclusion", "Ready", progress)
    draw = ImageDraw.Draw(img)

    card_box = [180, 100, WIDTH - 180, HEIGHT - 80]
    draw.rounded_rectangle(card_box, radius=16, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.rounded_rectangle([180, 100, WIDTH - 180, 106], radius=3, fill=GREEN)

    if LOGO_IMG:
        logo_large = LOGO_IMG.resize((84, 84))
        img.paste(logo_large, (card_box[0] + 40, card_box[1] + 35), mask=logo_large)

    draw.text((card_box[0] + 145, card_box[1] + 35), "You're Ready to Use ROADGUARD AI!", fill=WHITE, font=FONT_TITLE_XL)
    draw.text((card_box[0] + 145, card_box[1] + 90), "स्मार्ट और सुरक्षित सड़कों के निर्माण में सहयोग करें", fill=AMBER, font=FONT_SUBTITLE)

    draw.line([(card_box[0] + 40, card_box[1] + 145), (card_box[2] - 40, card_box[1] + 145)], fill=(37, 41, 51), width=1)

    recap = [
        "✅ 1. Navigate to 'Detect Road Damage' to upload your first road image.",
        "✅ 2. Choose between English and हिंदी in the sidebar at any time.",
        "✅ 3. Review AI bounding boxes and verify explainable priority scores.",
        "✅ 4. Track repairs on the Live GIS Map and Maintenance Queue.",
        "✅ 5. Generate official PDF work orders with photographic proof."
    ]
    y_text = card_box[1] + 175
    for item in recap:
        draw.text((card_box[0] + 40, y_text), item, fill=WHITE, font=FONT_BODY_BOLD)
        y_text += 45

    # Bottom Pill
    draw.rounded_rectangle([card_box[0] + 40, card_box[3] - 65, card_box[2] - 40, card_box[3] - 25], radius=8, fill=(18, 38, 28), outline=GREEN, width=1)
    draw.text((card_box[0] + 60, card_box[3] - 55), "🚀 Ready! Start inspecting road hazards right now in the Detect Road Damage tab.", fill=GREEN, font=FONT_BODY_BOLD)

    return img

def generate_user_tutorial_video():
    """Compiles all scenes into the 720p HD tutorial video file."""
    print(f"🎬 Starting User Tutorial Video Generation: {OUTPUT_FILE}")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(str(OUTPUT_FILE), fourcc, FPS, (WIDTH, HEIGHT))

    # Scene schedule (seconds per scene): Total = 72 seconds
    scenes = [
        (render_scene_1, 10),   # 0:00 - 0:10 (Introduction)
        (render_scene_2, 10),   # 0:10 - 0:20 (Step 1: Capture / Upload)
        (render_scene_3, 11),   # 0:20 - 0:31 (Step 2: AI Detection)
        (render_scene_4, 11),   # 0:31 - 0:42 (Step 3: Location Pinning)
        (render_scene_5, 11),   # 0:42 - 0:53 (Step 4: Priority Scoring)
        (render_scene_6, 11),   # 0:53 - 1:04 (Step 5, 6, 7: Submit & PDF)
        (render_scene_7, 9)     # 1:04 - 1:12 (Ready to Use)
    ]

    total_duration = sum(dur for _, dur in scenes)
    total_frames = total_duration * FPS
    current_frame = 0

    for scene_func, duration in scenes:
        scene_frames = duration * FPS
        for f in range(scene_frames):
            prog = current_frame / total_frames
            pil_frame = scene_func(prog)
            # Convert PIL RGB to OpenCV BGR
            cv_frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
            video_writer.write(cv_frame)
            current_frame += 1

    video_writer.release()
    print(f"✅ User Tutorial Video Successfully Generated: {OUTPUT_FILE} ({total_frames} frames, {total_duration}s)")
    return OUTPUT_FILE

if __name__ == "__main__":
    generate_user_tutorial_video()
