"""
ROADGUARD AI - Smart Road Health & Damage Intelligence Platform
Main application entry point orchestrating sidebar navigation, CSS theming,
bilingual internationalization (English & हिंदी), database initialization, and routing.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime

# Streamlit Page Configuration - Must be the first Streamlit command
st.set_page_config(
    page_title="ROADGUARD AI - Smart Road Health & Damage Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import ASSETS_DIR, DEFAULT_MODEL_PATH
from database.db import init_db
from utils.auth import init_session_auth, get_current_user, switch_role
from detection.detector import get_detector
from utils.i18n import t, render_language_selector, get_current_language

# Page View Imports
from dashboard.overview import render_overview
from dashboard.detect import render_detection_page
from dashboard.reports_view import render_reports_page
from dashboard.map_view import render_map_page
from dashboard.queue_view import render_queue_page
from dashboard.analytics_view import render_analytics_page
from dashboard.export_view import render_export_page
from dashboard.settings_view import render_settings_page

def load_custom_css():
    """Loads and injects custom GovTech SaaS dark stylesheet."""
    css_file = ASSETS_DIR / "styles.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_top_telemetry_bar(user, model_status):
    """Renders a sleek top telemetry banner typical of municipal control rooms."""
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    engine_label = "YOLOv8 Custom" if model_status.get("is_custom") else "YOLOv8 Vision"
    
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(90deg, #161922 0%, #11141A 100%); border: 1px solid rgba(255,255,255,0.08); border-left: 4px solid #F97316; border-radius: 10px; padding: 11px 18px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(0,0,0,0.4);">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 10px #10B981; display: inline-block;"></span>
                    <span style="font-size: 0.76rem; font-weight: 700; color: #10B981; letter-spacing: 0.06em;">{t('system_status')}</span>
                </div>
                <span style="color: #373A44;">|</span>
                <div style="font-size: 0.76rem; color: #A1A1AA;">
                    {t('engine_label')}: <span style="color: #FFA057; font-weight: 700;">{engine_label}</span>
                </div>
                <span style="color: #373A44;">|</span>
                <div style="font-size: 0.76rem; color: #A1A1AA;">
                    {t('gis_telemetry')}: <span style="color: #10B981; font-weight: 700;">{t('online')}</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #71717A;">
                    🕒 {current_time_str}
                </div>
                <div style="background: rgba(249,115,22,0.15); border: 1px solid rgba(249,115,22,0.35); color: #FFA057; font-size: 0.7rem; font-weight: 700; padding: 3px 9px; border-radius: 5px;">
                    v2.4-GOVTECH
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    # 1. Initialize System Infrastructure
    init_db()
    init_session_auth()
    load_custom_css()

    user = get_current_user() or {"full_name": "Municipal Road Engineer", "role": "authority"}
    detector = get_detector()
    model_status = detector.get_status_info()

    # 2. Sidebar Navigation & Branding
    with st.sidebar:
        logo_file = ASSETS_DIR / "logo.png"
        if logo_file.exists():
            st.image(str(logo_file), width=70)

        st.markdown(f"""
            <div class="rg-brand-container">
                <h2 class="rg-brand-title">{t('app_name')}</h2>
                <div class="rg-brand-tagline">{t('app_tagline')}</div>
                <div class="rg-brand-version">{t('app_suite')}</div>
            </div>
        """, unsafe_allow_html=True)

        # Language Selector (English / हिंदी)
        st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;'>{t('lang_selector_label')}</div>", unsafe_allow_html=True)
        render_language_selector()
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Active User & Role Card
        role_label = t("role_authority") if user.get("role") == "authority" else t("role_citizen")
        role_color = "#F97316" if user.get("role") == "authority" else "#10B981"
        st.markdown(f"""
            <div class="rg-session-card">
                <div class="rg-session-label">{t('active_credentials')}</div>
                <div class="rg-session-name">👤 {user.get('full_name')}</div>
                <div class="rg-role-chip" style="background: {role_color}18; color: {role_color}; border: 1px solid {role_color}44;">
                    ● {role_label}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Navigation Options (Bilingual)
        page_keys = [
            ("nav_overview", "overview"),
            ("nav_detect", "detect"),
            ("nav_reports", "reports"),
            ("nav_map", "map"),
            ("nav_queue", "queue"),
            ("nav_analytics", "analytics"),
            ("nav_export", "export"),
            ("nav_settings", "settings")
        ]

        page_display_names = [t(k) for k, _ in page_keys]
        selected_page_name = st.radio(
            "Navigation Menu",
            page_display_names,
            label_visibility="collapsed"
        )

        selected_page_key = "overview"
        for k, slug in page_keys:
            if t(k) == selected_page_name:
                selected_page_key = slug
                break

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        # Fast Role Switcher in Sidebar
        with st.expander(t("switch_persona"), expanded=False):
            if user.get("role") == "authority":
                if st.button(t("switch_to_citizen"), use_container_width=True):
                    switch_role("citizen")
                    st.rerun()
            else:
                if st.button(t("switch_to_authority"), use_container_width=True):
                    switch_role("authority")
                    st.rerun()

        # Model Readiness Diagnostic in Sidebar
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if model_status["is_custom"]:
            st.markdown(f"""
                <div style="padding: 10px 12px; border-radius: 8px; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); font-size: 0.74rem; color: #10B981;">
                    <span style="font-weight: 700;">{t('model_loaded')}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="padding: 10px 12px; border-radius: 8px; background: rgba(249, 115, 22, 0.08); border: 1px solid rgba(249, 115, 22, 0.3); font-size: 0.74rem; color: #FFA057;">
                    <span style="font-weight: 700;">{t('ai_core_ready')}</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="margin-top: 24px; padding: 12px; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.68rem; color: #71717A;">
                {t('footer_sub')}
            </div>
        """, unsafe_allow_html=True)

    # 3. Top Control Room Telemetry Header
    render_top_telemetry_bar(user, model_status)

    # 4. Page Routing
    if selected_page_key == "overview":
        render_overview()
    elif selected_page_key == "detect":
        render_detection_page()
    elif selected_page_key == "reports":
        render_reports_page()
    elif selected_page_key == "map":
        render_map_page()
    elif selected_page_key == "queue":
        render_queue_page()
    elif selected_page_key == "analytics":
        render_analytics_page()
    elif selected_page_key == "export":
        render_export_page()
    elif selected_page_key == "settings":
        render_settings_page()

if __name__ == "__main__":
    main()
