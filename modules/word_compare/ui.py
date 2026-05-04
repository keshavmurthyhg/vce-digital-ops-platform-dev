import streamlit as st
import tempfile
import os
import difflib
from docx import Document

from modules.word_compare.comparator import compare_documents


# -----------------------------
# Extract text from word file
# -----------------------------
def extract_doc_text(doc_file):
    doc = Document(doc_file)

    content = []

    # paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content.append(text)

    # tables
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip() for cell in row.cells
            )
            if row_text.strip():
                content.append(row_text)

    return content


# -----------------------------
# Generate HTML diff preview
# -----------------------------
def generate_diff_html(old_lines, new_lines, is_old=True):
    matcher = difflib.SequenceMatcher(
        None,
        old_lines,
        new_lines
    )

    html_lines = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():

        if opcode == "equal":
            lines = old_lines[i1:i2] if is_old else new_lines[j1:j2]

            for line in lines:
                html_lines.append(
                    f"""
                    <div style='padding:4px'>
                        {line}
                    </div>
                    """
                )

        elif opcode == "delete" and is_old:
            for line in old_lines[i1:i2]:
                html_lines.append(
                    f"""
                    <div style='background-color:#ffcccc;
                                padding:4px;
                                margin:2px;
                                border-radius:4px'>
                        ❌ Removed: {line}
                    </div>
                    """
                )

        elif opcode == "insert" and not is_old:
            for line in new_lines[j1:j2]:
                html_lines.append(
                    f"""
                    <div style='background-color:#ccffcc;
                                padding:4px;
                                margin:2px;
                                border-radius:4px'>
                        ➕ Added: {line}
                    </div>
                    """
                )

        elif opcode == "replace":
            if is_old:
                for line in old_lines[i1:i2]:
                    html_lines.append(
                        f"""
                        <div style='background-color:#ffd699;
                                    padding:4px;
                                    margin:2px;
                                    border-radius:4px'>
                            🔄 Replaced: {line}
                        </div>
                        """
                    )
            else:
                for line in new_lines[j1:j2]:
                    html_lines.append(
                        f"""
                        <div style='background-color:#ffd699;
                                    padding:4px;
                                    margin:2px;
                                    border-radius:4px'>
                            🔄 Updated: {line}
                        </div>
                        """
                    )

    return "".join(html_lines)


# -----------------------------
# Main UI
# -----------------------------
def render():
    st.title("Word Compare Utility")

    st.write(
        "Upload old master document and new document "
        "to preview and highlight changes."
    )

    col1, col2 = st.columns(2)

    with col1:
        old_file = st.file_uploader(
            "Upload Old Document (Master)",
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

        # Preview section
        st.subheader("Difference Preview")

        old_lines = extract_doc_text(old_file)
        new_lines = extract_doc_text(new_file)

        old_html = generate_diff_html(
            old_lines,
            new_lines,
            is_old=True
        )

        new_html = generate_diff_html(
            old_lines,
            new_lines,
            is_old=False
        )

        preview_col1, preview_col2 = st.columns(2)

        with preview_col1:
            st.markdown("### Old Document Preview")
            st.markdown(
                f"""
                <div style="
                    height:500px;
                    overflow-y:auto;
                    border:1px solid #ccc;
                    padding:10px;
                    background:white;">
                    {old_html}
                </div>
                """,
                unsafe_allow_html=True
            )

        with preview_col2:
            st.markdown("### New Document Preview")
            st.markdown(
                f"""
                <div style="
                    height:500px;
                    overflow-y:auto;
                    border:1px solid #ccc;
                    padding:10px;
                    background:white;">
                    {new_html}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # Download highlighted doc
        if st.button("Generate Highlighted Word File"):
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

                st.success("Comparison completed successfully")

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
