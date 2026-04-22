import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile

from modules.excel_compare.logic import compare_excels


def render():

    st.title("📊 Excel Compare Tool")

    col1, col2 = st.columns(2)

    old_file = col1.file_uploader("Upload OLD file", type=["xlsx"])
    new_file = col2.file_uploader("Upload NEW file", type=["xlsx"])

    key_column = st.text_input("Key Column (e.g., Part Number)")

    if old_file and new_file and key_column:

        old_df, new_df, added, removed, modified = compare_excels(
            old_file, new_file, key_column
        )

        st.success("Comparison complete")

        # ---------- KPI ----------
        c1, c2, c3 = st.columns(3)
        c1.metric("Added", len(added))
        c2.metric("Removed", len(removed))
        c3.metric("Modified", len(modified))

        # ---------- PREVIEW ----------
        tab1, tab2, tab3 = st.tabs(["Added", "Removed", "Modified"])

        with tab1:
            st.dataframe(added)

        with tab2:
            st.dataframe(removed)

        with tab3:
            st.dataframe(modified)

        # ---------- EXPORT ----------
        if st.button("Download Results (ZIP)"):

            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as z:

                # Added
                buf1 = BytesIO()
                added.to_excel(buf1, index=False)
                z.writestr("added.xlsx", buf1.getvalue())

                # Removed
                buf2 = BytesIO()
                removed.to_excel(buf2, index=False)
                z.writestr("removed.xlsx", buf2.getvalue())

                # Modified
                buf3 = BytesIO()
                modified.to_excel(buf3, index=False)
                z.writestr("modified.xlsx", buf3.getvalue())

            zip_buffer.seek(0)

            st.download_button(
                "⬇ Download ZIP",
                zip_buffer,
                file_name="excel_compare_results.zip"
            )
