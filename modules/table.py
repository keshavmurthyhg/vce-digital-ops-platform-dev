import streamlit as st

def show_table(df):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Number": st.column_config.TextColumn(width="small"),
            "Description": st.column_config.TextColumn(width="large"),
            "Priority": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="small"),
            "Created By": st.column_config.TextColumn(width="medium"),
        }
    )
