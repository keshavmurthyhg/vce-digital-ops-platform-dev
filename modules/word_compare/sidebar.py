import streamlit as st


def render_sidebar():
    st.sidebar.subheader("Word Compare Controls")

    old_file = st.sidebar.file_uploader(
        "Upload Old Document (Master)",
        type=["docx"],
        key="wc_old_doc"
    )

    new_file = st.sidebar.file_uploader(
        "Upload New Document",
        type=["docx"],
        key="wc_new_doc"
    )

    generate_clicked = st.sidebar.button(
        "Generate Highlighted File"
    )

    clear_clicked = st.sidebar.button(
        "Clear Files"
    )

    if clear_clicked:
        keys_to_clear = [
            "wc_old_doc",
            "wc_new_doc",
            "word_compare_output"
        ]

        for key in keys_to_clear:
            st.session_state.pop(
                key,
                None
            )

        st.rerun()

    return {
        "old_file": old_file,
        "new_file": new_file,
        "generate_clicked": generate_clicked
    }
