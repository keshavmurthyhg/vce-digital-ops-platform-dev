import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import difflib
import html
from datetime import datetime
from docx import Document

from modules.word_compare.comparator import compare_documents


# --------------------------------------
# Extract content
# --------------------------------------
def extract_doc_content(doc_file):
    doc = Document(doc_file)
    content = []

    # Paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content.append(text)

    # Tables
    for table_index, table in enumerate(doc.tables):
        content.append(
            f"--- TABLE {table_index+1} ---"
        )

        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
            )
            content.append(row_text)

    # Images
    image_count = 0

    for rel in doc.part.rels.values():
        try:
            if rel.is_external:
                continue

            if "image" in rel.target_ref.lower():
                image_count += 1

        except:
            continue

    if image_count:
        content.append(
            f"--- IMAGES FOUND: {image_count} ---"
        )

    return content


# --------------------------------------
# HTML preview generator
# --------------------------------------
def generate_diff_html(
    old_lines,
    new_lines,
    is_old=True
):
    matcher = difflib.SequenceMatcher(
        None,
        old_lines,
        new_lines
    )

    output = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():

        if opcode == "equal":
            lines = old_lines[i1:i2] if is_old else new_lines[j1:j2]

            for line in lines:
                output.append(
                    f"""
                    <p style='padding:5px'>
                    {html.escape(line)}
                    </p>
                    """
                )

        elif opcode == "delete" and is_old:
            for line in old_lines[i1:i2]:
                output.append(
                    f"""
                    <p style='background:#ffcccc;padding:5px'>
                    Removed: {html.escape(line)}
                    </p>
                    """
                )

        elif opcode == "insert" and not is_old:
            for line in new_lines[j1:j2]:
                output.append(
                    f"""
                    <p style='background:#ccffcc;padding:5px'>
                    Added: {html.escape(line)}
                    </p>
                    """
                )

        elif opcode == "replace":
            lines = old_lines[i1:i2] if is_old else new_lines[j1:j2]

            for line in lines:
                output.append(
                    f"""
                    <p style='background:#ffe599;padding:5px'>
                    Updated: {html.escape(line)}
                    </p>
                    """
                )

    return f"""
    <div style="
        height:600px;
        overflow-y:auto;
        border:1px solid #ccc;
        background:white;
        padding:10px;
    ">
        {''.join(output)}
    </div>
    """


# --------------------------------------
# Main UI
# --------------------------------------
def render():
    st.title("Word Compare Utility")

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

        old_file.seek(0)
        new_file.seek(0)

        old_lines = extract_doc_content(old_file)

        old_file.seek(0)
        new_file.seek(0)

        new_lines = extract_doc_content(new_file)

        old_html = generate_diff_html(
            old_lines,
            new_lines,
            True
        )

        new_html = generate_diff_html(
            old_lines,
            new_lines,
            False
        )

        st.subheader("Difference Preview")

        p1, p2 = st.columns(2)

        with p1:
            st.markdown(
                f"### {old_file.name}"
            )

            components.html(
                old_html,
                height=650,
                scrolling=True
            )

        with p2:
            st.markdown(
                f"### {new_file.name}"
            )

            components.html(
                new_html,
                height=650,
                scrolling=True
            )

        st.divider()

        if st.button(
            "Generate Highlighted Word File"
        ):
            try:
                old_file.seek(0)
                new_file.seek(0)

                base_name = os.path.splitext(
                    old_file.name
                )[0]

                current_date = datetime.now().strftime(
                    "%d%b%Y"
                )

                output_filename = (
                    f"{base_name}"
                    f"_Diff-Highlighted_"
                    f"{current_date}.docx"
                )

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

                with open(
                    output_path,
                    "rb"
                ) as f:
                    st.download_button(
                        label="Download Compared Document",
                        data=f,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                os.remove(output_path)

            except Exception as e:
                st.error(
                    f"Error: {str(e)}"
                )
