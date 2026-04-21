import streamlit as st
import os
from modules.excel_compare.logic import (
    compare_excels,
    get_diff_mask,
    style_dataframe,
    generate_output,
    get_summary
)


def show_excel_compare():
    st.title("📊 Excel Comparison Tool")

    # INIT
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.markdown("## ⚙️ Excel Compare")

    file1 = st.sidebar.file_uploader(
        "Upload First Excel",
        type=["xlsx"],
        key=f"file1_{st.session_state.uploader_key}"
    )

    file2 = st.sidebar.file_uploader(
        "Upload Second Excel",
        type=["xlsx"],
        key=f"file2_{st.session_state.uploader_key}"
    )

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🧹 Clear"):
            st.session_state.uploader_key += 1
            st.rerun()

    with col2:
        compare_clicked = st.button("⚡ Compare")

    # =========================
    # MAIN
    # =========================
    if file1 and file2:
        filename1 = file1.name
        filename2 = file2.name

        df1, df2 = compare_excels(file1, file2)
        diff_mask = get_diff_mask(df1, df2)

        # =========================
        # SUMMARY
        # =========================
        st.subheader("📊 Summary")
         col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Cells", summary["total_cells"])
        col2.metric("Differences", summary["diff_cells"])
        col3.metric("Rows Changed", summary["changed_rows"])
        col4.metric("Columns Changed", summary["changed_cols"])   


        # =========================
        # PREVIEW
        # =========================
        st.subheader("🔍 Preview Comparison")

        colA, colB = st.columns(2)

        with colA:
            st.markdown(f"### 📄 {filename1}")
            styled1 = style_dataframe(df1, diff_mask)
            st.dataframe(styled1, use_container_width=True)

        with colB:
            st.markdown(f"### 📄 {filename2}")
            styled2 = style_dataframe(df2, diff_mask)
            st.dataframe(styled2, use_container_width=True)

        # =========================
        # DOWNLOAD
        # =========================
        if compare_clicked:
            zip_path, zip_name = generate_output(file1, file2)
        
            with open(zip_path, "rb") as f:
                st.sidebar.download_button(
                    "⬇️ Download Comparison (ZIP)",
                    f,
                    zip_name
                )
        
            st.sidebar.success("✅ ZIP Ready!")

            st.sidebar.success("✅ Files ready!")
