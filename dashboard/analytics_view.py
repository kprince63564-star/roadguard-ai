"""
ROADGUARD AI - Analytics and Insights Module
Deep analytical intelligence and longitudinal trends on municipal road deterioration,
repair velocity, and geographic hazard clusters.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.db import get_all_reports
from config import STATUS_COLORS, PRIORITY_BANDS

def render_analytics_page():
    """Renders comprehensive analytical visualizations and statistical breakdowns."""
    st.markdown("""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>MUNICIPAL OPERATIONS</span> / <span>BUSINESS INTELLIGENCE</span> / <span class="active">ANALYTICS & INSIGHTS</span>
                </div>
                <h1>Road Infrastructure Analytics & Insights</h1>
                <p class="rg-page-subtitle">
                    Longitudinal telemetry, spatial damage concentrations, and municipal maintenance resolution velocity.
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-ai">● PREDICTIVE DEGRADATION MODEL</span>
                <span class="rg-header-chip rg-chip-online">● REAL-TIME DATASET AGGREGATION</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    reports = get_all_reports()
    if not reports:
        st.info("Insufficient data available in the database to generate analytical models. Add reports to view insights.")
        return

    df = pd.DataFrame(reports)
    df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["date"] = df["created_at_dt"].dt.date

    # Row 1: High Priority Hotspots & Damage Classification
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">🔥 High-Priority Reports by Location</div>', unsafe_allow_html=True)
        high_df = df[df["priority_band"] == "HIGH"]
        if not high_df.empty and "location_address" in high_df.columns:
            loc_counts = high_df["location_address"].value_counts().head(7).reset_index()
            loc_counts.columns = ["Location Corridor", "Critical Incidents"]

            fig_hotspot = px.bar(
                loc_counts,
                x="Critical Incidents",
                y="Location Corridor",
                orientation="h",
                color="Critical Incidents",
                color_continuous_scale=["#F59E0B", "#EF4444", "#DC2626"]
            )
            fig_hotspot.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Inter"),
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig_hotspot, use_container_width=True)
        else:
            st.caption("No High-Priority reports registered yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">📈 Longitudinal Defect Registration Trends</div>', unsafe_allow_html=True)
        trend_timeframe = st.radio("Temporal Aggregation Window:", ["Daily", "Weekly", "Monthly"], horizontal=True, key="analytics_interval")
        if not df.empty and "created_at_dt" in df.columns:
            if trend_timeframe == "Weekly":
                trend_data = df.dropna(subset=["created_at_dt"]).groupby(df["created_at_dt"].dropna().dt.to_period("W").dt.start_time.dt.date).size().reset_index(name="Report Count")
                trend_data.columns = ["Time Period", "Report Count"]
            elif trend_timeframe == "Monthly":
                trend_data = df.dropna(subset=["created_at_dt"]).groupby(df["created_at_dt"].dropna().dt.to_period("M").dt.start_time.dt.date).size().reset_index(name="Report Count")
                trend_data.columns = ["Time Period", "Report Count"]
            else:
                trend_data = df.groupby("date").size().reset_index(name="Report Count")
                trend_data.columns = ["Time Period", "Report Count"]

            trend_data["Time Period"] = trend_data["Time Period"].astype(str)

            fig_trend = px.bar(
                trend_data,
                x="Time Period",
                y="Report Count",
                color_discrete_sequence=["#38BDF8"],
                text="Report Count"
            )
            fig_trend.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Inter"),
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#1E293B")
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 2: Resolution Pipeline & Roadway Category Impact
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">⚖️ Repaired vs. Unresolved Incident Ratio</div>', unsafe_allow_html=True)
        resolved_count = len(df[df["status"] == "Resolved"])
        unresolved_count = len(df[df["status"] != "Resolved"])

        ratio_df = pd.DataFrame([
            {"Category": "Resolved / Repaired", "Count": resolved_count},
            {"Category": "Active / Unresolved", "Count": unresolved_count}
        ])

        fig_ratio = px.pie(
            ratio_df,
            names="Category",
            values="Count",
            hole=0.6,
            color="Category",
            color_discrete_map={"Resolved / Repaired": "#10B981", "Active / Unresolved": "#F59E0B"}
        )
        fig_ratio.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC", family="Inter"),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_ratio, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">🛣️ Mean Priority Score by Road Classification</div>', unsafe_allow_html=True)
        if "road_type" in df.columns and "priority_score" in df.columns:
            road_grp = df.groupby("road_type")["priority_score"].mean().reset_index()
            road_grp["priority_score"] = road_grp["priority_score"].round(1)

            fig_road = px.bar(
                road_grp,
                x="road_type",
                y="priority_score",
                color="priority_score",
                color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"],
                text="priority_score"
            )
            fig_road.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Inter"),
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(title="", showgrid=False),
                yaxis=dict(title="Avg Score (0-100)", showgrid=True, gridcolor="#1E293B")
            )
            st.plotly_chart(fig_road, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 3: AI Detection Confidence vs Priority Score Scatter
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown('<div class="rg-card-title">🔬 Detection Confidence vs. Priority Score Correlation</div>', unsafe_allow_html=True)
    if "avg_confidence" in df.columns and "priority_score" in df.columns:
        fig_scatter = px.scatter(
            df,
            x="avg_confidence",
            y="priority_score",
            color="priority_band",
            size="detection_count",
            hover_data=["id", "damage_type", "location_address"],
            color_discrete_map={"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#10B981"},
            labels={"avg_confidence": "AI Model Confidence", "priority_score": "Visual Priority Score"}
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC", family="Inter"),
            xaxis=dict(showgrid=True, gridcolor="#1E293B"),
            yaxis=dict(showgrid=True, gridcolor="#1E293B")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
