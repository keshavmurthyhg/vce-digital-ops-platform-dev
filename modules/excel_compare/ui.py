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
        summary = get_summary(diff_mask)

        st.subheader("📊 Summary")
        st.write(f"🔸 Total Cells: {summary['total_cells']}")
        st.write(f"🔸 Differences: {summary['diff_cells']}")
        st.write(f"🔸 Rows Changed: {summary['changed_rows']}")
        st.write(f"🔸 Columns Changed: {summary['changed_cols']}")

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
            file1_out, file2_out = generate_output(file1, file2)

            name1 = os.path.splitext(filename1)[0] + "_Highlighted.xlsx"
            name2 = os.path.splitext(filename2)[0] + "_Highlighted.xlsx"

            with open(file1_out, "rb") as f:
                st.sidebar.download_button(
                    f"⬇️ {name1}",
                    f,
                    name1
                )

            with open(file2_out, "rb") as f:
                st.sidebar.download_button(
                    f"⬇️ {name2}",
                    f,
                    name2
                )

            st.sidebar.success("✅ Files ready!")
