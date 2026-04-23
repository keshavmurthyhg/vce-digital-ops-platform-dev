import streamlit as st
from modules.report.doc_generator import generate_pdf, generate_word_doc_wrapper
from modules.report.ui.actions import run_bulk

def render_main(filtered_df):

    st.title("Incident Report Generator")

    if filtered_df is None or filtered_df.empty:
        st.warning("No data available")
        return

    inc_list = filtered_df["number"].astype(str).tolist()

    selected = st.selectbox("Select Incident", inc_list)

    if selected:
        st.session_state.selected_incident = selected

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate PDF"):
            # fetch single row
            row = filtered_df[filtered_df["number"] == selected].iloc[0]

            pdf = generate_pdf(
                data=row.to_dict(),
                root="",
                l2="",
                res="",
                images=st.session_state.images
            )

            st.download_button("Download PDF", pdf, file_name=f"{selected}.pdf")

    with col2:
        if st.button("Bulk Generate"):
            zip_bytes = run_bulk(filtered_df, st.session_state.images)

            if zip_bytes:
                st.download_button(
                    "Download ZIP",
                    zip_bytes,
                    file_name="bulk_reports.zip"
                )
            else:
                st.warning("No reports generated")
