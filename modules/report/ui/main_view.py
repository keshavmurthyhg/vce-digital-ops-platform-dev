import streamlit as st

from modules.common.ui.preview import render_preview
from modules.common.ui.buttons import render_action_buttons
from modules.report.services.rca_service import build_rca
from modules.report.services.data_mapper import map_incident


def render_main(df):

    st.title("Incident Report Generator")

    # ---------------- INCIDENT + FETCH ---------------- #
    col1, col2 = st.columns([4, 1])

    with col1:
        incident = st.selectbox(
            "Select Incident",
            df["number"].dropna().unique(),
            key="incident_select"
        )

    with col2:
        st.write("")   # minimal spacer for label alignment
        fetch_btn = st.button(
            "Fetch",
            use_container_width=True
        )

    
    # ---------------- BULK ---------------- #
    st.subheader("Bulk Incident Numbers")
    # Auto-fill from sidebar bulk selection
    bulk_default = st.session_state.get("bulk_incidents_list", [])
    
    bulk_text = st.text_area(
        "Enter comma-separated incident numbers",
        value=",".join(bulk_default),
        key="bulk_incidents",
        height=100
    )

    # ---------------- BUTTONS ---------------- #
    actions = render_action_buttons()

    # ---------------- FETCH ---------------- #
    if fetch_btn:
        try:
            row_raw = df[df["number"] == incident].iloc[0].to_dict()

            row = map_incident(row_raw)
            st.session_state["data"] = row

            rca = build_rca(row)

            # Explicit session mapping
            st.session_state["problem"] = rca.get("problem", "")
            st.session_state["root_cause"] = rca.get("analysis", "")
            st.session_state["resolution"] = rca.get("resolution", "")

            st.success("Incident loaded successfully")

        except Exception as e:
            st.error(f"Error loading incident: {e}")

    # ---------------- PREVIEW ---------------- #
    if actions.get("preview"):
        if "data" not in st.session_state:
            st.warning("Please fetch an incident first")
        else:
            render_preview(st.session_state["data"])

    # ---------------- GENERATE PDF ---------------- #
    if actions.get("pdf"):
        if "data" not in st.session_state:
            st.warning("Please fetch an incident first")
        else:
            from modules.report.doc_generator import generate_pdf

            pdf_bytes = generate_pdf(
                data=st.session_state["data"],
                root=st.session_state.get("problem"),
                l2=st.session_state.get("root_cause"),
                res=st.session_state.get("resolution"),
                images=None
            )

            st.download_button(
                "Download PDF",
                pdf_bytes,
                "incident_report.pdf",
                mime="application/pdf"
            )

    # ---------------- GENERATE WORD ---------------- #
    if actions.get("word"):
        if "data" not in st.session_state:
            st.warning("Please fetch an incident first")
        else:
            from modules.report.doc_generator import generate_word_doc_wrapper

            word_bytes = generate_word_doc_wrapper(
                data=st.session_state["data"],
                root=st.session_state.get("problem"),
                l2=st.session_state.get("root_cause"),
                res=st.session_state.get("resolution"),
                images=None
            )

            st.download_button(
                "Download Word",
                word_bytes,
                "incident_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # ---------------- BULK GENERATE ---------------- #
    if actions.get("bulk"):
        if not bulk_text:
            st.warning("Please enter incident numbers")
        else:
            from modules.report.bulk_generator import build_bulk_reports, generate_bulk_zip
    
            incident_list = [i.strip() for i in bulk_text.split(",") if i.strip()]
    
            reports = build_bulk_reports(df, incident_list, images_map={})
    
            if not reports:
                st.warning("No reports generated")
            else:
                zip_buffer = generate_bulk_zip(reports)
    
                st.download_button(
                    "Download Bulk Reports (ZIP)",
                    data=zip_buffer,
                    file_name="bulk_reports.zip",
                    mime="application/zip"
                )
    
    # ---------------- CLEAR ---------------- #
    if actions.get("clear"):
        st.session_state.clear()
        st.rerun()

    # ---------------- RCA SECTION ---------------- #
    if "data" in st.session_state:

        st.subheader("Edit Report Details")

        st.text_area("PROBLEM STATEMENT", key="problem", height=120)
        st.file_uploader("Problem Images", accept_multiple_files=True, key="problem_images")

        st.text_area("ROOT CAUSE", key="root_cause", height=150)
        st.file_uploader("Root Images", accept_multiple_files=True, key="root_images")

        if str(st.session_state.get("resolution", "")).lower() == "nan":
            st.session_state["resolution"] = ""
        
        st.text_area(
            "RESOLUTION & RECOMMENDATION",
            key="resolution",
            height=150
        )
        st.file_uploader("Resolution Images", accept_multiple_files=True, key="resolution_images")
