import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import difflib
import html
from datetime import datetime
from docx import Document

from modules.word_compare.comparator import compare_documents


# ------------------------------------------
# Extract document content
# ------------------------------------------
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
        content.append(f"[TABLE-{table_index+1}]")

        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
            )
            content.append(f"[TABLE] {row_text}")

    # Images
    image_count = 0
    for rel in doc.part.rels.values():
        try:
            if rel.is_external:
                continue

            if "image" in rel.target_ref.lower():
                image_count += 1

        except Exception:
            continue

    if image_count:
        content.append(
            f"[IMAGES FOUND: {image_count}]"
        )

    return content


# ------------------------------------------
# Generate diff HTML
# ------------------------------------------
def generate_diff_html(old_lines, new_lines, is_old=True):
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
                    <div class="line normal">
                        {html.escape(line)}
                    </div>
                    """
                )

        elif opcode == "delete" and is_old:
            for line in old_lines[i1:i2]:
                output.append(
                    f"""
                    <div class="line removed">
                        ❌ Removed: {html.escape(line)}
                    </div>
                    """
                )

        elif opcode == "insert" and not is_old:
            for line in new_lines[j1:j2]:
                output.append(
                    f"""
                    <div class="line added">
                        ➕ Added: {html.escape(line)}
                    </div>
                    """
                )

        elif opcode == "replace":
            lines = old_lines[i1:i2] if is_old else new_lines[j1:j2]

            for line in lines:
                label = (
                    "🔄 Replaced"
                    if is_old
                    else "🔄 Updated"
                )

                output.append(
                    f"""
                    <div class="line updated">
                        {label}: {html.escape(line)}
                    </div>
                    """
                )

    return "".join(output)


# ------------------------------------------
# Combined synchronized preview
# ------------------------------------------
def render_synced_preview(
    old_html,
    new_html,
    old_filename,
    new_filename
):
    combined_html = f"""
    <html>
    <head>
    <style>
        body {{
            margin:0;
            font-family:Arial;
        }}

        .container {{
            display:flex;
            width:100%;
            height:650px;
            border:1px solid #ccc;
        }}

        .pane {{
            width:50%;
            overflow-y:auto;
            border-right:1px solid #ddd;
            padding:10px;
        }}

        .header {{
            font-weight:bold;
            font-size:16px;
            margin-bottom:10px;
            position:sticky;
            top:0;
            background:white;
            padding:10px;
            z-index:100;
        }}

        .line {{
            padding:6px;
            margin:4px 0;
            border-radius:4px;
            font-size:13px;
        }}

        .normal {{
            background:white;
        }}

        .removed {{
            background:#ffcccc;
        }}

        .added {{
            background:#ccffcc;
        }}

        .updated {{
            background:#ffe599;
        }}
    </style>
    </head>

    <body>

    <div class="container">

        <div class="pane" id="leftPane">
            <div class="header">{old_filename}</div>
            {old_html}
        </div>

        <div class="pane" id="rightPane">
            <div class="header">{new_filename}</div>
            {new_html}
        </div>

    </div>

    <script>
        const left = document.getElementById("leftPane");
        const right = document.getElementById("rightPane");

        let syncing = false;

        left.addEventListener("scroll", function() {{
            if (!syncing) {{
                syncing = true;
                right.scrollTop = left.scrollTop;
                syncing = false;
            }}
        }});

        right.addEventListener("scroll", function() {{
            if (!syncing) {{
                syncing = true;
                left.scrollTop = right.scrollTop;
                syncing = false;
            }}
        }});
    </script>

    </body>
    </html>
    """

    components.html(
        combined_html,
        height=700,
        scrolling=False
    )


# ------------------------------------------
# Main UI
# ------------------------------------------
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
            type=["docx"]
        )

    with col2:
        new_file = st.file_uploader(
            "Upload New Document",
            type=["docx"]
        )

    if old_file and new_file:

        old_file.seek(0)
        old_lines = extract_doc_content(old_file)

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

        render_synced_preview(
            old_html,
            new_html,
            old_file.name,
            new_file.name
        )

        st.divider()

        if st.button("Generate Highlighted Word File"):

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

                with open(output_path, "rb") as f:
                    file_bytes = f.read()

                st.download_button(
                    label="Download Compared Document",
                    data=file_bytes,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

                os.remove(output_path)

            except Exception as e:
                st.error(
                    f"Error: {str(e)}"
                )
