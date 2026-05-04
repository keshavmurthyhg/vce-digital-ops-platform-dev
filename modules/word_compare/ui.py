import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import difflib
import html
from docx import Document

from modules.word_compare.comparator import compare_documents


# ---------------------------------------------------
# Extract paragraphs + tables in original doc order
# ---------------------------------------------------
def extract_doc_text(doc_file):
    doc = Document(doc_file)
    content = []

    # Extract paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content.append({
                "type": "paragraph",
                "content": text
            })

    # Extract tables
    for table_index, table in enumerate(doc.tables):
        table_rows = []

        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
            )

            if row_text.strip():
                table_rows.append(row_text)

        if table_rows:
            content.append({
                "type": "table",
                "content": table_rows
            })

    return content


# ---------------------------------------------------
# Flatten content for diff comparison
# ---------------------------------------------------
def flatten_content(content):
    lines = []

    for item in content:
        if item["type"] == "paragraph":
            lines.append(item["content"])

        elif item["type"] == "table":
            for row in item["content"]:
                lines.append(f"[TABLE] {row}")

    return lines


# ---------------------------------------------------
# Generate HTML preview
# ---------------------------------------------------
def generate_diff_html(old_lines, new_lines, is_old=True):
    matcher = difflib.SequenceMatcher(
        None,
        old_lines,
        new_lines
    )

    html_output = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():

        # ---------------------------
        # Equal content
        # ---------------------------
        if opcode == "equal":
            lines = old_lines[i1:i2] if is_old else new_lines[j1:j2]

            for line in lines:
                html_output.append(
                    f"""
                    <p style="
                        margin:6px 0;
                        padding:4px;
                        font-family:Calibri;
                        font-size:14px;
                    ">
                        {html.escape(line)}
                    </p>
                    """
                )

        # ---------------------------
        # Removed content
        # ---------------------------
        elif opcode == "delete" and is_old:
            for line in old_lines[i1:i2]:
                html_output.append(
                    f"""
                    <p style="
                        background-color:#ffcccc;
                        margin:6px 0;
                        padding:6px;
                        border-radius:4px;
                        font-family:Calibri;
                    ">
                        ❌ Removed: {html.escape(line)}
                    </p>
                    """
                )

        # ---------------------------
        # Added content
        # ---------------------------
        elif opcode == "insert" and not is_old:
            for line in new_lines[j1:j2]:
                html_output.append(
                    f"""
                    <p style="
                        background-color:#ccffcc;
                        margin:6px 0;
                        padding:6px;
                        border-radius:4px;
                        font-family:Calibri;
                    ">
                        ➕ Added: {html.escape(line)}
                    </p>
                    """
                )

        # ---------------------------
        # Replaced content
        # ---------------------------
        elif opcode == "replace":
            if is_old:
                lines = old_lines[i1:i2]
                prefix = "🔄 Replaced:"
            else:
                lines = new_lines[j1:j2]
                prefix = "🔄 Updated:"

            for line in lines:
                html_output.append(
                    f"""
                    <p style="
                        background-color:#ffe599;
                        margin:6px 0;
                        padding:6px;
                        border-radius:4px;
                        font-family:Calibri;
                    ">
                        {prefix} {html.escape(line)}
                    </p>
                    """
                )

    final_html = "".join(html_output)

    return f"""
    <div style="
        height:600px;
        overflow-y:auto;
        border:1px solid #d3d3d3;
        padding:15px;
        background:white;
        font-family:Calibri;
    ">
        {final_html}
    </div>
    """


# ---------------------------------------------------
# Main UI
# ---------------------------------------------------
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

        try:
            # Reset file pointers
            old_file.seek(0)
            new_file.seek(0)

            old_content = extract_doc_text(old_file)

            old_file.seek(0)
            new_file.seek(0)

            new_content = extract_doc_text(new_file)

            old_lines = flatten_content(old_content)
            new_lines = flatten_content(new_content)

            st.subheader("Difference Preview")

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
                components.html(
                    old_html,
                    height=650,
                    scrolling=True
                )

            with preview_col2:
                st.markdown("### New Document Preview")
                components.html(
                    new_html,
                    height=650,
                    scrolling=True
                )

            st.divider()

            if st.button("Generate Highlighted Word File"):
                try:
                    old_file.seek(0)
                    new_file.seek(0)

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
                    st.error(
                        f"Document generation error: {str(e)}"
                    )

        except Exception as e:
            st.error(
                f"Preview generation error: {str(e)}"
            )
