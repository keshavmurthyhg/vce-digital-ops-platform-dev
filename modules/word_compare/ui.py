import streamlit as st
import tempfile
import os

from modules.word_compare.comparator import compare_documents


def render():
    st.title("Word Compare Utility")

    st.write(
        "Upload old master document and new document "
        "to highlight changes."
    )

    col1, col2 = st.columns(2)

    with col1:
        old_file = st.file_uploader(
            "Upload Old Document (Master)",
            type=["docx"]
        )

    with col2:
        new_file = st.file_uploader(
            "Upload New Document",
            type=["docx"]
        )

    if old_file and new_file:
        if st.button("Compare Documents"):
            try:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".docx"
                ) as tmp:
                    output_path = tmp.name

                compare_documents(
                    old_file,
                    new_file,
                    output_path
                )

                st.success(
                    "Comparison completed successfully"
                )

                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download Compared Document",
                        data=f,
                        file_name="comparison_output.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                os.remove(output_path)

            except Exception as e:
                st.error(f"Error: {str(e)}")
