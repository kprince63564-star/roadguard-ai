"""
ROADGUARD AI - Live Damage Map
Interactive geospatial intelligence map displaying road damage hazards,
priority-coded markers, popup diagnostics, and unlocated incident triage.
"""

import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd

from pathlib import Path
from PIL import Image

from database.db import get_filtered_reports
from utils.helpers import format_datetime, get_priority_badge_html
from utils.image_processing import image_to_base64
from config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, PRIORITY_BANDS, REPORT_STATUSES

def render_map_page():
    """Renders the interactive geospatial road damage map."""
    st.markdown("""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>MUNICIPAL OPERATIONS</span> / <span>GIS TELEMETRY</span> / <span class="active">LIVE DAMAGE MAP</span>
                </div>
                <h1>Live Road Damage Geospatial GIS Map</h1>
                <p class="rg-page-subtitle">
                    Interactive spatial visualization of verified road surface defects color-coded by visual priority score with cluster analysis.
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-online">● CARTO DARK-MATTER GIS TILES</span>
                <span class="rg-header-chip rg-chip-ai">● SPATIAL CLUSTERING ACTIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Filter Controls
    with st.expander("📍 Geospatial Layer Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            priority_filter = st.selectbox("Priority Level", ["All", "HIGH", "MEDIUM", "LOW"], key="map_p_filter")
        with col2:
            status_filter = st.selectbox("Maintenance Status", ["All"] + REPORT_STATUSES, key="map_s_filter")
        with col3:
            damage_filter = st.selectbox("Damage Category", ["All", "Pothole", "Crack", "Alligator Crack"], key="map_d_filter")

    # Fetch reports matching filter
    reports = get_filtered_reports(
        damage_type=damage_filter if damage_filter != "All" else None,
        priority_band=priority_filter if priority_filter != "All" else None,
        status=status_filter if status_filter != "All" else None
    )

    # Separate reports into Geocoded vs Unlocated
    geocoded_reports = [r for r in reports if r.get("latitude") is not None and r.get("longitude") is not None]
    unlocated_reports = [r for r in reports if r.get("latitude") is None or r.get("longitude") is None]

    # Map Summary Stats
    stat_c1, stat_c2, stat_c3 = st.columns(3)
    with stat_c1:
        st.metric("Total Filtered Incidents", len(reports))
    with stat_c2:
        st.metric("Pinned on GIS Map", len(geocoded_reports))
    with stat_c3:
        st.metric("Unlocated (Missing GPS)", len(unlocated_reports))

    # Determine Map Center
    if geocoded_reports:
        avg_lat = sum(r["latitude"] for r in geocoded_reports) / len(geocoded_reports)
        avg_lon = sum(r["longitude"] for r in geocoded_reports) / len(geocoded_reports)
        map_center = [avg_lat, avg_lon]
        zoom_level = 13
    else:
        map_center = DEFAULT_MAP_CENTER
        zoom_level = DEFAULT_MAP_ZOOM

    # Initialize Folium Map — using OpenStreetMap (free, no API key ever required)
    # We add a dark CartoDB tile layer on top; if unavailable, OSM base still shows.
    m = folium.Map(
        location=map_center,
        zoom_start=zoom_level,
        tiles=None,          # We add tiles manually below so we can control fallback
        control_scale=True
    )
    # Primary: CartoDB dark matter (free, no key needed via Folium's built-in CDN)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="Dark Map",
        max_zoom=20,
        subdomains="abcd",
    ).add_to(m)
    # Fallback layer (always visible in layer control if dark tiles fail)
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Standard Map (Fallback)",
        show=False,
    ).add_to(m)
    folium.LayerControl().add_to(m)

    # Marker Clustering
    marker_cluster = MarkerCluster(name="Damage Clusters").add_to(m)

    # Color mapping for priority
    priority_colors = {
        "HIGH": "#EF4444",    # Red
        "MEDIUM": "#F59E0B",  # Amber
        "LOW": "#10B981"      # Green
    }

    # Add Markers
    for r in geocoded_reports:
        band = r.get("priority_band", "LOW").upper()
        marker_color = priority_colors.get(band, "#10B981")

        demo_label = " [DEMO RECORD]" if r.get("is_demo_data") else ""

        # Check for annotated or original thumbnail
        thumb_html = ""
        img_p = r.get("annotated_image_path") or r.get("original_image_path")
        if img_p and Path(img_p).exists():
            try:
                with Image.open(img_p) as t_img:
                    t_img.thumbnail((220, 130))
                    b64_str = image_to_base64(t_img)
                    thumb_html = f'<img src="data:image/jpeg;base64,{b64_str}" style="width:100%; border-radius:4px; margin-top:6px; border:1px solid #CBD5E1;" />'
            except Exception:
                pass

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 230px; font-size: 12px; color: #1E293B;">
            <div style="font-size: 14px; font-weight: bold; margin-bottom: 4px; color: {marker_color};">
                {r['id']}{demo_label}
            </div>
            <div style="margin-bottom: 6px;">
                <b>Defect:</b> {r['damage_type']}<br/>
                <b>Priority Score:</b> {r['priority_score']:.1f}/100 ({band})<br/>
                <b>Status:</b> {r['status']}<br/>
                <b>Source:</b> {r.get('location_source', 'Manual')}<br/>
                <b>Address:</b> {r.get('location_address', 'N/A')}
            </div>
            {thumb_html}
            <div style="font-size: 10px; color: #64748B; margin-top: 6px;">
                Reported: {format_datetime(r['created_at'])}
            </div>
        </div>
        """

        # Custom Circle Marker
        folium.CircleMarker(
            location=[r["latitude"], r["longitude"]],
            radius=8,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{r['id']}: {r['damage_type']} ({band} Priority - {r['priority_score']:.1f})",
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.85,
            weight=2
        ).add_to(marker_cluster)

    # Render Map via Streamlit-Folium
    st_folium(m, width="100%", height=520)

    # Map Legend
    st.markdown("""
        <div style="display: flex; gap: 20px; align-items: center; justify-content: center; margin-top: 10px; padding: 10px; background: #131E36; border-radius: 8px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="height: 12px; width: 12px; border-radius: 50%; background-color: #EF4444; display: inline-block;"></span>
                <span style="color: #F8FAFC; font-size: 0.85rem; font-weight: 600;">High Priority (70–100)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="height: 12px; width: 12px; border-radius: 50%; background-color: #F59E0B; display: inline-block;"></span>
                <span style="color: #F8FAFC; font-size: 0.85rem; font-weight: 600;">Medium Priority (40–69)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="height: 12px; width: 12px; border-radius: 50%; background-color: #10B981; display: inline-block;"></span>
                <span style="color: #F8FAFC; font-size: 0.85rem; font-weight: 600;">Low Priority (0–39)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Unlocated Incidents Section
    if unlocated_reports:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">⚠️ Unpinned Incidents (Coordinates Not Provided)</div>', unsafe_allow_html=True)
        st.caption("As required by system safety protocols, reports without verified coordinates are never placed at arbitrary map coordinates.")

        unlocated_data = []
        for ur in unlocated_reports:
            p_badge = get_priority_badge_html(ur["priority_band"], ur["priority_score"])
            unlocated_data.append({
                "Report ID": ur["id"],
                "Damage Type": ur["damage_type"],
                "Street Address / Landmark": ur["location_address"] or "Not Provided",
                "Priority": p_badge,
                "Status": ur["status"],
                "Reported Date": format_datetime(ur["created_at"])
            })
        st.write(pd.DataFrame(unlocated_data).to_html(escape=False, index=False), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
