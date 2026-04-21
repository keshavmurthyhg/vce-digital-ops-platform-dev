import streamlit as st
from modules.excel_compare.logic import (
    compare_excels,
    get_diff_mask,
    style_dataframe,
    generate_output
)


def show_excel_compare():
    st.title("📊 Excel Comparison Tool")

    # ✅ Clear Button (Top)
    col_clear, _ = st.columns([1, 5])
    with col_clear:
        if st.button("🧹 Clear"):
            st.session_state.clear()
            st.rerun()

    # ✅ File Upload
    file1 = st.file_uploader("Upload First Excel", type=["xlsx"], key="file1")
    file2 = st.file_uploader("Upload Second Excel", type=["xlsx"], key="file2")

    # ✅ Preview (Realtime)
    if file1 and file2:
        df1, df2 = compare_excels(file1, file2)
        diff_mask = get_diff_mask(df1, df2)

        st.subheader("🔍 Preview Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📄 File 1")
            styled1 = style_dataframe(df1, diff_mask)
            st.dataframe(styled1, use_container_width=True)

        with col2:
            st.markdown("### 📄 File 2")
            styled2 = style_dataframe(df2, diff_mask)
            st.dataframe(styled2, use_container_width=True)

        # ✅ Compare + Download
        if st.button("⚡ Generate Highlighted Excel"):
            try:
                file1_out, file2_out = generate_output(file1, file2)

                st.success("✅ Comparison completed!")

                with open(file1_out, "rb") as f:
                    st.download_button(
                        "⬇️ Download File 1 (Highlighted)",
                        f,
                        "file1_highlighted.xlsx"
                    )

                with open(file2_out, "rb") as f:
                    st.download_button(
                        "⬇️ Download File 2 (Highlighted)",
                        f,
                        "file2_highlighted.xlsx"
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")
