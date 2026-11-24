"""
ROADGUARD AI - Explainer Video Generator
Generates a high-definition 720p 30fps explainer video (.mp4) showcasing
ROADGUARD AI's architecture, YOLO vision pipeline, explainable scoring,
GIS mapping, maintenance queue, and automated reporting.
"""

import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

from config import BASE_DIR, ASSETS_DIR, OUTPUTS_DIR

# Video parameters
WIDTH = 1280
HEIGHT = 720
FPS = 30
TOTAL_SECONDS = 75
TOTAL_FRAMES = TOTAL_SECONDS * FPS
OUTPUT_FILE = OUTPUTS_DIR / "roadguard_explainer.mp4"

# Color Palette (Dark GovTech SaaS)
BG_COLOR = (11, 17, 32)            # #0B1120 Deep Navy
CARD_BG = (19, 30, 54)             # #131E36 Panel Navy
CARD_BORDER = (30, 41, 59)         # #1E293B Border
CYAN = (6, 182, 212)               # #06B6D4 Electric Cyan
BLUE = (56, 189, 248)              # #38BDF8 Sky Blue
GOLD = (245, 158, 11)              # #F59E0B Amber / Warning
RED = (239, 68, 68)                # #EF4444 Coral Red / Danger
GREEN = (16, 185, 129)             # #10B981 Emerald / Success
WHITE = (248, 250, 252)            # #F8FAFC Primary Text
MUTED = (148, 163, 184)            # #94A3B8 Secondary Text
DARK_TEXT = (15, 23, 42)

# Load System Fonts
try:
    FONT_TITLE_XL = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 52)
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
    FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24)
    FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    FONT_BODY_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
    FONT_SMALL_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
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

DASH_IMG = None
dash_path = ASSETS_DIR / "dashboard_screenshot.png"
if dash_path.exists():
    DASH_IMG = Image.open(dash_path).convert("RGB")


def create_base_frame(chapter_name: str, progress_ratio: float) -> Image.Image:
    """Draws background grid, top status bar, and bottom progress bar."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Subtle background technical grid dots
    for x in range(40, WIDTH, 60):
        for y in range(40, HEIGHT - 30, 60):
            draw.point((x, y), fill=(24, 36, 60))

    # Top Brand Ribbon
    draw.line([(0, 48), (WIDTH, 48)], fill=(30, 41, 59), width=1)
    if LOGO_IMG:
        logo_mini = LOGO_IMG.resize((28, 28))
        img.paste(logo_mini, (24, 10), mask=logo_mini)
    draw.text((60, 14), "ROADGUARD AI", fill=BLUE, font=FONT_SMALL_BOLD)
    draw.text((200, 15), "|  Smart Road Health & Damage Intelligence", fill=MUTED, font=FONT_SMALL)

    # Active chapter pill on top right
    pill_text = f"CHAPTER: {chapter_name.upper()}"
    bbox = draw.textbbox((0, 0), pill_text, font=FONT_TAG)
    pill_w = bbox[2] - bbox[0] + 16
    draw.rounded_rectangle([WIDTH - pill_w - 24, 12, WIDTH - 24, 36], radius=4, fill=(19, 30, 54), outline=(56, 189, 248), width=1)
    draw.text((WIDTH - pill_w - 16, 16), pill_text, fill=CYAN, font=FONT_TAG)

    # Bottom Progress Bar
    bar_y = HEIGHT - 12
    draw.line([(0, bar_y), (WIDTH, bar_y)], fill=(20, 30, 50), width=6)
    fill_w = int(WIDTH * progress_ratio)
    if fill_w > 0:
        draw.line([(0, bar_y), (fill_w, bar_y)], fill=CYAN, width=6)

    return img


def draw_card(img: Image.Image, box, fill=CARD_BG, outline=CARD_BORDER, radius=12, glow=False):
    """Draws a modern SaaS card container with optional glow."""
    draw = ImageDraw.Draw(img)
    x1, y1, x2, y2 = box
    if glow:
        draw.rounded_rectangle([x1 - 2, y1 - 2, x2 + 2, y2 + 2], radius=radius + 2, outline=(56, 189, 248, 80), width=2)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=1)


def render_scene_1(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 1: Platform Introduction & Title Sequence (0s - 8s)"""
    prog = local_f / (8 * FPS)
    img = create_base_frame("Introduction", prog)
    draw = ImageDraw.Draw(img)

    # Pulsing shield logo in center
    pulse = 1.0 + 0.04 * math.sin(local_f * 0.1)
    logo_sz = int(140 * pulse)
    if LOGO_IMG:
        logo_scaled = LOGO_IMG.resize((logo_sz, logo_sz))
        lx = (WIDTH - logo_sz) // 2
        ly = 150
        img.paste(logo_scaled, (lx, ly), mask=logo_scaled)

    # Animated Title reveal
    title_text = "ROADGUARD AI"
    draw.text(((WIDTH - 420) // 2, 320), title_text, fill=WHITE, font=FONT_TITLE_XL)

    # Subtitle
    sub_text = "Smart Road Health & Damage Intelligence Platform"
    draw.text(((WIDTH - 590) // 2, 390), sub_text, fill=CYAN, font=FONT_SUBTITLE)

    # Description card
    card_box = ((WIDTH - 820) // 2, 450, (WIDTH + 820) // 2, 570)
    draw_card(img, card_box, glow=True)
    draw.text((card_box[0] + 30, card_box[1] + 24),
              "An AI-powered municipal intelligence suite transforming raw road surface imagery",
              fill=WHITE, font=FONT_BODY_BOLD)
    draw.text((card_box[0] + 30, card_box[1] + 56),
              "into explainable hazard priority rankings, interactive GIS maps, and automated work orders.",
              fill=MUTED, font=FONT_BODY)

    # Tech Pills row
    pills = ["Ultralytics YOLO Vision", "Explainable Priority Scoring", "Interactive Folium GIS", "Relational SQLite & PDF"]
    px_start = 220
    for p in pills:
        draw.rounded_rectangle([px_start, 610, px_start + 195, 642], radius=6, fill=(15, 23, 42), outline=(56, 189, 248), width=1)
        draw.text((px_start + 12, 618), p, fill=BLUE, font=FONT_SMALL_BOLD)
        px_start += 215

    return img


def render_scene_2(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 2: The Infrastructure Crisis / Problem Statement (8s - 17s)"""
    prog = local_f / (9 * FPS)
    img = create_base_frame("The Municipal Challenge", 8/75 + prog * (9/75))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((80, 80), "The Urban Infrastructure Problem", fill=WHITE, font=FONT_TITLE)
    draw.text((80, 130), "Road degradation poses massive economic, safety, and operational challenges for cities worldwide.", fill=MUTED, font=FONT_BODY)

    # 3 Problem Cards
    cards = [
        {
            "icon": "⚠️",
            "title": "Severe Pothole Hazards",
            "stat": "$3.0 Billion / Year",
            "stat_label": "Global vehicle damage & road claims",
            "desc": "Unreported potholes develop into deep cavities, causing severe collisions, vehicle suspensions damage, and commuter delays.",
            "color": RED
        },
        {
            "icon": "⏳",
            "title": "Slow Paper Inspections",
            "stat": "3 to 6 Weeks Delay",
            "stat_label": "From citizen report to repair dispatch",
            "desc": "Traditional road inspections rely on manual patrols, paper forms, and fragmented citizen calls with no centralized priority ranking.",
            "color": GOLD
        },
        {
            "icon": "❓",
            "title": "Subjective Severity Triage",
            "stat": "Zero Geospatial Data",
            "stat_label": "Missing structured GIS coordinates",
            "desc": "Municipal road engineers lack explainable visual severity metrics and unified GIS maps to allocate asphalt repair crews effectively.",
            "color": CYAN
        }
    ]

    cx = 80
    for i, c in enumerate(cards):
        # Staggered slide in
        stagger = min(1.0, max(0.0, (local_f - i * 15) / 20.0))
        cy = int(200 + (1.0 - stagger) * 40)
        card_rect = (cx, cy, cx + 340, cy + 420)

        draw_card(img, card_rect, glow=(stagger == 1.0))
        # Top color accent line
        draw.line([(card_rect[0] + 12, card_rect[1] + 6), (card_rect[2] - 12, card_rect[1] + 6)], fill=c["color"], width=3)

        # Icon & Title
        draw.text((cx + 24, cy + 24), c["icon"], fill=WHITE, font=FONT_TITLE)
        draw.text((cx + 24, cy + 76), c["title"], fill=WHITE, font=FONT_SUBTITLE)

        # Stat Box
        draw.rounded_rectangle([cx + 20, cy + 120, cx + 320, cy + 200], radius=8, fill=(15, 23, 42), outline=c["color"], width=1)
        draw.text((cx + 34, cy + 132), c["stat"], fill=c["color"], font=FONT_BODY_BOLD)
        draw.text((cx + 34, cy + 164), c["stat_label"], fill=MUTED, font=FONT_SMALL)

        # Description
        draw.text((cx + 24, cy + 225), c["desc"][:80], fill=MUTED, font=FONT_SMALL)
        draw.text((cx + 24, cy + 250), c["desc"][80:160], fill=MUTED, font=FONT_SMALL)
        draw.text((cx + 24, cy + 275), c["desc"][160:], fill=MUTED, font=FONT_SMALL)

        cx += 390

    return img


def render_scene_3(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 3: The 4-Step Solution Pipeline (17s - 26s)"""
    prog = local_f / (9 * FPS)
    img = create_base_frame("System Workflow", 17/75 + prog * (9/75))
    draw = ImageDraw.Draw(img)

    draw.text((80, 80), "End-to-End Road Maintenance Workflow", fill=WHITE, font=FONT_TITLE)
    draw.text((80, 130), "How ROADGUARD AI converts everyday citizen photos into verified engineering actions.", fill=MUTED, font=FONT_BODY)

    steps = [
        ("1", "CAPTURE / UPLOAD", "Citizen or inspector takes road photo via smartphone camera or upload with EXIF GPS.", CYAN),
        ("2", "AI DAMAGE DETECTION", "Ultralytics YOLO localizes potholes & fissures with bounding boxes and confidence %.", BLUE),
        ("3", "PRIORITY SCORING", "Transparent 0–100 visual severity score based on area, defect count, & road traffic context.", GOLD),
        ("4", "GIS MAP & DISPATCH", "Pins to live Folium GIS map; authority triages maintenance queue and dispatches crews.", GREEN)
    ]

    sx = 80
    for idx, (num, title, desc, col) in enumerate(steps):
        sy = 220
        box = (sx, sy, sx + 255, sy + 380)
        draw_card(img, box, glow=True)

        # Number circle
        draw.ellipse([sx + 24, sy + 24, sx + 74, sy + 74], fill=col)
        draw.text((sx + 40, sy + 32), num, fill=DARK_TEXT, font=FONT_TITLE)

        draw.text((sx + 24, sy + 95), title, fill=col, font=FONT_SMALL_BOLD)
        draw.line([(sx + 24, sy + 125), (sx + 230, sy + 125)], fill=(40, 55, 80), width=1)

        # Description wrapped
        words = desc.split()
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 24:
                lines.append(" ".join(cur_line[:-1]))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))

        ly = sy + 145
        for l in lines:
            draw.text((sx + 24, ly), l, fill=WHITE, font=FONT_SMALL)
            ly += 26

        # Arrow connector between steps
        if idx < 3:
            arr_x = sx + 265
            draw.polygon([(arr_x, sy + 180), (arr_x + 16, sy + 190), (arr_x, sy + 200)], fill=BLUE)

        sx += 295

    return img


def render_scene_4(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 4: YOLO AI Detection Engine in Action (26s - 38s)"""
    prog = local_f / (12 * FPS)
    img = create_base_frame("AI Vision Pipeline", 26/75 + prog * (12/75))
    draw = ImageDraw.Draw(img)

    draw.text((80, 75), "AI Road Damage Detection Engine", fill=WHITE, font=FONT_TITLE)
    draw.text((80, 120), "Ultralytics YOLO computer vision detects potholes, cracks, and road defects with high certainty.", fill=MUTED, font=FONT_BODY)

    # Road Image Display
    img_box = (80, 170, 720, 610)
    draw_card(img, img_box, glow=True)

    if ROAD_IMG:
        road_scaled = ROAD_IMG.resize((620, 400))
        img.paste(road_scaled, (90, 185))

        # Animated Laser Scan Line
        scan_y = int(185 + (local_f % (FPS * 3)) / (FPS * 3) * 400)
        draw.line([(90, scan_y), (710, scan_y)], fill=(6, 182, 212), width=3)
        draw.line([(90, scan_y - 2), (710, scan_y - 2)], fill=(56, 189, 248, 120), width=1)

        # Render Bounding Boxes
        # Pothole Bounding Box
        bx1, by1, bx2, by2 = 250, 310, 480, 480
        draw.rectangle([bx1, by1, bx2, by2], outline=RED, width=3)
        draw.rectangle([bx1, by1 - 26, bx1 + 175, by1], fill=RED)
        draw.text((bx1 + 8, by1 - 22), "Pothole (89.5% Conf)", fill=WHITE, font=FONT_TAG)

        # Longitudinal Crack Bounding Box
        cx1, cy1, cx2, cy2 = 490, 260, 620, 440
        draw.rectangle([cx1, cy1, cx2, cy2], outline=GOLD, width=3)
        draw.rectangle([cx1, cy1 - 26, cx1 + 195, cy1], fill=GOLD)
        draw.text((cx1 + 8, cy1 - 22), "Longitudinal Crack (74%)", fill=DARK_TEXT, font=FONT_TAG)

    # Right Side Spec Panel
    panel_box = (750, 170, 1200, 610)
    draw_card(img, panel_box)

    draw.text((775, 195), "DETECTION DIAGNOSTICS", fill=CYAN, font=FONT_SUBTITLE)
    draw.line([(775, 230), (1175, 230)], fill=(40, 55, 80), width=1)

    metrics = [
        ("Model Framework:", "Ultralytics YOLO (PyTorch)"),
        ("Model Checkpoint:", "models/best.pt (Modular Loader)"),
        ("Supported Defect Classes:", "Potholes, Alligator Cracks, Fissures"),
        ("Input Processing:", "Dynamic RGB Normalization & NMS"),
        ("Inference Speed:", "~18ms on GPU / ~45ms on CPU"),
        ("Multi-Image Support:", "Single, Batch & Camera Capture"),
        ("Bounding Box Extraction:", "Coordinates [x1, y1, x2, y2] + Area Ratio")
    ]

    my = 250
    for k, v in metrics:
        draw.text((775, my), k, fill=MUTED, font=FONT_SMALL)
        draw.text((775, my + 20), v, fill=WHITE, font=FONT_BODY_BOLD)
        my += 48

    return img


def render_scene_5(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 5: Explainable Visual Priority Scoring (38s - 50s)"""
    prog = local_f / (12 * FPS)
    img = create_base_frame("Priority Scoring", 38/75 + prog * (12/75))
    draw = ImageDraw.Draw(img)

    draw.text((80, 75), "Explainable 0–100 Visual Priority Engine", fill=WHITE, font=FONT_TITLE)
    draw.text((80, 120), "Algorithmic civil engineering scoring combining defect severity, surface area, and road traffic context.", fill=MUTED, font=FONT_BODY)

    # Left: Score Gauge Display
    gauge_box = (80, 170, 480, 610)
    draw_card(img, gauge_box, glow=True)

    draw.text((110, 200), "ASSESSED HAZARD INDEX", fill=MUTED, font=FONT_SMALL_BOLD)

    # Animated Score Counter
    target_score = 88.5
    curr_score = min(target_score, target_score * (local_f / (FPS * 2.0)))

    draw.text((110, 230), f"{curr_score:.1f}", fill=RED, font=FONT_TITLE_XL)
    draw.text((250, 250), "/ 100", fill=MUTED, font=FONT_SUBTITLE)

    # Priority Band Tag
    draw.rounded_rectangle([110, 310, 310, 345], radius=6, fill=(239, 68, 68, 40), outline=RED, width=1)
    draw.text((125, 318), "HIGH PRIORITY HAZARD", fill=RED, font=FONT_SMALL_BOLD)

    # Action Urgency
    draw.text((110, 370), "Recommended Triage Action:", fill=MUTED, font=FONT_SMALL)
    draw.text((110, 395), "Schedule physical inspection", fill=WHITE, font=FONT_BODY_BOLD)
    draw.text((110, 420), "within 24 to 48 hours.", fill=WHITE, font=FONT_BODY_BOLD)

    # Engineering Disclaimer Callout
    disclaimer_box = (100, 470, 460, 580)
    draw.rounded_rectangle(disclaimer_box, radius=8, fill=(15, 23, 42), outline=(56, 189, 248), width=1)
    draw.text((112, 485), "ENGINEERING NOTICE:", fill=CYAN, font=FONT_TAG)
    draw.text((112, 508), "2D visual scoring prioritizes human inspection.", fill=MUTED, font=FONT_TAG)
    draw.text((112, 528), "It does not claim to measure subsurface cavity", fill=MUTED, font=FONT_TAG)
    draw.text((112, 548), "depth or structural road strength.", fill=MUTED, font=FONT_TAG)

    # Right: Formula Factor Breakdown
    right_box = (510, 170, 1200, 610)
    draw_card(img, right_box)

    draw.text((540, 195), "5-FACTOR MULTI-VARIABLE FORMULA", fill=CYAN, font=FONT_SUBTITLE)
    draw.line([(540, 230), (1170, 230)], fill=(40, 55, 80), width=1)

    factors = [
        ("1. Class Baseline Severity", "38.0 Pts", "Potholes (cavities) heavily weighted over hairline cracks", RED),
        ("2. Damaged Surface Area", "24.5 Pts", "Pixel bounding box coverage percentage relative to frame", GOLD),
        ("3. Defect Multiplicity / Density", "12.0 Pts", "Cluster multiplicity multiplier for multiple defect regions", CYAN),
        ("4. AI Model Certainty", "14.2 Pts", "Detection confidence weighting ensures high certainty triage", BLUE),
        ("5. Roadway Context Multiplier", "1.25x", "Multipliers for Highway vs Residential, Heavy Trucks, & Rain", GREEN)
    ]

    fy = 245
    for title, pts, desc, col in factors:
        draw.text((540, fy), title, fill=WHITE, font=FONT_BODY_BOLD)
        draw.text((1050, fy), pts, fill=col, font=FONT_BODY_BOLD)
        draw.text((540, fy + 24), desc, fill=MUTED, font=FONT_SMALL)
        # Mini progress bar
        draw.line([(540, fy + 48), (1160, fy + 48)], fill=(30, 45, 70), width=3)
        draw.line([(540, fy + 48), (540 + int(620 * 0.75), fy + 48)], fill=col, width=3)
        fy += 68

    return img


def render_scene_6(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 6: Geospatial Intelligence & GIS Map (50s - 61s)"""
    prog = local_f / (11 * FPS)
    img = create_base_frame("GIS Geospatial Map", 50/75 + prog * (11/75))
    draw = ImageDraw.Draw(img)

    draw.text((80, 75), "Live Geospatial Intelligence & GIS Mapping", fill=WHITE, font=FONT_TITLE)
    draw.text((80, 120), "Interactive Folium mapping with cluster layers, priority pins, and photo thumbnail popups.", fill=MUTED, font=FONT_BODY)

    # Simulated GIS Map container
    map_box = (80, 170, 780, 610)
    draw_card(img, map_box, fill=(15, 23, 42), glow=True)

    # Draw simulated dark map roads/intersections
    map_draw = ImageDraw.Draw(img)
    # Highway corridors
    map_draw.line([(100, 380), (760, 380)], fill=(35, 50, 80), width=16)
    map_draw.line([(100, 380), (760, 380)], fill=(50, 70, 110), width=10)
    map_draw.line([(400, 190), (400, 590)], fill=(35, 50, 80), width=16)
    map_draw.line([(400, 190), (400, 590)], fill=(50, 70, 110), width=10)
    # Secondary streets
    map_draw.line([(220, 200), (680, 560)], fill=(30, 45, 70), width=6)
    map_draw.line([(180, 520), (620, 220)], fill=(30, 45, 70), width=6)

    # Simulated Priority Pins
    pins = [
        (400, 380, RED, "RGD-2026-0101", "Pothole (88.5)", True),
        (260, 380, GOLD, "RGD-2026-0102", "Crack (52.0)", False),
        (560, 380, RED, "RGD-2026-0105", "Pothole (82.0)", False),
        (400, 260, GREEN, "RGD-2026-0104", "Fissure (32.5)", False),
        (310, 460, GOLD, "RGD-2026-0103", "Crack (48.0)", False)
    ]

    for px, py, col, rid, dname, active in pins:
        # Glow pulse
        if active:
            r = int(18 + 4 * math.sin(local_f * 0.2))
            map_draw.ellipse([px - r, py - r, px + r, py + r], outline=col, width=2)
        map_draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=col, outline=WHITE, width=2)

    # Active Marker Popup Box simulation
    pop_box = (430, 260, 740, 500)
    draw_card(img, pop_box, fill=(19, 30, 54), glow=True)
    draw.text((450, 280), "RGD-2026-0101", fill=RED, font=FONT_BODY_BOLD)
    draw.text((450, 310), "Defect: Pothole & Cavity", fill=WHITE, font=FONT_SMALL)
    draw.text((450, 335), "Priority Score: 88.5 / 100 (HIGH)", fill=RED, font=FONT_SMALL_BOLD)
    draw.text((450, 360), "Location: Delhi Ring Road Flyover", fill=MUTED, font=FONT_SMALL)
    draw.text((450, 385), "Coordinates: 28.5700, 77.2400 (GPS)", fill=CYAN, font=FONT_TAG)
    draw.text((450, 410), "Status: Inspection Scheduled", fill=GOLD, font=FONT_SMALL_BOLD)

    # Right: Geospatial Highlights
    g_box = (810, 170, 1200, 610)
    draw_card(img, g_box)

    draw.text((835, 195), "GEOSPATIAL CAPABILITIES", fill=CYAN, font=FONT_SUBTITLE)
    draw.line([(835, 230), (1175, 230)], fill=(40, 55, 80), width=1)

    feats = [
        ("📍 Interactive Map Pinning", "Click anywhere on the map during capture to set coordinates automatically."),
        ("📷 EXIF GPS Extraction", "Smartphones automatically embed GPS metadata directly into reports."),
        ("🛡️ Strict Safety Protocols", "Missing-GPS reports are never placed randomly; segregated to unlocated list."),
        ("🎨 Dynamic Color Pins", "Red (High 70-100), Amber (Medium 40-69), Green (Low 0-39)."),
        ("🔍 Granular Layer Filters", "Filter by damage category, lifecycle repair status, and priority tier.")
    ]

    gy = 250
    for t, d in feats:
        draw.text((835, gy), t, fill=WHITE, font=FONT_BODY_BOLD)
        draw.text((835, gy + 22), d[:48], fill=MUTED, font=FONT_SMALL)
        draw.text((835, gy + 42), d[48:], fill=MUTED, font=FONT_SMALL)
        gy += 70

    return img


def render_scene_7(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 7: Authority Queue, Status Lifecycle & PDF Reports (61s - 70s)"""
    prog = local_f / (9 * FPS)
    img = create_base_frame("Operations & Reporting", 61/75 + prog * (9/75))
    draw = ImageDraw.Draw(img)

    draw.text((80, 75), "Municipal Triage Queue & Automated Work Orders", fill=WHITE, font=FONT_TITLE)
    draw.text((80, 120), "Ranked priority queue, 5-stage lifecycle audit logging, and instant ReportLab PDF compilation.", fill=MUTED, font=FONT_BODY)

    # Left: Platform Live Screenshot
    dash_box = (80, 170, 680, 610)
    draw_card(img, dash_box, glow=True)

    if DASH_IMG:
        dash_scaled = DASH_IMG.resize((580, 390))
        img.paste(dash_scaled, (90, 190))

    # Right: Operational Workflow Cards
    right_box = (710, 170, 1200, 610)
    draw_card(img, right_box)

    draw.text((735, 195), "MUNICIPAL OPERATIONS", fill=CYAN, font=FONT_SUBTITLE)
    draw.line([(735, 230), (1175, 230)], fill=(40, 55, 80), width=1)

    ops = [
        ("⚡ Ranked Priority Queue", "Pending defects ranked by score with transparent algorithmic reasoning for human decision support."),
        ("🔄 5-Stage Lifecycle Audit", "New -> Under Review -> Inspection Scheduled -> Repair in Progress -> Resolved with immutable logs."),
        ("📄 ReportLab PDF Generation", "Compiles print-ready inspection sheets with header branding, coordinates, AI bboxes, and sign-offs."),
        ("📊 Full CSV Database Export", "One-click export of relational records formatted for GIS and municipal CAD databases."),
        ("👤 Role-Based Access Control", "Municipal Authority (Admin) vs Citizen Reporter with salted SHA-256 password security.")
    ]

    oy = 245
    for t, d in ops:
        draw.text((735, oy), t, fill=BLUE, font=FONT_BODY_BOLD)
        draw.text((735, oy + 22), d[:50], fill=MUTED, font=FONT_SMALL)
        draw.text((735, oy + 42), d[50:], fill=MUTED, font=FONT_SMALL)
        oy += 70

    return img


def render_scene_8(frame_idx: int, local_f: int) -> Image.Image:
    """Scene 8: Conclusion & Call to Action (70s - 75s)"""
    prog = local_f / (5 * FPS)
    img = create_base_frame("Summary", 70/75 + prog * (5/75))
    draw = ImageDraw.Draw(img)

    # Logo in center
    if LOGO_IMG:
        logo_sz = 110
        logo_scaled = LOGO_IMG.resize((logo_sz, logo_sz))
        img.paste(logo_scaled, ((WIDTH - logo_sz) // 2, 140), mask=logo_scaled)

    draw.text(((WIDTH - 420) // 2, 270), "ROADGUARD AI", fill=WHITE, font=FONT_TITLE_XL)
    draw.text(((WIDTH - 520) // 2, 340), "Smarter, Safer, Data-Driven Road Infrastructure", fill=CYAN, font=FONT_SUBTITLE)

    # Highlights Box
    h_box = ((WIDTH - 840) // 2, 395, (WIDTH + 840) // 2, 530)
    draw_card(img, h_box, glow=True)

    draw.text((h_box[0] + 40, h_box[1] + 24), "✓ 100% Functional Production Web Application (Streamlit + SQLite)", fill=GREEN, font=FONT_BODY_BOLD)
    draw.text((h_box[0] + 40, h_box[1] + 54), "✓ Modular Ultralytics YOLO Vision with In-Browser Checkpoint Uploader", fill=BLUE, font=FONT_BODY_BOLD)
    draw.text((h_box[0] + 40, h_box[1] + 84), "✓ Explainable Scoring, Interactive GIS Maps, & Official PDF Work Orders", fill=CYAN, font=FONT_BODY_BOLD)

    # CTA Button simulation
    cta_box = ((WIDTH - 480) // 2, 560, (WIDTH + 480) // 2, 620)
    draw.rounded_rectangle(cta_box, radius=8, fill=(2, 132, 199), outline=(56, 189, 248), width=2)
    draw.text((cta_box[0] + 60, cta_box[1] + 16), "OPEN HTTP://LOCALHOST:8501", fill=WHITE, font=FONT_BODY_BOLD)

    return img


def generate_video():
    """Compiles the full explainer video file."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(OUTPUT_FILE), fourcc, float(FPS), (WIDTH, HEIGHT))

    print(f"Generating ROADGUARD AI Explainer Video ({TOTAL_FRAMES} frames @ {FPS} fps)...")

    # Frame distribution timeline:
    # Scene 1: 0 to 8s (frames 0 to 240)
    # Scene 2: 8 to 17s (frames 240 to 510)
    # Scene 3: 17 to 26s (frames 510 to 780)
    # Scene 4: 26 to 38s (frames 780 to 1140)
    # Scene 5: 38 to 50s (frames 1140 to 1500)
    # Scene 6: 50 to 61s (frames 1500 to 1830)
    # Scene 7: 61 to 70s (frames 1830 to 2100)
    # Scene 8: 70 to 75s (frames 2100 to 2250)

    for f in range(TOTAL_FRAMES):
        if f < 240:
            pil_frame = render_scene_1(f, f)
        elif f < 510:
            pil_frame = render_scene_2(f, f - 240)
        elif f < 780:
            pil_frame = render_scene_3(f, f - 510)
        elif f < 1140:
            pil_frame = render_scene_4(f, f - 780)
        elif f < 1500:
            pil_frame = render_scene_5(f, f - 1140)
        elif f < 1830:
            pil_frame = render_scene_6(f, f - 1500)
        elif f < 2100:
            pil_frame = render_scene_7(f, f - 1830)
        else:
            pil_frame = render_scene_8(f, f - 2100)

        # Convert PIL (RGB) to OpenCV (BGR)
        cv_frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
        out.write(cv_frame)

        if f % 300 == 0:
            print(f"Rendered {f}/{TOTAL_FRAMES} frames ({int(f/TOTAL_FRAMES*100)}%)...")

    out.release()
    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"Video generation complete! Saved to {OUTPUT_FILE} ({file_size_mb:.2f} MB)")
    return str(OUTPUT_FILE)


if __name__ == "__main__":
    generate_video()
