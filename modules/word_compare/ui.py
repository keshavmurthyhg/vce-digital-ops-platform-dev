import streamlit as st

from modules.word_compare.sidebar import (
    render_sidebar
)

from modules.word_compare.preview import (
    extract_doc_content,
    generate_aligned_diff_rows,
    render_synced_preview
)

from modules.word_compare.generator import (
    generate_output_file
)


# --------------------------------------------------
# Main UI
# --------------------------------------------------
def render():
    st.title("Word Compare Utility")

    st.write(
        "Upload old master document and new document "
        "from sidebar to compare changes."
    )

    # ------------------------------------------
    # Sidebar Controls
    # ------------------------------------------
    controls = render_sidebar()

    old_file = controls["old_file"]
    new_file = controls["new_file"]
    generate_clicked = controls["generate_clicked"]

    # ------------------------------------------
    # Initial state
    # ------------------------------------------
    if not old_file or not new_file:
        st.info(
            "Upload both documents from the sidebar "
            "to start comparison."
        )
        return

    try:
        # ------------------------------------------
        # Extract preview content
        # ------------------------------------------
        old_file.seek(0)
        old_lines = extract_doc_content(
            old_file
        )

        new_file.seek(0)
        new_lines = extract_doc_content(
            new_file
        )

        # ------------------------------------------
        # Generate preview rows
        # ------------------------------------------
        old_html, new_html = (
            generate_aligned_diff_rows(
                old_lines,
                new_lines
            )
        )

        # ------------------------------------------
        # Success message
        # ------------------------------------------
        st.success(
            "Files loaded successfully. "
            "Review the preview below."
        )

        # ------------------------------------------
        # Preview Section
        # ------------------------------------------
        st.subheader(
            "Difference Preview"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"### {old_file.name}"
            )

        with col2:
            st.markdown(
                f"### {new_file.name}"
            )

        render_synced_preview(
            old_html,
            new_html
        )

        # ------------------------------------------
        # Generate Output
        # ------------------------------------------
        if generate_clicked:
            try:
                output_data = (
                    generate_output_file(
                        old_file,
                        new_file
                    )
                )

                st.session_state[
                    "word_compare_output"
                ] = output_data

                st.success(
                    "Highlighted document "
                    "generated successfully."
                )

            except Exception as e:
                st.error(
                    f"Generation Error: {str(e)}"
                )

        # ------------------------------------------
        # Download Button
        # ------------------------------------------
        if (
            "word_compare_output"
            in st.session_state
        ):
            output_data = st.session_state[
                "word_compare_output"
            ]

            st.sidebar.download_button(
                label="Download Compared File",
                data=output_data[
                    "file_bytes"
                ],
                file_name=output_data[
                    "file_name"
                ],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    except Exception as e:
        st.error(
            f"Preview Error: {str(e)}"
        )
