"""
ROADGUARD AI - Overview Dashboard
Executive smart-city dashboard displaying real-time damage statistics,
interactive Plotly visualizations, recent field reports, and bilingual support (EN/HI).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.db import (
    get_dashboard_stats,
    get_all_reports,
    get_recent_reports,
    seed_demo_data_if_empty
)
from utils.helpers import format_datetime, get_priority_badge_html, get_status_badge_html
from utils.i18n import t, get_current_language
from config import STATUS_COLORS, PRIORITY_BANDS, OUTPUTS_DIR

def render_overview():
    """Renders the primary executive overview dashboard with i18n support."""
    st.markdown(f"""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>{t('breadcrumb_ops')}</span> / <span>{t('breadcrumb_surface')}</span> / <span class="active">{t('breadcrumb_overview')}</span>
                </div>
                <h1>{t('header_title')}</h1>
                <p class="rg-page-subtitle">
                    {t('header_subtitle')}
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-online">{t('chip_gis')}</span>
                <span class="rg-header-chip rg-chip-ai">{t('chip_ai')}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # User Tutorial & Walkthrough Video Player
    video_path = OUTPUTS_DIR / "roadguard_tutorial.mp4"
    if not video_path.exists():
        video_path = OUTPUTS_DIR / "roadguard_explainer.mp4"

    if video_path.exists():
        with st.expander(t("video_expander_title"), expanded=False):
            col_v1, col_v2 = st.columns([3, 1])
            with col_v1:
                st.video(str(video_path))
            with col_v2:
                st.markdown(f"##### {t('video_pillars_title')}")
                st.markdown(f"""
                - {t('video_step1')}
                - {t('video_step2')}
                - {t('video_step3')}
                - {t('video_step4')}
                """)
                with open(video_path, "rb") as vf:
                    st.download_button(
                        label=t("download_video_btn"),
                        data=vf.read(),
                        file_name="ROADGUARD_AI_Tutorial.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                srt_path = OUTPUTS_DIR / "roadguard_tutorial.srt"
                if not srt_path.exists():
                    srt_path = OUTPUTS_DIR / "roadguard_explainer.srt"
                if srt_path.exists():
                    with open(srt_path, "rb") as sf:
                        st.download_button(
                            label=t("download_subtitles_btn"),
                            data=sf.read(),
                            file_name="roadguard_tutorial.srt",
                            mime="text/plain",
                            use_container_width=True
                        )

            # Synchronized Step-by-Step Guide Viewer (Bilingual)
            with st.expander(t("guide_script_title"), expanded=False):
                st.markdown("""
                | Time / समय | Step / चरण | English Instructions | हिंदी मार्गदर्शन (Hindi Guide) |
                |:---|:---|:---|:---|
                | **0:00 - 0:10** | **Overview** | "Welcome to ROADGUARD AI — your complete guide to smart road health inspection and maintenance triage." | "रोडगार्ड एआई में आपका स्वागत है — सड़क स्वास्थ्य निरीक्षण और रखरखाव का संपूर्ण मार्गदर्शक।" |
                | **0:10 - 0:20** | **Step 1: Capture** | "Open 'Detect Road Damage'. Use device camera on site or upload road imagery." | "चरण 1: 'सड़क क्षति पहचानें' टैब खोलें। मौके पर कैमरा से फोटो लें या फाइल अपलोड करें।" |
                | **0:20 - 0:31** | **Step 2: AI Vision** | "Tap 'Analyze Road Damage'. YOLOv8 detects potholes and cracks with bounding boxes in milliseconds." | "चरण 2: 'विश्लेषण करें' बटन दबाएं। YOLOv8 गड्ढों और दरारों का सटीक पता लगाता है।" |
                | **0:31 - 0:42** | **Step 3: GIS Map** | "GPS is auto-extracted from photo EXIF, or click directly on the interactive GIS map to pin." | "चरण 3: फोटो से जीपीएस अपने आप मिलता है, या लाइव जीआईएस नक्शे पर क्लिक करके स्थान तय करें।" |
                | **0:42 - 0:53** | **Step 4: Priority** | "The explainable engine computes a 0 to 100 hazard index factoring road classification and traffic volume." | "चरण 4: पारदर्शी स्कोर इंजन सड़क प्रकार और यातायात घनत्व के आधार पर 0 से 100 स्कोर तय करता है।" |
                | **0:53 - 1:04** | **Step 5: Work Order**| "Save to database to receive a tracking ID. Update repair stages and export official PDF work orders." | "चरण 5: डेटाबेस में सहेजें, ट्रैकिंग आईडी प्राप्त करें और आधिकारिक पीडीएफ वर्क ऑर्डर डाउनलोड करें।" |
                | **1:04 - 1:13** | **Ready to Use** | "You're now ready to use ROADGUARD AI! Switch to Hindi or English anytime in the sidebar." | "अब आप तैयार हैं! साइडबार से कभी भी हिंदी या अंग्रेजी चुनें और सुरक्षित सड़कों के निर्माण में मदद करें।" |
                """)

    # Fetch real stats from database
    stats = get_dashboard_stats()
    all_reports = get_all_reports()

    # Empty State Handling
    if stats["total_reports"] == 0:
        st.markdown(f"""
            <div class="rg-card rg-empty-state">
                <div class="rg-empty-icon">🛣️</div>
                <h3>{t('empty_title')}</h3>
                <p>{t('empty_desc')}</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(t("empty_load_btn"), use_container_width=True):
                seed_demo_data_if_empty()
                st.success("Loaded realistic municipal sample records.")
                st.rerun()
        return

    # Critical Incident Alert Bar (if high-priority items exist)
    if stats['high_priority_count'] > 0:
        st.markdown(f"""
            <div style="background: linear-gradient(90deg, rgba(239,68,68,0.14) 0%, rgba(220,38,38,0.06) 100%); border: 1px solid rgba(239,68,68,0.35); border-left: 4px solid #EF4444; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem;">⚠️</span>
                    <div>
                        <strong style="color: #F87171; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.05em;">{t('priority_alert_title')}</strong>
                        <span style="color: #F8FAFC; font-size: 0.88rem; margin-left: 6px;">
                            <b>{stats['high_priority_count']} {t('priority_alert_desc')}</b>
                        </span>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: rgba(239,68,68,0.2); color: #EF4444; border: 1px solid rgba(239,68,68,0.4); font-size: 0.72rem; font-weight: 700; padding: 3px 10px; border-radius: 9999px;">
                        {t('urgent_triage_chip')}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 1. Primary Metric Row (4 KPI Cards)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="rg-metric-card">
                <div class="rg-metric-label">
                    <span style="color: #F97316;">📁</span> {t('kpi_total_reports')}
                </div>
                <div class="rg-metric-value">{stats['total_reports']}</div>
                <div class="rg-metric-subtext">{t('kpi_total_reports_sub')}</div>
                <div class="rg-metric-delta rg-delta-up">{t('kpi_total_reports_delta')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="rg-metric-card">
                <div class="rg-metric-label">
                    <span style="color: #EF4444;">🕳️</span> {t('kpi_potholes')}
                </div>
                <div class="rg-metric-value" style="color: #EF4444;">{stats['total_potholes']}</div>
                <div class="rg-metric-subtext">{t('kpi_potholes_sub')}</div>
                <div class="rg-metric-delta rg-delta-down">{t('kpi_potholes_delta')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="rg-metric-card">
                <div class="rg-metric-label">
                    <span style="color: #F59E0B;">⚡</span> {t('kpi_cracks')}
                </div>
                <div class="rg-metric-value" style="color: #F59E0B;">{stats['total_cracks']}</div>
                <div class="rg-metric-subtext">{t('kpi_cracks_sub')}</div>
                <div class="rg-metric-delta rg-delta-up">{t('kpi_cracks_delta')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="rg-metric-card">
                <div class="rg-metric-label">
                    <span style="color: #DC2626;">🚨</span> {t('kpi_high_priority')}
                </div>
                <div class="rg-metric-value" style="color: #DC2626;">{stats['high_priority_count']}</div>
                <div class="rg-metric-subtext">{t('kpi_high_priority_sub')}</div>
                <div class="rg-metric-delta rg-delta-down">{t('kpi_high_priority_delta')}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Secondary KPI Row (3 Operational Cards)
    col5, col6, col7 = st.columns(3)
    with col5:
        st.markdown(f"""
            <div class="rg-metric-card">
                <div class="rg-metric-label">
                    <span style="color: #F59E0B;">⏳</span> {t('kpi_awaiting')}
                </div>
                <div class="rg-metric-value" style="color: #F59E0B;">{stats['awaiting_inspection']}</div>
                <div class="rg-metric-subtext">{t('kpi_awaiting_sub')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
            <div class="rg-metric-card">
                <div class="rg-metric-label">
                    <span style="color: #10B981;">✅</span> {t('kpi_repaired')}
                </div>
                <div class="rg-metric-value" style="color: #10B981;">{stats['marked_repaired']}</div>
                <div class="rg-metric-subtext">{t('kpi_repaired_sub')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col7:
        avg_score = stats['avg_priority_score']
        score_color = "#EF4444" if avg_score >= 70 else ("#F59E0B" if avg_score >= 40 else "#10B981")
        st.markdown(f"""
            <div class="rg-metric-card">
                <div class="rg-metric-label">
                    <span style="color: {score_color};">📊</span> {t('kpi_avg_score')}
                </div>
                <div class="rg-metric-value" style="color: {score_color};">{avg_score:.1f} <span style="font-size: 1.1rem; color: #94A3B8; font-weight: 500;">/100</span></div>
                <div class="rg-metric-subtext">{t('kpi_avg_score_sub')}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 2. Charts Section
    df = pd.DataFrame(all_reports)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="rg-card-title"><span>📊</span> {t("chart_damage_dist")}</div>', unsafe_allow_html=True)
        if not df.empty and "damage_type" in df.columns:
            damage_counts = df["damage_type"].value_counts().reset_index()
            damage_counts.columns = ["Damage Type", "Count"]

            fig_type = px.pie(
                damage_counts,
                names="Damage Type",
                values="Count",
                hole=0.6,
                color_discrete_sequence=["#EF4444", "#F97316", "#F59E0B", "#EAB308", "#10B981"]
            )
            fig_type.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Plus Jakarta Sans, sans-serif"),
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
            )
            fig_type.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#14171E', width=2))
            )
            st.plotly_chart(fig_type, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="rg-card-title"><span>🎯</span> {t("chart_priority_triage")}</div>', unsafe_allow_html=True)
        if not df.empty and "priority_band" in df.columns:
            band_counts = df["priority_band"].value_counts().reset_index()
            band_counts.columns = ["Priority Band", "Count"]
            band_color_map = {"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#10B981"}

            fig_band = px.bar(
                band_counts,
                x="Priority Band",
                y="Count",
                color="Priority Band",
                color_discrete_map=band_color_map,
                text="Count"
            )
            fig_band.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Plus Jakarta Sans, sans-serif"),
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor="#252933", title="Incidents"),
                showlegend=False
            )
            fig_band.update_traces(
                textposition='outside',
                marker=dict(line=dict(color='rgba(255,255,255,0.1)', width=1))
            )
            st.plotly_chart(fig_band, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Lifecycle Pipeline & Top Locations
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="rg-card-title"><span>🔄</span> {t("chart_status_pipeline")}</div>', unsafe_allow_html=True)
        if not df.empty and "status" in df.columns:
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]

            fig_status = px.bar(
                status_counts,
                y="Status",
                x="Count",
                orientation="h",
                color="Status",
                color_discrete_map=STATUS_COLORS,
                text="Count"
            )
            fig_status.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Plus Jakarta Sans, sans-serif"),
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor="#252933", title="Reports"),
                yaxis=dict(showgrid=False, title=""),
                showlegend=False
            )
            fig_status.update_traces(
                textposition='outside',
                marker=dict(line=dict(color='rgba(255,255,255,0.1)', width=1))
            )
            st.plotly_chart(fig_status, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col4:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="rg-card-title"><span>📍</span> {t("chart_hotspots")}</div>', unsafe_allow_html=True)
        if not df.empty and "location_address" in df.columns:
            top_locs = df["location_address"].value_counts().head(5).reset_index()
            top_locs.columns = ["Location", "Reports"]

            fig_loc = px.bar(
                top_locs,
                x="Reports",
                y="Location",
                orientation="h",
                color_discrete_sequence=["#F97316"],
                text="Reports"
            )
            fig_loc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Plus Jakarta Sans, sans-serif"),
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor="#252933", title="Recorded Incidents"),
                yaxis=dict(showgrid=False, autorange="reversed", title="")
            )
            fig_loc.update_traces(
                textposition='outside',
                marker=dict(line=dict(color='rgba(249,115,22,0.4)', width=1))
            )
            st.plotly_chart(fig_loc, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. Recent Reports Table
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="rg-card-title"><span>🕒</span> {t("table_title")}</div>', unsafe_allow_html=True)

    recent = get_recent_reports(limit=8)
    if recent:
        table_rows = []
        for r in recent:
            p_badge = get_priority_badge_html(r["priority_band"], r["priority_score"])
            s_badge = get_status_badge_html(r["status"])
            demo_tag = ' <span style="background:rgba(249,115,22,0.15);color:#FFA057;border:1px solid rgba(249,115,22,0.35);padding:1px 6px;border-radius:4px;font-size:0.65rem;font-weight:700;">DEMO</span>' if r.get("is_demo_data") else ""
            table_rows.append({
                t("col_incident_id"): f"<code>{r['id']}</code>{demo_tag}",
                t("col_classification"): f"<strong style='color:#F8FAFC;'>{r['damage_type']}</strong>",
                t("col_location"): f"<span style='color:#CBD5E1;'>📍 {r['location_address'] or 'Not Provided'}</span>",
                t("col_priority"): p_badge,
                t("col_status"): s_badge,
                t("col_timestamp"): f"<span style='font-family: monospace; color:#94A3B8; font-size:0.8rem;'>{format_datetime(r['created_at'])}</span>"
            })

        rec_df = pd.DataFrame(table_rows)
        st.write(rec_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
