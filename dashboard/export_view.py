"""
ROADGUARD AI - Generate & Export Reports
Allows municipal operators and inspectors to generate official PDF work orders
and export audit data in CSV format.
"""

import streamlit as st
import pandas as pd
from database.db import get_all_reports, get_report_by_id
from utils.pdf_generator import generate_pdf_report
from utils.helpers import reports_to_csv_bytes, format_datetime

def render_export_page():
    """Renders the PDF report generation and CSV export center."""
    st.markdown("""
        <div class="rg-page-header">
            <div>
                <div class="rg-page-breadcrumb">
                    <span>MUNICIPAL OPERATIONS</span> / <span>COMPLIANCE</span> / <span class="active">REPORTS & EXPORT</span>
                </div>
                <h1>Municipal Reports & Work Order Generation</h1>
                <p class="rg-page-subtitle">
                    Export verified road defect records for public records compliance, contractor dispatch, and civil engineering audit sheets.
                </p>
            </div>
            <div class="rg-header-status">
                <span class="rg-header-chip rg-chip-online">● REPORTLAB PDF ENGINE ACTIVE</span>
                <span class="rg-header-chip rg-chip-ai">● RFC-4180 CSV COMPLIANT</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    all_reports = get_all_reports()
    if not all_reports:
        st.info("No road damage records are currently available for export.")
        return

    tab1, tab2 = st.tabs(["📄 Generate Official PDF Work Order", "📊 Tabular CSV Database Export"])

    with tab1:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">📄 Select Incident Report for PDF Generation</div>', unsafe_allow_html=True)
        st.write("Generates a print-ready municipal engineering inspection sheet with AI annotations and civil sign-off lines.")

        report_options = {
            f"{r['id']} - {r['damage_type']} ({r['priority_band']} Priority, Score {r['priority_score']:.1f})": r['id']
            for r in all_reports
        }

        selected_label = st.selectbox("Select Report to Print:", list(report_options.keys()))
        selected_id = report_options[selected_label]

        if st.button("🔨 Compile Official Inspection PDF", type="primary"):
            with st.spinner(f"Rendering PDF layout for {selected_id}..."):
                full_rep = get_report_by_id(selected_id)
                if full_rep:
                    pdf_path = generate_pdf_report(full_rep)
                    with open(pdf_path, "rb") as f:
                        pdf_data = f.read()

                    st.success(f"PDF Inspection Work Order compiled successfully!")
                    st.download_button(
                        label=f"⬇️ Download {selected_id} PDF Work Order",
                        data=pdf_data,
                        file_name=f"RoadGuard_Inspection_{selected_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to load report data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown('<div class="rg-card-title">📊 Full Database CSV Export</div>', unsafe_allow_html=True)
        st.write("Download all recorded incident records, coordinates, priority scores, and statuses formatted for GIS and civil maintenance software.")

        csv_bytes = reports_to_csv_bytes(all_reports)

        st.download_button(
            label="⬇️ Download Entire Reports Database (CSV)",
            data=csv_bytes,
            file_name="roadguard_damage_reports.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Preview Export Dataset (First 10 Rows)")
        preview_df = pd.DataFrame(all_reports)[["id", "damage_type", "priority_score", "priority_band", "status", "location_address", "created_at"]].head(10)
        st.dataframe(preview_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
