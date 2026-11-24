"""
ROADGUARD AI - AI Road Damage Detection Module
Upload road imagery or capture via camera, run YOLO damage detection,
calculate visual priority score, pin location interactively, and register official damage reports.
"""

import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
from pathlib import Path
import folium
from streamlit_folium import st_folium

from detection.detector import get_detector
from severity.scoring import calculate_visual_priority_score
from database.db import add_report
from utils.image_processing import (
    validate_uploaded_image,
    extract_exif_gps,
    save_image_to_disk
)
from utils.helpers import generate_report_id, get_priority_badge_html
from utils.auth import get_current_user
from utils.i18n import t
from config import (
    ROAD_TYPE_MODIFIERS,
    TRAFFIC_VOLUME_MODIFIERS,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    DEFAULT_MODEL_PATH,
    ASSETS_DIR
)

def render_detection_page():
    """Renders the AI detection and reporting interface."""
    st.markdown(f"""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>{t('breadcrumb_ops')}</span> / <span>COMPUTER VISION</span> / <span class="active">{t('nav_detect')}</span>
                </div>
                <h1>{t('detect_header')}</h1>
                <p class="rg-page-subtitle">
                    {t('detect_subtitle')}
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-ai">● INFERENCE ENGINE: STANDBY</span>
                <span class="rg-header-chip rg-chip-online">● EXIF GPS DECODER READY</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    detector = get_detector()
    status_info = detector.get_status_info()

    # Diagnostic Model Banner
    if status_info["is_custom"]:
        st.markdown(f"""
            <div class="rg-alert-info">
                <b>Custom YOLO Checkpoint Active:</b> Loaded trained road damage model weights from <code>{status_info['model_path']}</code>.
            </div>
        """, unsafe_allow_html=True)
    elif status_info["status"] == "BASE_MODEL_LOADED":
        st.markdown("""
            <div class="rg-alert-info">
                <b>Base YOLO Weights Active:</b> Using base checkpoint. For specialized road damage classes, place your fine-tuned weights at <code>models/best.pt</code>.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="rg-alert-warning">
                <b>No Trained Checkpoint at <code>models/best.pt</code>:</b>
                No fine-tuned road damage weights were detected in the <code>models/</code> directory.
                You can run real predictions by dropping your <code>best.pt</code> file into <code>models/</code> or uploading it in <b>Settings / About</b>,
                or check the box below to test the full pipeline in <b>Clearly Labeled Demo Simulation Mode</b>.
            </div>
        """, unsafe_allow_html=True)

    allow_demo = False
    if not status_info["exists"] and not status_info["is_custom"]:
        allow_demo = st.checkbox(
            "Enable Clearly Labeled Demo Simulation Mode (for pipeline testing without weights)",
            value=True,
            help="Generates sample annotated bounding boxes clearly marked as [DEMO] so you can test database saving and map pinning."
        )

    # Input Method Selection
    col_input_type, col_sample_btn = st.columns([2, 1])
    with col_input_type:
        input_method = st.radio(
            "Choose Image Input Method:",
            ["📁 Upload Image File", "📸 Use Device Camera"],
            horizontal=True
        )
    with col_sample_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        sample_img_path = ASSETS_DIR / "sample_road.jpg"
        if sample_img_path.exists():
            if st.button(t("detect_sample_btn"), use_container_width=True, help="Load the bundled sample road surface photo for immediate testing"):
                with open(sample_img_path, "rb") as f:
                    st.session_state["loaded_sample_bytes"] = f.read()
                    st.session_state["active_image_source"] = "sample"
                st.success("Sample road image loaded!")

    pil_image = None
    image_bytes = None
    exif_coords = None

    if st.session_state.get("active_image_source") == "sample" and "loaded_sample_bytes" in st.session_state:
        image_bytes = st.session_state["loaded_sample_bytes"]
        import io
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        st.caption("Currently inspecting: `assets/sample_road.jpg` (Sample Road Surface Photo)")
        if st.button("✕ Clear Sample Image"):
            del st.session_state["loaded_sample_bytes"]
            del st.session_state["active_image_source"]
            st.rerun()

    elif input_method == "📁 Upload Image File":
        uploaded_files = st.file_uploader(
            "Upload Road Surface Photo (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="High-angle photos with clear visibility of asphalt or pavement produce best results."
        )

        if uploaded_files:
            if len(uploaded_files) > 1:
                selected_name = st.selectbox(
                    f"Select Image to Analyze ({len(uploaded_files)} files uploaded):",
                    [f.name for f in uploaded_files]
                )
                image_file = next(f for f in uploaded_files if f.name == selected_name)
            else:
                image_file = uploaded_files[0]

            is_valid, validation_msg = validate_uploaded_image(image_file)
            if not is_valid:
                st.error(f"Image Error: {validation_msg}")
                return

            image_bytes = image_file.getvalue()
            pil_image = Image.open(image_file).convert("RGB")
            exif_coords = extract_exif_gps(image_bytes)

    else:
        cam_file = st.camera_input("Capture road photo using device camera")
        if cam_file:
            is_valid, validation_msg = validate_uploaded_image(cam_file)
            if not is_valid:
                st.error(f"Image Error: {validation_msg}")
                return
            image_bytes = cam_file.getvalue()
            pil_image = Image.open(cam_file).convert("RGB")

    if pil_image is None:
        st.info("Please upload, capture, or load a sample road surface image above to initiate AI damage detection.")
        return

    # Detection Controls
    with st.expander("⚙️ Advanced Detection & Context Parameters", expanded=False):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            conf_slider = st.slider("Confidence Threshold", 0.15, 0.90, float(CONFIDENCE_THRESHOLD), 0.05)
        with col_c2:
            iou_slider = st.slider("IoU NMS Threshold", 0.20, 0.80, float(IOU_THRESHOLD), 0.05)

    # Run Prediction Button
    if st.button(t("detect_analyze_btn"), type="primary", use_container_width=True):
        with st.spinner("Executing YOLO computer vision inference and computing visual priority index..."):
            pred_results = detector.predict(
                pil_image,
                conf_threshold=conf_slider,
                iou_threshold=iou_slider,
                allow_demo_fallback=allow_demo
            )
            st.session_state["current_prediction"] = pred_results
            st.session_state["uploaded_image_bytes"] = image_bytes
            st.session_state["exif_coords"] = exif_coords

    # Display Analysis Results if available in session state
    if "current_prediction" in st.session_state:
        pred = st.session_state["current_prediction"]

        if not pred.get("success"):
            st.error(pred.get("error", "Detection failed."))
            return

        st.markdown("<hr style='border-color: #1E293B; margin: 24px 0;'/>", unsafe_allow_html=True)

        if pred.get("is_demo"):
            st.warning("⚠️ **Notice:** Results below were generated in **Labeled Demo Simulation Mode** because `models/best.pt` is not present. This record will be flagged as `[DEMO]` in the database.")

        # Side-by-Side Image Comparison
        st.markdown("### 🖼️ Visual Damage Inspection")
        img_col1, img_col2 = st.columns(2)

        with img_col1:
            st.markdown("**Original Road Capture**")
            st.image(pred["original_image"], use_container_width=True)

        with img_col2:
            annotated_title = "**AI YOLO Detection Overlay**"
            if pred.get("is_demo"):
                annotated_title += " *(Demo Simulation)*"
            st.markdown(annotated_title)
            st.image(pred["annotated_image"], use_container_width=True)

        detections = pred.get("detections", [])

        # Interactive Location Picker
        st.markdown("### 📍 Geospatial Location & Map Pinning")
        st.write("Click anywhere on the map to pin the incident coordinates, or use preset GPS coordinates.")

        # Initialize session coordinates if not present
        if "detect_pin_lat" not in st.session_state:
            if st.session_state.get("exif_coords"):
                st.session_state["detect_pin_lat"] = st.session_state["exif_coords"][0]
                st.session_state["detect_pin_lon"] = st.session_state["exif_coords"][1]
                st.session_state["detect_loc_source"] = "Device GPS (Photo EXIF)"
            else:
                st.session_state["detect_pin_lat"] = 28.6139
                st.session_state["detect_pin_lon"] = 77.2090
                st.session_state["detect_loc_source"] = "Manual Coordinates"

        # Preset coordinate shortcuts
        p_c1, p_c2, p_c3, p_c4 = st.columns(4)
        with p_c1:
            if st.button("📍 Delhi PWD Ring Road", use_container_width=True):
                st.session_state["detect_pin_lat"] = 28.5700
                st.session_state["detect_pin_lon"] = 77.2400
                st.session_state["detect_loc_source"] = "Device GPS"
                st.session_state["detect_address"] = "Ring Road Flyover Corridor, Lajpat Nagar"
                st.rerun()
        with p_c2:
            if st.button("📍 Mumbai Western Express", use_container_width=True):
                st.session_state["detect_pin_lat"] = 19.0760
                st.session_state["detect_pin_lon"] = 72.8777
                st.session_state["detect_loc_source"] = "Device GPS"
                st.session_state["detect_address"] = "Western Express Highway, Bandra Hub"
                st.rerun()
        with p_c3:
            if st.button("📍 Connaught Circus Outer", use_container_width=True):
                st.session_state["detect_pin_lat"] = 28.6315
                st.session_state["detect_pin_lon"] = 77.2167
                st.session_state["detect_loc_source"] = "Manual Coordinates"
                st.session_state["detect_address"] = "Outer Connaught Circus, Lane 4"
                st.rerun()
        with p_c4:
            if st.button("🚫 Location Not Provided", use_container_width=True):
                st.session_state["detect_loc_source"] = "Not Provided"
                st.rerun()

        # Mini Folium interactive picker
        cur_lat = st.session_state.get("detect_pin_lat", 28.6139)
        cur_lon = st.session_state.get("detect_pin_lon", 77.2090)

        picker_map = folium.Map(
            location=[cur_lat, cur_lon],
            zoom_start=13,
            tiles="CartoDB dark_matter"
        )
        if st.session_state.get("detect_loc_source") != "Not Provided":
            folium.Marker(
                [cur_lat, cur_lon],
                tooltip="Pinned Damage Incident",
                icon=folium.Icon(color="red", icon="wrench", prefix="fa")
            ).add_to(picker_map)

        picker_output = st_folium(picker_map, width="100%", height=280, key="damage_map_picker")
        if picker_output and picker_output.get("last_clicked"):
            new_c_lat = round(picker_output["last_clicked"]["lat"], 6)
            new_c_lon = round(picker_output["last_clicked"]["lng"], 6)
            if (new_c_lat, new_c_lon) != (st.session_state["detect_pin_lat"], st.session_state["detect_pin_lon"]):
                st.session_state["detect_pin_lat"] = new_c_lat
                st.session_state["detect_pin_lon"] = new_c_lon
                st.session_state["detect_loc_source"] = "Map Pin"
                st.rerun()

        # Field Context Form for Scoring & Saving
        st.markdown("### 📋 Site Context & Explainable Priority Calculation")

        with st.form("road_report_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                road_type = st.selectbox("Roadway Classification", list(ROAD_TYPE_MODIFIERS.keys()), index=1)
            with c2:
                traffic_volume = st.selectbox("Traffic Volume Density", list(TRAFFIC_VOLUME_MODIFIERS.keys()), index=0)
            with c3:
                weather_condition = st.selectbox("Weather / Pavement State", ["Dry / Clear", "Wet / Post-Rain", "Overcast"], index=0)

            # Location Inputs
            st.markdown("##### 📍 Confirmed Location Parameters")
            loc_col1, loc_col2, loc_col3 = st.columns([1, 1, 1])

            with loc_col1:
                lat_input = st.number_input("Latitude", value=float(st.session_state.get("detect_pin_lat", 28.6139)), format="%.6f", step=0.0001)
            with loc_col2:
                lon_input = st.number_input("Longitude", value=float(st.session_state.get("detect_pin_lon", 77.2090)), format="%.6f", step=0.0001)
            with loc_col3:
                source_options = ["Device GPS", "Manual Coordinates", "Map Pin", "Not Provided"]
                curr_source = st.session_state.get("detect_loc_source", "Manual Coordinates")
                source_idx = source_options.index(curr_source) if curr_source in source_options else 1
                loc_source = st.selectbox("Location Source", source_options, index=source_idx)

            address_input = st.text_input(
                "Street Address / Landmark",
                value=st.session_state.get("detect_address", "Main Highway Corridor, Sector 4")
            )
            notes_input = st.text_area(
                "Field Inspector / Citizen Observations",
                placeholder="e.g., Noticeable vehicle swerving, loose gravel present around edge."
            )

            # Calculate Visual Priority Score
            assessment = calculate_visual_priority_score(
                detections=detections,
                road_type=road_type,
                traffic_volume=traffic_volume,
                weather_condition=weather_condition
            )

            # Display Priority Breakdown Box
            st.markdown(f"""
                <div class="rg-card" style="border-left: 4px solid {assessment.color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span class="badge-{assessment.band.lower()}">{assessment.label.upper()}</span>
                            <h2 style="color: {assessment.color}; margin: 8px 0 4px 0; font-size: 2.2rem; font-weight: 800;">
                                {assessment.score} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span>
                            </h2>
                            <p style="color: #F8FAFC; font-weight: 600; margin: 0;">{assessment.urgency}</p>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #94A3B8; font-size: 0.8rem; text-transform: uppercase;">Primary Detected Defect</div>
                            <div style="color: #F8FAFC; font-size: 1.1rem; font-weight: 700;">{assessment.primary_category}</div>
                            <div style="color: #94A3B8; font-size: 0.8rem; margin-top: 4px;">{len(detections)} Detected Regions</div>
                        </div>
                    </div>
                    <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08); font-size: 0.78rem; color: #94A3B8;">
                        <b>Score Breakdown:</b> Class Base ({assessment.factor_breakdown['class_points']} pts) +
                        Surface Coverage ({assessment.factor_breakdown['area_points']} pts, {assessment.factor_breakdown['total_area_ratio_pct']}%) +
                        Region Multiplicity ({assessment.factor_breakdown['count_points']} pts) +
                        Certainty ({assessment.factor_breakdown['confidence_points']} pts) ×
                        Context Multiplier ({assessment.factor_breakdown['combined_context_multiplier']}x).
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Engineering disclaimer
            st.caption(f"ℹ️ {assessment.technical_disclaimer}")

            # Submit Report Button
            save_submitted = st.form_submit_button("💾 Save Official Road Damage Report to Database", type="primary")

            if save_submitted:
                user = get_current_user() or {"full_name": "Citizen Reporter", "role": "citizen"}
                report_id = generate_report_id()

                # Save original and annotated images to disk
                orig_path = save_image_to_disk(pred["original_image"], report_id, "orig")
                annot_path = save_image_to_disk(pred["annotated_image"], report_id, "annotated")

                # Prepare report data dictionary
                report_data = {
                    "id": report_id,
                    "created_at": datetime.now().isoformat(),
                    "damage_type": pred["primary_type"],
                    "primary_class": assessment.primary_category,
                    "detection_count": len(detections),
                    "max_confidence": pred.get("max_confidence", 0.0),
                    "avg_confidence": pred.get("avg_confidence", 0.0),
                    "priority_score": assessment.score,
                    "priority_band": assessment.band,
                    "urgency_level": assessment.urgency,
                    "latitude": lat_input if loc_source != "Not Provided" else None,
                    "longitude": lon_input if loc_source != "Not Provided" else None,
                    "location_address": address_input,
                    "location_source": loc_source,
                    "road_type": road_type,
                    "traffic_volume": traffic_volume,
                    "weather_condition": weather_condition,
                    "original_image_path": orig_path,
                    "annotated_image_path": annot_path,
                    "status": "New",
                    "reporter_name": user.get("full_name", "Citizen Reporter"),
                    "reporter_role": user.get("role", "citizen"),
                    "notes": notes_input,
                    "score_breakdown": assessment.factor_breakdown,
                    "is_demo_data": 1 if pred.get("is_demo") else 0
                }

                # Save to SQLite
                saved_id = add_report(report_data, detections)
                st.success(f"✅ Road Damage Report successfully recorded! Assigned Tracking ID: **{saved_id}**")
                st.balloons()

        # Detection Results Table
        if detections:
            st.markdown("#### 🔍 Detected Damage Regions")
            det_table_data = []
            for idx, d in enumerate(detections, 1):
                det_table_data.append({
                    "Index": idx,
                    "Damage Class": d["class_name"],
                    "Confidence": f"{d['confidence']*100:.1f}%",
                    "Surface Area Ratio": f"{d['area_ratio']*100:.2f}%",
                    "Bounding Box [x1, y1, x2, y2]": f"[{d['box_x1']:.0f}, {d['box_y1']:.0f}, {d['box_x2']:.0f}, {d['box_y2']:.0f}]"
                })
            st.dataframe(pd.DataFrame(det_table_data), use_container_width=True)
