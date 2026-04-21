import streamlit as st
from modules.excel_compare.logic import compare_excels, generate_output


def show_excel_compare():
    st.title("📊 Excel Comparison Tool")

    file1 = st.file_uploader("Upload First Excel", type=["xlsx"], key="file1")
    file2 = st.file_uploader("Upload Second Excel", type=["xlsx"], key="file2")

    if file1 and file2:
        if st.button("Compare Files"):
            try:
                df1, df2 = compare_excels(file1, file2)

                output_path = generate_output(df1, df2)

                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download Compared Excel",
                        data=f,
                        file_name="comparison_output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                st.success("Comparison completed successfully!")

            except Exception as e:
                st.error(f"Error: {str(e)}")
