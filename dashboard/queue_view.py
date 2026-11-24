"""
ROADGUARD AI - Maintenance Priority Queue
Authority-facing triage queue ranking damaged road segments by visual priority score
to assist municipal engineering teams in allocating inspection and repair resources.
"""

import streamlit as st
import pandas as pd
import json

from database.db import get_filtered_reports, update_report_status, get_report_by_id
from utils.helpers import format_datetime, get_priority_badge_html, get_status_badge_html
from utils.auth import get_current_user, is_authority
from config import REPORT_STATUSES

def render_queue_page():
    """Renders the authority maintenance priority queue."""
    st.markdown("""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>MUNICIPAL OPERATIONS</span> / <span>FIELD DISPATCH</span> / <span class="active">PRIORITY QUEUE</span>
                </div>
                <h1>Municipal Maintenance Priority Queue</h1>
                <p class="rg-page-subtitle">
                    Algorithmic civil engineering triage queue prioritizing road repairs and field inspection crews by hazard severity.
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-ai">● WORK ORDER DISPATCH READY</span>
                <span class="rg-header-chip rg-chip-online">● RANKED BY VISUAL HAZARD SCORE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Authority Advisory Notice
    st.markdown("""
        <div class="rg-alert-info">
            <b>Decision-Support Notice:</b> This automated queue assists human municipal road engineers by ranking surface severity.
            Final engineering, safety, and contractor allocation decisions remain under human command.
        </div>
    """, unsafe_allow_html=True)

    # Queue Filters
    with st.expander("Filter Priority Queue", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            band_filter = st.selectbox("Priority Tier", ["All", "HIGH", "MEDIUM", "LOW"], key="q_band")
        with c2:
            cat_filter = st.selectbox("Damage Category", ["All", "Pothole", "Crack", "Alligator Crack", "Surface"], key="q_cat")
        with c3:
            status_filter = st.selectbox("Lifecycle Status", ["All (Unresolved)", "All"] + REPORT_STATUSES, index=0, key="q_status")
        with c4:
            search_loc = st.text_input("Filter Location / Corridor", placeholder="e.g. Ring Road, Highway", key="q_loc")

    actual_status = None
    if status_filter == "All (Unresolved)":
        actual_status = None  # Will filter out 'Resolved' in python
    elif status_filter != "All":
        actual_status = status_filter

    reports = get_filtered_reports(
        damage_type=cat_filter if cat_filter != "All" else None,
        priority_band=band_filter if band_filter != "All" else None,
        status=actual_status,
        search_query=search_loc,
        sort_by="priority_desc"  # Highest visual priority always first!
    )

    if status_filter == "All (Unresolved)":
        reports = [r for r in reports if r.get("status") != "Resolved"]

    if not reports:
        st.info("No active maintenance items found matching criteria.")
        return

    st.markdown(f"**{len(reports)} Active Maintenance Items Queued (Ranked by Visual Priority Score)**")

    for rank, rep in enumerate(reports, 1):
        rep_id = rep["id"]
        score = float(rep["priority_score"])
        band = rep["priority_band"].upper()
        p_badge = get_priority_badge_html(band, score)
        s_badge = get_status_badge_html(rep["status"])

        # Border color based on priority
        border_color = "#EF4444" if band == "HIGH" else ("#F59E0B" if band == "MEDIUM" else "#10B981")

        # Parse breakdown
        breakdown_text = "Surface defect detected"
        if rep.get("score_breakdown_json"):
            try:
                bd = json.loads(rep["score_breakdown_json"])
                breakdown_text = (
                    f"Class Severity: {bd.get('class_points',0)} pts | "
                    f"Surface Area: {bd.get('area_points',0)} pts ({bd.get('total_area_ratio_pct',0)}%) | "
                    f"Region Multiplier: {bd.get('count_points',0)} pts | "
                    f"Context Multiplier: {bd.get('combined_context_multiplier',1.0)}x"
                )
            except Exception:
                pass

        demo_tag = ' <span style="background:#06B6D422;color:#38BDF8;border:1px solid #38BDF866;padding:2px 6px;border-radius:4px;font-size:0.7rem;">DEMO</span>' if rep.get("is_demo_data") else ""

        with st.container():
            st.markdown(f"""
                <div class="rg-card" style="border-left: 5px solid {border_color}; margin-bottom: 14px; padding: 18px 22px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background: rgba(255,255,255,0.06); border-radius: 8px; padding: 4px 10px; font-weight: 800; font-size: 1.1rem; color: #94A3B8;">
                                #{rank}
                            </div>
                            <div>
                                <span style="font-size: 1.15rem; font-weight: 800; color: #F8FAFC;">{rep_id}</span>
                                {demo_tag}
                                <div style="color: #38BDF8; font-weight: 600; font-size: 0.9rem; margin-top: 2px;">
                                    {rep['damage_type']} ({rep['primary_class']})
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            {p_badge}
                            {s_badge}
                        </div>
                    </div>
                    <div style="margin-top: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; font-size: 0.85rem; color: #CBD5E1;">
                        <div>📍 <b>Location:</b> {rep['location_address'] or 'Not Provided'}</div>
                        <div>🛣️ <b>Roadway:</b> {rep['road_type']}</div>
                        <div>🚦 <b>Traffic:</b> {rep['traffic_volume']}</div>
                        <div>📅 <b>Reported:</b> {format_datetime(rep['created_at'])}</div>
                    </div>
                    <div style="margin-top: 10px; background: rgba(0,0,0,0.25); border-radius: 6px; padding: 8px 12px; font-size: 0.8rem; color: #94A3B8;">
                        <span style="color: #38BDF8; font-weight: 700;">Rank Logic:</span> {breakdown_text}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Quick Dispatch / Status Update Row
            with st.expander(f"⚡ Fast Action & Work Order: {rep_id}", expanded=False):
                if not is_authority():
                    st.info("👁️ **Citizen Mode (Read-Only):** Dispatching work orders and modifying repair lifecycle statuses is reserved for Municipal Authority personnel. Switch to Authority role in the sidebar to perform triage actions.")
                else:
                    col_a1, col_a2, col_a3 = st.columns([1.5, 2, 1])
                    with col_a1:
                        new_st = st.selectbox(
                            "Set Work Order Status",
                            REPORT_STATUSES,
                            index=REPORT_STATUSES.index(rep["status"]) if rep["status"] in REPORT_STATUSES else 0,
                            key=f"q_stat_{rep_id}"
                        )
                    with col_a2:
                        action_note = st.text_input(
                            "Dispatch Instruction",
                            placeholder="e.g., Crew #2 scheduled for asphalt milling on Monday",
                            key=f"q_note_{rep_id}"
                        )
                    with col_a3:
                        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("Apply Status", key=f"q_btn_{rep_id}"):
                            usr = get_current_user() or {"full_name": "Road Operations"}
                            update_report_status(rep_id, new_st, f"{usr.get('full_name')} (Maintenance Authority)", action_note)
                            st.success(f"{rep_id} updated to {new_st}")
                            st.rerun()
