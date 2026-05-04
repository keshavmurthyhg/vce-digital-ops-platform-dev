import streamlit as st
import pandas as pd
from io import BytesIO

from modules.word_compare.extractor import extract_doc_content
from modules.word_compare.comparator import compare_documents


def render():
    st.title("Word Compare Utility")

    st.write("Upload two Word documents to compare paragraphs and tables.")

    col1, col2 = st.columns(2)

    with col1:
        old_file = st.file_uploader(
            "Upload Old Document",
            type=["docx"],
            key="old_doc"
        )

    with col2:
        new_file = st.file_uploader(
            "Upload New Document",
            type=["docx"],
            key="new_doc"
        )

    if old_file and new_file:
        try:
            with st.spinner("Comparing documents..."):

                old_content = extract_doc_content(old_file)
                new_content = extract_doc_content(new_file)

                result_df = compare_documents(
                    old_content,
                    new_content
                )

            st.success("Comparison completed successfully")

            if result_df.empty:
                st.info("No differences found between documents.")
            else:
                st.subheader("Comparison Results")
                st.dataframe(
                    result_df,
                    use_container_width=True
                )

                # CSV download
                csv_data = result_df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="Download Comparison Report",
                    data=csv_data,
                    file_name="word_comparison_report.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"Error comparing documents: {str(e)}")
