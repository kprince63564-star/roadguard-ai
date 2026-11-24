"""
ROADGUARD AI - Internationalization (i18n) Module
Provides dual-language support for English (en) and Hindi (hi / हिंदी),
allowing citizens and municipal engineers to seamlessly switch languages.
"""

import streamlit as st
from typing import Dict, Any, Optional

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिंदी (Hindi)"
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App Branding
        "app_name": "ROADGUARD AI",
        "app_tagline": "Road Health & Damage Intelligence",
        "app_suite": "MUNICIPAL DEPLOYMENT SUITE • v2.4",
        "system_status": "SYSTEM OPERATIONAL",
        "engine_label": "ENGINE",
        "gis_telemetry": "GIS TELEMETRY",
        "online": "ONLINE",
        "offline": "OFFLINE",
        "active_credentials": "Active Credentials",
        "switch_persona": "🔄 Switch User Persona",
        "switch_to_citizen": "Switch to Citizen View",
        "switch_to_authority": "Switch to Authority View",
        "model_loaded": "● MODEL WEIGHTS: best.pt loaded",
        "ai_core_ready": "● AI VISION CORE: Online (Simulation Ready)",
        "footer_sub": "ROADGUARD AI • GovTech SaaS<br/>Empowering Smart City Infrastructure",
        "lang_selector_label": "🌐 Language / भाषा",

        # Navigation
        "nav_overview": "📊 Overview Dashboard",
        "nav_detect": "🔍 Detect Road Damage",
        "nav_reports": "📋 Damage Reports",
        "nav_map": "🗺️ Live Damage Map",
        "nav_queue": "⚡ Maintenance Priority Queue",
        "nav_analytics": "📈 Analytics & Insights",
        "nav_export": "📄 Generate Reports",
        "nav_settings": "⚙️ Settings / About",

        # Header
        "breadcrumb_ops": "MUNICIPAL OPERATIONS",
        "breadcrumb_surface": "SURFACE MONITORING",
        "breadcrumb_overview": "EXECUTIVE OVERVIEW",
        "header_title": "Executive Road Intelligence Overview",
        "header_subtitle": "Real-time municipal telemetry on road surface degradation, visual hazard priority triage, and work order lifecycle dispatch.",
        "chip_gis": "● GIS SURVEILLANCE ACTIVE",
        "chip_ai": "● AI DEFECT SCORING v2.4",

        # Video Expander
        "video_expander_title": "🎬 Watch App Tutorial: How to Use ROADGUARD AI (उपयोग गाइड)",
        "video_pillars_title": "🛡️ How to Use ROADGUARD AI in 4 Steps:",
        "video_step1": "1. **Capture or Upload:** Take a road photo or upload from device.",
        "video_step2": "2. **AI Detection:** Ultralytics YOLO localizes potholes & fissures.",
        "video_step3": "3. **Pin Location:** Auto-extract GPS or click on the interactive GIS map.",
        "video_step4": "4. **Triage & Dispatch:** Calculate 0–100 priority score & generate PDF work order.",
        "download_video_btn": "⬇️ Download Tutorial Video (.mp4)",
        "download_subtitles_btn": "⬇️ Download Subtitles (.srt)",
        "guide_script_title": "🎙️ View Step-by-Step App Walkthrough Guide (English & हिंदी)",

        # Empty State
        "empty_title": "No Road Damage Reports in Municipal Database",
        "empty_desc": "The database is currently clean with zero recorded damage incidents. You can submit your first live road inspection in the Detect Road Damage module, or seed sample records.",
        "empty_load_btn": "📥 Load Labeled Demo Records",

        # Alert Bar
        "priority_alert_title": "Priority Alert Active:",
        "priority_alert_desc": "critical road hazard(s) require immediate engineering inspection and crew dispatch.",
        "urgent_triage_chip": "URGENT TRIAGE",

        # Metric KPI Cards
        "kpi_total_reports": "Total Registered Incidents",
        "kpi_total_reports_sub": "Active telemetry logs",
        "kpi_total_reports_delta": "▲ 100% verified database",
        "kpi_potholes": "Detected Potholes",
        "kpi_potholes_sub": "High impact cavity defects",
        "kpi_potholes_delta": "● High vehicular risk",
        "kpi_cracks": "Detected Cracks",
        "kpi_cracks_sub": "Structural & alligator fissures",
        "kpi_cracks_delta": "● Surface degradation",
        "kpi_high_priority": "High Priority Hazards",
        "kpi_high_priority_sub": "Score ≥ 70 / 100",
        "kpi_high_priority_delta": "Immediate Action Required",
        "kpi_awaiting": "Awaiting Inspection",
        "kpi_awaiting_sub": "Pending field engineering verification",
        "kpi_repaired": "Repaired / Resolved",
        "kpi_repaired_sub": "Completed civil works",
        "kpi_avg_score": "Mean Priority Hazard Index",
        "kpi_avg_score_sub": "Explainable visual triage index",

        # Charts
        "chart_damage_dist": "Damage Type Distribution",
        "chart_priority_triage": "Priority Band Triage",
        "chart_status_pipeline": "Maintenance Status Pipeline",
        "chart_hotspots": "Critical Damage Hotspots",

        # Table
        "table_title": "Live Field Damage Telemetry Feed",
        "col_incident_id": "Incident ID",
        "col_classification": "Classification",
        "col_location": "Location / Corridor",
        "col_priority": "Visual Priority",
        "col_status": "Lifecycle Status",
        "col_timestamp": "Logged Timestamp",

        # Detect Page
        "detect_header": "AI Road Damage Detection & Telemetry",
        "detect_subtitle": "Automated multi-defect localization powered by Ultralytics YOLO with explainable visual civil engineering priority triage.",
        "detect_input_method": "Choose Image Input Method:",
        "detect_upload_file": "📁 Upload Image File",
        "detect_camera": "📸 Use Device Camera",
        "detect_sample_btn": "⚡ Load Sample Road Image",
        "detect_analyze_btn": "🚀 Analyze Road Damage with AI",
        "detect_map_title": "📍 Geospatial Location & Map Pinning",
        "detect_map_desc": "Click anywhere on the map to pin the incident coordinates, or use preset GPS coordinates.",
        "detect_form_title": "📋 Site Context & Explainable Priority Calculation",
        "detect_road_type": "Roadway Classification",
        "detect_traffic_volume": "Traffic Volume Density",
        "detect_weather": "Weather / Pavement State",
        "detect_submit_btn": "💾 Save Official Road Damage Report to Database",

        # Reports Page
        "reports_header": "Road Damage Reports Management",
        "reports_subtitle": "Inspect recorded damage reports, audit status transitions, filter by priority, and manage repair workflows.",

        # Roles
        "role_authority": "MUNICIPAL AUTHORITY",
        "role_citizen": "CITIZEN REPORTER"
    },

    "hi": {
        # App Branding
        "app_name": "रोडगार्ड एआई",
        "app_tagline": "सड़क स्वास्थ्य एवं क्षति विश्लेषण प्रणाली",
        "app_suite": "नगर निगम परिनियोजन संस्करण • v2.4",
        "system_status": "सिस्टम सक्रिय",
        "engine_label": "इंजन",
        "gis_telemetry": "जीआईएस टेलीमेट्री",
        "online": "ऑनलाइन",
        "offline": "ऑफलाइन",
        "active_credentials": "सक्रिय क्रेडेंशियल",
        "switch_persona": "🔄 उपयोगकर्ता भूमिका बदलें",
        "switch_to_citizen": "नागरिक दृश्य में बदलें",
        "switch_to_authority": "अधिकारी दृश्य में बदलें",
        "model_loaded": "● मॉडल भार: best.pt लोड हो गया",
        "ai_core_ready": "● एआई विज़न कोर: ऑनलाइन (सिमुलेशन तैयार)",
        "footer_sub": "रोडगार्ड एआई • सरकारी प्रौद्योगिकी SaaS<br/>स्मार्ट सिटी अवसंरचना को सशक्त बनाना",
        "lang_selector_label": "🌐 भाषा / Language",

        # Navigation
        "nav_overview": "📊 अवलोकन डैशबोर्ड",
        "nav_detect": "🔍 सड़क क्षति पहचानें",
        "nav_reports": "📋 क्षति रिपोर्ट प्रबंधन",
        "nav_map": "🗺️ लाइव क्षति नक्शा (GIS)",
        "nav_queue": "⚡ रखरखाव प्राथमिकता कतार",
        "nav_analytics": "📈 एनालिटिक्स और अंतर्दृष्टि",
        "nav_export": "📄 रिपोर्ट और वर्क ऑर्डर",
        "nav_settings": "⚙️ सेटिंग्स / सिस्टम परिचय",

        # Header
        "breadcrumb_ops": "नगर निगम संचालन",
        "breadcrumb_surface": "सड़क सतह निगरानी",
        "breadcrumb_overview": "कार्यकारी अवलोकन",
        "header_title": "कार्यकारी सड़क विश्लेषण डैशबोर्ड",
        "header_subtitle": "सड़क क्षरण, दृश्य खतरे की प्राथमिकता और मरम्मत कार्य आदेशों की रीयल-टाइम नगर निगम टेलीमेट्री।",
        "chip_gis": "● जीआईएस निगरानी सक्रिय",
        "chip_ai": "● एआई दोष स्कोरिंग v2.4",

        # Video Expander
        "video_expander_title": "🎬 एप उपयोग गाइड: रोडगार्ड एआई का उपयोग कैसे करें",
        "video_pillars_title": "🛡️ रोडगार्ड एआई का उपयोग करने के 4 आसान चरण:",
        "video_step1": "1. **फोटो लें या अपलोड करें:** सड़क की तस्वीर खींचे या डिवाइस से अपलोड करें।",
        "video_step2": "2. **एआई द्वारा पहचान:** Ultralytics YOLO गड्ढों और दरारों का तुरंत पता लगाता है।",
        "video_step3": "3. **स्थान पिन करें:** फोटो से जीपीएस स्वतः लें या लाइव नक्शे पर क्लिक करें।",
        "video_step4": "4. **प्राथमिकता और डिस्पैच:** 0-100 स्कोर देखकर आधिकारिक पीडीएफ वर्क ऑर्डर बनाएं।",
        "download_video_btn": "⬇️ ट्यूटोरियल वीडियो डाउनलोड करें (.mp4)",
        "download_subtitles_btn": "⬇️ उपशीर्षक डाउनलोड करें (.srt)",
        "guide_script_title": "🎙️ चरण-दर-चरण एप गाइड देखें (हिंदी और अंग्रेजी)",

        # Empty State
        "empty_title": "नगर निगम डेटाबेस में कोई सड़क क्षति रिपोर्ट नहीं है",
        "empty_desc": "वर्तमान में डेटाबेस साफ है। आप 'सड़क क्षति पहचानें' मॉड्यूल में पहली रिपोर्ट दर्ज कर सकते हैं या डेमो डेटा लोड कर सकते हैं।",
        "empty_load_btn": "📥 डेमो रिकॉर्ड्स लोड करें",

        # Alert Bar
        "priority_alert_title": "प्राथमिकता चेतावनी सक्रिय:",
        "priority_alert_desc": "गंभीर सड़क खतरों के लिए तत्काल इंजीनियरिंग निरीक्षण और मरम्मत दल की आवश्यकता है।",
        "urgent_triage_chip": "अति आवश्यक",

        # Metric KPI Cards
        "kpi_total_reports": "कुल दर्ज घटनाएं",
        "kpi_total_reports_sub": "सक्रिय टेलीमेट्री लॉग्स",
        "kpi_total_reports_delta": "▲ 100% सत्यापित डेटाबेस",
        "kpi_potholes": "पहचाने गए गड्ढे",
        "kpi_potholes_sub": "गंभीर वाहन जोखिम",
        "kpi_potholes_delta": "● उच्च दुर्घटना खतरा",
        "kpi_cracks": "पहचानी गई दरारें",
        "kpi_cracks_sub": "ढांचागत एवं सतह दरारें",
        "kpi_cracks_delta": "● सतह का क्षरण",
        "kpi_high_priority": "उच्च प्राथमिकता खतरे",
        "kpi_high_priority_sub": "स्कोर ≥ 70 / 100",
        "kpi_high_priority_delta": "तत्काल कार्रवाई आवश्यक",
        "kpi_awaiting": "निरीक्षण की प्रतीक्षा",
        "kpi_awaiting_sub": "इंजीनियरिंग सत्यापन लंबित",
        "kpi_repaired": "मरम्मत / समाधान पूर्ण",
        "kpi_repaired_sub": "पूर्ण हुए सिविल कार्य",
        "kpi_avg_score": "औसत प्राथमिकता खतरा सूचकांक",
        "kpi_avg_score_sub": "स्पष्ट दृश्य प्राथमिकता स्कोर",

        # Charts
        "chart_damage_dist": "क्षति प्रकार वितरण",
        "chart_priority_triage": "प्राथमिकता श्रेणी वर्गीकरण",
        "chart_status_pipeline": "रखरखाव स्थिति पाइपलाइन",
        "chart_hotspots": "प्रमुख संवेदनशील स्थान (हॉटस्पॉट)",

        # Table
        "table_title": "लाइव फील्ड क्षति टेलीमेट्री फीड",
        "col_incident_id": "घटना आईडी",
        "col_classification": "क्षति प्रकार",
        "col_location": "स्थान / कॉरिडोर",
        "col_priority": "दृश्य प्राथमिकता",
        "col_status": "कार्य स्थिति",
        "col_timestamp": "दर्ज समय",

        # Detect Page
        "detect_header": "एआई सड़क क्षति पहचान एवं टेलीमेट्री",
        "detect_subtitle": "Ultralytics YOLO द्वारा संचालित स्वचालित दोष पहचान और पारदर्शी सिविल इंजीनियरिंग प्राथमिकता मूल्यांकन।",
        "detect_input_method": "छवि इनपुट विधि चुनें:",
        "detect_upload_file": "📁 छवि फ़ाइल अपलोड करें",
        "detect_camera": "📸 डिवाइस कैमरा का उपयोग करें",
        "detect_sample_btn": "⚡ नमूना सड़क फोटो लोड करें",
        "detect_analyze_btn": "🚀 एआई से सड़क क्षति का विश्लेषण करें",
        "detect_map_title": "📍 भौगोलिक स्थान एवं नक्शा पिनिंग",
        "detect_map_desc": "घटना के निर्देशांक पिन करने के लिए नक्शे पर कहीं भी क्लिक करें, या जीपीएस का उपयोग करें।",
        "detect_form_title": "📋 साइट संदर्भ एवं पारदर्शी स्कोर गणना",
        "detect_road_type": "सड़क वर्गीकरण",
        "detect_traffic_volume": "यातायात घनत्व",
        "detect_weather": "मौसम / सड़क की स्थिति",
        "detect_submit_btn": "💾 आधिकारिक सड़क क्षति रिपोर्ट सहेजें",

        # Reports Page
        "reports_header": "सड़क क्षति रिपोर्ट प्रबंधन",
        "reports_subtitle": "दर्ज रिपोर्टों का निरीक्षण करें, मरम्मत स्थिति अपडेट करें और प्राथमिकता अनुसार छांटें।",

        # Roles
        "role_authority": "नगर निगम प्राधिकारी",
        "role_citizen": "नागरिक रिपोर्टर"
    }
}

def get_current_language() -> str:
    """Returns currently selected language code ('en' or 'hi')."""
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    return st.session_state["language"]

def set_language(lang_code: str):
    """Sets active language."""
    if lang_code in SUPPORTED_LANGUAGES:
        st.session_state["language"] = lang_code

def t(key: str, default: Optional[str] = None) -> str:
    """Translates a key into current language."""
    lang = get_current_language()
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    if key in lang_dict:
        return lang_dict[key]
    # Fallback to English
    return TRANSLATIONS["en"].get(key, default or key)

def render_language_selector():
    """Renders sleek language switch pills in sidebar."""
    cur_lang = get_current_language()
    options = list(SUPPORTED_LANGUAGES.keys())
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 English", key="lang_btn_en", use_container_width=True, 
                     type="primary" if cur_lang == "en" else "secondary"):
            set_language("en")
            st.rerun()
    with col2:
        if st.button("🇮🇳 हिंदी", key="lang_btn_hi", use_container_width=True,
                     type="primary" if cur_lang == "hi" else "secondary"):
            set_language("hi")
            st.rerun()
