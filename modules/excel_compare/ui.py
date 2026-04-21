import streamlit as st
from modules.excel_compare.logic import (
    compare_excels,
    get_diff_mask,
    style_dataframe,
    generate_output
)


def show_excel_compare():
    st.title("📊 Excel Comparison Tool")

    # =========================
    # ✅ SIDEBAR CONTROLS
    # =========================
    st.sidebar.markdown("## ⚙️ Excel Compare")

    file1 = st.sidebar.file_uploader(
        "Upload First Excel",
        type=["xlsx"],
        key="file1"
    )

    file2 = st.sidebar.file_uploader(
        "Upload Second Excel",
        type=["xlsx"],
        key="file2"
    )

    col1, col2 = st.sidebar.columns(2)

    # ✅ SAFE CLEAR (DO NOT REMOVE PAGE)
    with col1:
        if st.button("🧹 Clear"):
            keys_to_keep = ["page"]  # preserve navigation
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]
            st.rerun()

    generate_clicked = False

    with col2:
        if st.button("⚡ Compare"):
            generate_clicked = True

    # =========================
    # ✅ MAIN AREA (ONLY OUTPUT)
    # =========================
    if file1 and file2:
        df1, df2 = compare_excels(file1, file2)
        diff_mask = get_diff_mask(df1, df2)

        st.subheader("🔍 Preview Comparison")

        colA, colB = st.columns(2)

        with colA:
            st.markdown("### 📄 File 1")
            styled1 = style_dataframe(df1, diff_mask)
            st.dataframe(styled1, use_container_width=True)

        with colB:
            st.markdown("### 📄 File 2")
            styled2 = style_dataframe(df2, diff_mask)
            st.dataframe(styled2, use_container_width=True)

        # =========================
        # ✅ DOWNLOAD IN SIDEBAR
        # =========================
        if generate_clicked:
            try:
                file1_out, file2_out = generate_output(file1, file2)

                st.sidebar.success("✅ Generated!")

                with open(file1_out, "rb") as f:
                    st.sidebar.download_button(
                        "⬇️ File 1 Highlighted",
                        f,
                        "file1_highlighted.xlsx"
                    )

                with open(file2_out, "rb") as f:
                    st.sidebar.download_button(
                        "⬇️ File 2 Highlighted",
                        f,
                        "file2_highlighted.xlsx"
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")
