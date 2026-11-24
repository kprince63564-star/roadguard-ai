"""
ROADGUARD AI - Damage Reports Management
Comprehensive CRUD and lifecycle management interface for recorded road damage incidents.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from database.db import (
    get_filtered_reports,
    get_report_by_id,
    update_report_status,
    delete_report
)
from utils.helpers import (
    format_datetime,
    get_priority_badge_html,
    get_status_badge_html
)
from utils.auth import get_current_user, is_authority
from utils.pdf_generator import generate_pdf_report
from config import REPORT_STATUSES, PRIORITY_BANDS

def render_reports_page():
    """Renders the damage reports exploration and lifecycle management page."""
    st.markdown("""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>MUNICIPAL OPERATIONS</span> / <span>INCIDENTS</span> / <span class="active">REPORTS MANAGEMENT</span>
                </div>
                <h1>Road Damage Reports Management</h1>
                <p class="rg-page-subtitle">
                    Inspect recorded damage reports, audit status transitions, filter by priority, and manage repair workflows.
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-online">● AUDIT TRAIL LOGGING ACTIVE</span>
                <span class="rg-header-chip rg-chip-ai">● SQLITE DB ENCRYPTED/SALTED</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Search & Filter Controls Bar
    with st.expander("🔍 Search, Filter & Sort Controls", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1, 1, 1])

        with f_col1:
            search_query = st.text_input("Search Reports", placeholder="Filter by ID, Street, Notes, or Defect...")

        with f_col2:
            status_filter = st.selectbox("Status", ["All"] + REPORT_STATUSES)

        with f_col3:
            priority_filter = st.selectbox("Priority Band", ["All", "HIGH", "MEDIUM", "LOW"])

        with f_col4:
            sort_by = st.selectbox(
                "Sort By",
                [("date_desc", "Newest First"), ("date_asc", "Oldest First"),
                 ("priority_desc", "Highest Priority First"), ("priority_asc", "Lowest Priority First")],
                format_func=lambda x: x[1]
            )[0]

    # Query filtered reports from database
    reports = get_filtered_reports(
        priority_band=priority_filter if priority_filter != "All" else None,
        status=status_filter if status_filter != "All" else None,
        search_query=search_query,
        sort_by=sort_by
    )

    if not reports:
        st.info("No road damage reports match your current filter criteria.")
        return

    st.markdown(f"**Found {len(reports)} matching report(s)**")

    # Display Reports List / Cards
    for rep in reports:
        rep_id = rep["id"]
        is_demo = bool(rep.get("is_demo_data"))
        demo_tag = ' <span style="background:#06B6D422;color:#38BDF8;border:1px solid #38BDF866;padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:700;">DEMO DATA</span>' if is_demo else ""

        with st.container():
            p_badge = get_priority_badge_html(rep["priority_band"], rep["priority_score"])
            s_badge = get_status_badge_html(rep["status"])

            st.markdown(f"""
                <div class="rg-card" style="margin-bottom: 12px; padding: 16px 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-size: 1.15rem; font-weight: 800; color: #F8FAFC; margin-right: 8px;">{rep_id}</span>
                            {demo_tag}
                            <span style="margin-left: 8px; color: #94A3B8; font-size: 0.85rem;">{format_datetime(rep['created_at'])}</span>
                        </div>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            {p_badge}
                            {s_badge}
                        </div>
                    </div>
                    <div style="margin-top: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="color: #38BDF8; font-weight: 600;">{rep['damage_type']}</span>
                            <span style="color: #64748B; margin: 0 8px;">•</span>
                            <span style="color: #CBD5E1;">📍 {rep['location_address'] or 'Location not specified'}</span>
                        </div>
                        <div style="color: #94A3B8; font-size: 0.8rem;">
                            Reported by: <b>{rep['reporter_name']}</b>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Details & Actions Expander
            with st.expander(f"🔎 View Details & Manage Report: {rep_id}", expanded=False):
                full_rep = get_report_by_id(rep_id)
                if not full_rep:
                    st.error("Report details not found.")
                    continue

                col_img, col_info = st.columns([1, 1])

                with col_img:
                    annot_path = full_rep.get("annotated_image_path")
                    orig_path = full_rep.get("original_image_path")

                    if annot_path and Path(annot_path).exists():
                        st.image(annot_path, caption=f"Annotated Inspection ({rep_id})", use_container_width=True)
                    elif orig_path and Path(orig_path).exists():
                        st.image(orig_path, caption=f"Original Field Image ({rep_id})", use_container_width=True)
                    else:
                        st.caption("No image file on disk for this record.")

                with col_info:
                    st.markdown("##### 📌 Incident Assessment")
                    st.write(f"**Damage Class:** {full_rep.get('primary_class')}")
                    st.write(f"**Detection Count:** {full_rep.get('detection_count')} defects")
                    st.write(f"**Max AI Confidence:** {full_rep.get('max_confidence', 0)*100:.1f}%")
                    st.write(f"**Road Type:** {full_rep.get('road_type')}")
                    st.write(f"**Traffic Density:** {full_rep.get('traffic_volume')}")
                    st.write(f"**Weather Condition:** {full_rep.get('weather_condition')}")

                    lat = full_rep.get("latitude")
                    lon = full_rep.get("longitude")
                    if lat is not None and lon is not None:
                        st.write(f"**Coordinates:** `{lat:.5f}, {lon:.5f}` ({full_rep.get('location_source')})")
                    else:
                        st.write("**Coordinates:** *Not Provided*")

                    if full_rep.get("notes"):
                        st.info(f"**Inspector Notes:** {full_rep['notes']}")

                # Status Lifecycle Management
                st.markdown("##### 🔄 Update Maintenance Status")
                if not is_authority():
                    st.info("👁️ **Citizen Mode (Read-Only):** Updating report repair lifecycle status is reserved for Municipal Authority personnel. Switch to Authority role in the sidebar to modify.")
                else:
                    u_col1, u_col2, u_col3 = st.columns([1.5, 2, 1])

                    curr_status = full_rep["status"]
                    curr_idx = REPORT_STATUSES.index(curr_status) if curr_status in REPORT_STATUSES else 0

                    with u_col1:
                        new_status = st.selectbox(
                            "Change Status",
                            REPORT_STATUSES,
                            index=curr_idx,
                            key=f"status_select_{rep_id}"
                        )

                    with u_col2:
                        status_comment = st.text_input(
                            "Audit Comment / Work Order Note",
                            placeholder="e.g. Dispatched asphalt repair truck #4",
                            key=f"status_comment_{rep_id}"
                        )

                    with u_col3:
                        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("Update Status", key=f"btn_update_{rep_id}"):
                            current_user = get_current_user() or {"full_name": "Municipal Officer"}
                            changed_by = f"{current_user.get('full_name')} ({current_user.get('role', 'authority')})"
                            success = update_report_status(rep_id, new_status, changed_by, status_comment)
                            if success:
                                st.success(f"Status for {rep_id} updated to {new_status}!")
                                st.rerun()

                # Granular Detections
                detections = full_rep.get("detections", [])
                if detections:
                    st.markdown("##### 📐 Detected Bounding Regions")
                    det_data = []
                    for d in detections:
                        det_data.append({
                            "Class": d["class_name"],
                            "Confidence": f"{d['confidence']*100:.1f}%",
                            "Surface Area Ratio": f"{d['area_ratio']*100:.2f}%",
                            "Bounding Box": f"[{d['box_x1']:.0f}, {d['box_y1']:.0f}, {d['box_x2']:.0f}, {d['box_y2']:.0f}]"
                        })
                    st.dataframe(pd.DataFrame(det_data), use_container_width=True)

                # Status Audit Trail History
                history = full_rep.get("history", [])
                if history:
                    st.markdown("##### 📜 Audit History Trail")
                    hist_data = []
                    for h in history:
                        hist_data.append({
                            "Timestamp": format_datetime(h["timestamp"]),
                            "Previous Status": h["previous_status"] or "Initial Creation",
                            "New Status": h["new_status"],
                            "Modified By": h["changed_by"],
                            "Comments": h["comments"] or ""
                        })
                    st.dataframe(pd.DataFrame(hist_data), use_container_width=True)

                # Action Buttons Row: PDF Download & Delete
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                act_col1, act_col2 = st.columns([1, 1])

                with act_col1:
                    if st.button(f"📄 Generate Official PDF Report ({rep_id})", key=f"btn_pdf_{rep_id}"):
                        with st.spinner("Generating PDF inspection order..."):
                            pdf_file_path = generate_pdf_report(full_rep)
                            with open(pdf_file_path, "rb") as f:
                                pdf_bytes = f.read()
                            st.download_button(
                                label="⬇️ Download Generated PDF",
                                data=pdf_bytes,
                                file_name=f"RoadGuard_Report_{rep_id}.pdf",
                                mime="application/pdf",
                                key=f"dl_pdf_{rep_id}"
                            )

                with act_col2:
                    if is_authority():
                        # Safe delete with confirmation
                        del_confirm = st.checkbox(f"Confirm permanent deletion of {rep_id}", key=f"del_chk_{rep_id}")
                        if del_confirm:
                            if st.button(f"🗑️ Delete Report {rep_id}", type="primary", key=f"btn_del_{rep_id}"):
                                delete_report(rep_id)
                                st.warning(f"Report {rep_id} has been permanently deleted.")
                                st.rerun()
                    else:
                        st.caption("🔒 Report deletion restricted to Municipal Authority.")
