import streamlit as st


def render_sidebar():
    st.sidebar.subheader(
        "Word Compare Controls"
    )

    # -------------------------
    # Initialize uploader keys
    # -------------------------
    if "old_uploader_key" not in st.session_state:
        st.session_state.old_uploader_key = "old_upload_1"

    if "new_uploader_key" not in st.session_state:
        st.session_state.new_uploader_key = "new_upload_1"

    # -------------------------
    # Old file upload
    # -------------------------
    old_file = st.sidebar.file_uploader(
        "Upload Old Document (DOCX | 200MB)",
        type=["docx"],
        key="wc_old_doc"
    )

    # -------------------------
    # New file upload
    # -------------------------
    new_file = st.sidebar.file_uploader(
        "Upload New Document (DOCX | 200MB)",
        type=["docx"],
        key="wc_new_doc"
    )

    # -------------------------
    # Generate button
    # -------------------------
    generate_clicked = st.sidebar.button(
        "Generate Highlighted File",
        use_container_width=True
    )

    # -------------------------
    # Clear button
    # -------------------------
    clear_clicked = st.sidebar.button(
        "Clear Files",
        use_container_width=True
    )

    if clear_clicked:
        # Remove output file
        if "word_compare_output" in st.session_state:
            del st.session_state[
                "word_compare_output"
            ]

        if "generation_success" in st.session_state:
            del st.session_state[
                "generation_success"
            ]

        # Reset uploader keys
        st.session_state.old_uploader_key = (
            f"old_upload_{len(st.session_state)}"
        )

        st.session_state.new_uploader_key = (
            f"new_upload_{len(st.session_state)+1}"
        )

        st.rerun()

    return {
        "old_file": old_file,
        "new_file": new_file,
        "generate_clicked": generate_clicked
    }
