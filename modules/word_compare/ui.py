import streamlit as st

from modules.word_compare.sidebar import render_sidebar
from modules.word_compare.preview import (
    extract_doc_content,
    generate_aligned_diff_rows,
    render_synced_preview
)
from modules.word_compare.generator import generate_output_file


def render():
    # -------------------------
    # Top title section
    # -------------------------
    title_col1, title_col2 = st.columns([0.8, 9.2])

    with title_col1:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/281/281760.png",
            width=55
        )
    
    with title_col2:
        st.markdown(
            """
            <div style="
                font-size:42px;
                font-weight:700;
                color:#2f3342;
                margin-top:4px;
                white-space:nowrap;
                line-height:1;
            ">
                Word Compare Utility
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="
            margin-top:-5px;
            margin-bottom:10px;
            font-size:16px;
        ">
            Compare old and new word documents.
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------
    # Sidebar controls
    # -------------------------
    controls = render_sidebar()

    old_file = controls["old_file"]
    new_file = controls["new_file"]
    generate_clicked = controls["generate_clicked"]

    if not old_file or not new_file:
        return

    try:
        old_file.seek(0)
        old_lines = extract_doc_content(old_file)

        new_file.seek(0)
        new_lines = extract_doc_content(new_file)

        old_html, new_html = generate_aligned_diff_rows(
            old_lines,
            new_lines
        )

        # compact message
        # File upload success message
        st.success(
            "Files loaded successfully."
        )
        
        # Generation success message
        if st.session_state.get(
            "generation_success"
        ):
            st.success(
                "Highlighted document generated successfully."
            )

        st.markdown(
            "<h3 style='margin-bottom:5px;'>Difference Preview</h3>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"""
                <div style='font-size:18px;
                            font-weight:600;
                            margin-bottom:4px;'>
                    {old_file.name}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style='font-size:18px;
                            font-weight:600;
                            margin-bottom:4px;'>
                    {new_file.name}
                </div>
                """,
                unsafe_allow_html=True
            )

        render_synced_preview(
            old_html,
            new_html
        )

        if generate_clicked:
            try:
                output_data = generate_output_file(
                    old_file,
                    new_file
                )
        
                st.session_state[
                    "word_compare_output"
                ] = output_data
        
                # FIX: trigger success message
                st.session_state[
                    "generation_success"
                ] = True
        
                st.rerun()
        
            except Exception as e:
                st.error(
                    f"Generation Error: {str(e)}"
                )

        if "word_compare_output" in st.session_state:
            output_data = st.session_state[
                "word_compare_output"
            ]

            st.sidebar.download_button(
                label="Download Compared File",
                use_container_width=True
                data=output_data["file_bytes"],
                file_name=output_data["file_name"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    except Exception as e:
        st.error(
            f"Preview Error: {str(e)}"
        )
