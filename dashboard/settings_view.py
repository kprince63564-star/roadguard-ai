"""
ROADGUARD AI - Settings, System Diagnostics & Model Setup
Configuration portal for AI YOLO model weights, user role switcher,
database maintenance, and engineering specifications.
"""

import streamlit as st
from pathlib import Path

from detection.detector import get_detector
from database.db import seed_demo_data_if_empty, get_connection
from utils.auth import get_current_user, switch_role
from config import (
    DEFAULT_MODEL_PATH,
    MODELS_DIR,
    DB_PATH,
    UPLOADS_DIR,
    OUTPUTS_DIR
)

def render_settings_page():
    """Renders the settings and system administration dashboard."""
    st.markdown("""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>MUNICIPAL OPERATIONS</span> / <span>ADMINISTRATION</span> / <span class="active">SYSTEM SETTINGS</span>
                </div>
                <h1>Platform Settings & Model Diagnostics</h1>
                <p class="rg-page-subtitle">
                    Configure AI model checkpoints, manage access credentials, and audit storage diagnostics.
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-ai">● ULTRALYTICS YOLOv8</span>
                <span class="rg-header-chip rg-chip-online">● RBAC ACCESS: SHA-256</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 AI Model Setup & Loader",
        "👤 User Roles & Auth",
        "💾 Database & File Storage",
        "ℹ️ System Architecture & About"
    ])

    # Tab 1: AI Model Setup
    with tab1:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">🤖 YOLO Model Checkpoint Configuration</div>', unsafe_allow_html=True)

        detector = get_detector()
        status_info = detector.get_status_info()

        st.write(f"**Current Model Target:** `models/best.pt`")
        st.write(f"**Loaded Checkpoint State:** `{status_info['status']}`")
        st.write(f"**Custom Fine-Tuned Model Active:** `{status_info['is_custom']}`")

        if status_info["is_custom"]:
            st.success(f"✅ Active custom weights loaded from {status_info['model_path']}")
            if status_info["classes"]:
                st.write("**Registered Damage Classes:**")
                st.json(status_info["classes"])
        else:
            st.markdown("""
                <div class="rg-alert-warning">
                    <b>No weights located at <code>models/best.pt</code></b><br/>
                    ROADGUARD AI is architected to seamlessly load fine-tuned Ultralytics YOLO models (e.g., trained on the RDD2022 Road Damage Dataset or Roboflow Road Damage dataset).
                </div>
            """, unsafe_allow_html=True)

        st.markdown("##### 📤 Upload Checkpoint Directly via Web Browser:")
        st.write("Upload your trained PyTorch YOLO model weights (`best.pt`) directly into the `models/` directory:")
        uploaded_pt = st.file_uploader(
            "Upload YOLO Weights (.pt)",
            type=["pt"],
            key="weights_pt_uploader",
            help="Upload your trained road damage checkpoint (e.g., best.pt)"
        )
        if uploaded_pt:
            target_pt_path = MODELS_DIR / "best.pt"
            with open(target_pt_path, "wb") as f:
                f.write(uploaded_pt.getbuffer())
            reload_ok, reload_msg = detector.reload_model(target_pt_path)
            if reload_ok:
                st.success(f"🎉 Checkpoint uploaded and loaded into `{target_pt_path.name}` successfully!")
                st.rerun()
            else:
                st.error(f"Failed to load uploaded weights: {reload_msg}")

        st.markdown("##### 📥 Or Place Your Checkpoint Manually on Disk:")
        st.markdown("""
        1. Place your PyTorch YOLO model checkpoint (e.g. `best.pt`) inside the project `models/` directory:
           ```bash
           ROADGUARD-AI/
           └── models/
               └── best.pt
           ```
        2. Once present, click **Reload Checkpoint** below to activate it for live AI inference.
        """)

        st.markdown("##### 🔄 Custom Checkpoint Switcher / Reload")
        custom_path_input = st.text_input("Model Checkpoint Path (.pt)", value=str(DEFAULT_MODEL_PATH))
        if st.button("Load Specified Checkpoint"):
            success, msg = detector.reload_model(custom_path_input)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: User Roles & Auth
    with tab2:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">👤 Role-Based Access Control (RBAC)</div>', unsafe_allow_html=True)

        curr_user = get_current_user() or {"full_name": "Municipal Road Engineer", "role": "authority"}
        st.write(f"**Active User:** {curr_user.get('full_name')}")
        st.write(f"**Active Role:** `{curr_user.get('role').upper()}`")

        st.markdown("##### Switch Role for Testing:")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("Switch to Municipal Authority (Admin)", use_container_width=True):
                switch_role("authority")
                st.success("Switched to Municipal Authority role.")
                st.rerun()
        with col_r2:
            if st.button("Switch to Citizen Reporter", use_container_width=True):
                switch_role("citizen")
                st.success("Switched to Citizen Reporter role.")
                st.rerun()

        st.markdown("""
        - **Municipal Authority:** Accesses the Maintenance Priority Queue, updates repair lifecycle statuses, downloads executive PDF work orders.
        - **Citizen Reporter:** Captures and uploads road defect reports, views public live damage map.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: Database & Storage
    with tab3:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">💾 Storage & Database Telemetry</div>', unsafe_allow_html=True)

        db_size_kb = DB_PATH.stat().st_size / 1024 if DB_PATH.exists() else 0
        uploads_count = len(list(UPLOADS_DIR.glob("*.*"))) if UPLOADS_DIR.exists() else 0
        outputs_count = len(list(OUTPUTS_DIR.glob("*.*"))) if OUTPUTS_DIR.exists() else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Database File Size", f"{db_size_kb:.1f} KB")
        with c2:
            st.metric("Uploaded Images", uploads_count)
        with c3:
            st.metric("Annotated Outputs", outputs_count)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Database Actions:")
        col_db1, col_db2 = st.columns(2)
        with col_db1:
            if st.button("📥 Load Labeled Demo Records (if empty)", use_container_width=True):
                seed_demo_data_if_empty()
                st.success("Loaded demo records.")
                st.rerun()

        with col_db2:
            confirm_reset = st.checkbox("Confirm database reset")
            if confirm_reset and st.button("⚠️ Clear All Reports", type="primary", use_container_width=True):
                conn = get_connection()
                conn.execute("DELETE FROM detections")
                conn.execute("DELETE FROM status_history")
                conn.execute("DELETE FROM reports")
                conn.commit()
                conn.close()
                st.warning("All records deleted from database.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 4: About & Engineering Specifications
    with tab4:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">ℹ️ ROADGUARD AI System Architecture</div>', unsafe_allow_html=True)
        st.markdown("""
        **ROADGUARD AI** is an intelligent road surface diagnostic and municipal triage platform.

        ### Key Subsystems:
        1. **Vision Inference Engine:** Powered by Ultralytics YOLO with bounding box localization and multi-class classification.
        2. **Explainable Priority Scoring:** Calculates transparent 0–100 triage scores based on defect severity, pixel coverage ratio, density, and roadway traffic context.
        3. **Geospatial Intelligence:** Interactive GIS mapping with Folium and OpenStreetMap.
        4. **Relational Database:** SQLite with complete relational tables for incidents, detections, and audit logs.
        5. **Automated Documentation:** Instant PDF municipal work order generation via ReportLab.
        
        ### Engineering Notice:
        *Visual priority scores are computed strictly from 2D surface photography to prioritize human municipal inspection triage. A 2D photograph cannot measure pavement depth, sub-base compaction, or true load capacity.*
        """)

        video_p = OUTPUTS_DIR / "roadguard_explainer.mp4"
        if video_p.exists():
            st.markdown("##### 🎬 System Architecture Explainer Video (720p HD)")
            st.video(str(video_p))
            with open(video_p, "rb") as f:
                st.download_button("⬇️ Download Full Explainer Video (.mp4)", f.read(), file_name="ROADGUARD_AI_Explainer.mp4", mime="video/mp4")
        st.markdown('</div>', unsafe_allow_html=True)
