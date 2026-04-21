import streamlit as st
import time
from modules.excel_compare.logic import (
    compare_excels,
    section_diff_logic,
    style_dataframe,
    generate_output
)


def show_excel_compare():
    st.title("📊 Excel Comparison Tool")

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
        df1, df2 = compare_excels(file1, file2)

        diff_mask2, section_summary, total_diff = section_diff_logic(df1, df2)

        # ===== SUMMARY KPI =====
        #st.subheader("📊 Summary")

        #colA, colB = st.columns(2)
        #colA.metric("Total Differences", total_diff)
        #colB.metric("Sections Impacted", sum(1 for v in section_summary.values() if v["added"] or v["removed"]))

        # ===== SECTION SUMMARY =====
        #st.subheader("📦 Section-wise Changes")

        #for section, data in section_summary.items():
            #if data["added"] or data["removed"]:
                #st.write(f"🔸 {section} → Added: {data['added']} | Removed: {data['removed']}")

        # ===== PREVIEW =====
        st.subheader("🔍 Preview Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### 📄 {file1.name} (Base)")
            st.dataframe(df1, use_container_width=True)
        
        with col2:
            st.markdown(f"### 📄 {file2.name} (Changes)")
            st.dataframe(style_dataframe(df2, diff_mask2), use_container_width=True)
        
        # ===== SUMMARY KPI =====
        
        st.subheader("📊 Summary")
        col1, col2 = st.columns(2)

        col1.metric("Total Changes", total_diff)
        col2.metric("Sections Impacted", sum(1 for v in section_summary.values() if any(v.values())))
        
        # ===== SECTION SUMMARY =====
        st.subheader("📦 Section-wise Changes")
        
        for section, data in section_summary.items():
            if any(data.values()):
                st.write(
                    f"🔸 {section} → "
                    f"🟢 {data['added']} | 🔴 {data['removed']} | 🟡 {data['modified']}"
                )
        
        # ===== DOWNLOAD =====
        if compare_clicked:
            zip_path, zip_name = generate_output(file1, file2)

            with open(zip_path, "rb") as f:
                st.sidebar.download_button(
                    "⬇️ Download Comparison (ZIP)",
                    f,
                    zip_name
                )

            msg = st.sidebar.success("✅ ZIP Ready!")

            time.sleep(15)
            msg.empty()
