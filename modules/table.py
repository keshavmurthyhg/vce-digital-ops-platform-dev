import streamlit as st

def style_df(df):
    return df.style.set_properties(**{'text-align': 'center'}).set_properties(
        subset=["Description","Created By","Assigned To"],
        **{'text-align': 'left'}
    )

def show_table(df):
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Number": st.column_config.TextColumn(width="small"),
            "Description": st.column_config.TextColumn(width="large"),
            "Priority": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="small"),
            "Created By": st.column_config.TextColumn(width="medium"),
        },
        hide_index=True
    )
        "⬇️ Download",
        df.to_csv(index=False),
        "filtered_data.csv"
    )
