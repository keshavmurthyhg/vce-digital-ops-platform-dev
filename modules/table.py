import streamlit as st
import pandas as pd
import re


def clean_name(value):
    try:
        if pd.isna(value):
            return value

        value = str(value)
        value = re.sub(r"\s*<.*?>", "", value)
        value = re.sub(r"\s*\(.*?\)", "", value)
        return value.strip()

    except Exception:
        return value


def show_table(df):

    # --- Copy ---
    df = df.copy()

    # --- SL No ---
    df = df.reset_index(drop=True)
    df.insert(0, "SL No", df.index + 1)

    # --- Clean Names ---
    for col in ["Created By", "Assigned To"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_name)

    # --- Date Format ---
    for col in ["Created Date", "Resolution Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d-%b-%y")

    # --- Row selector ---
    selected_index = st.selectbox(
        "🔍 Select a row to preview",
        options=df.index,
        format_func=lambda x: f"{df.loc[x, 'Number']} | {df.loc[x, 'Description'][:60]}..."
    )

    # --- Alignment CSS ---
    st.markdown("""
    <style>
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] td {
        text-align: center !important;
        vertical-align: middle !important;
    }

    /* Left align text-heavy columns */
    [data-testid="stDataFrame"] td:nth-child(4),
    [data-testid="stDataFrame"] td:nth-child(8),
    [data-testid="stDataFrame"] td:nth-child(9) {
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Table ---
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # --- Preview Panel ---
    st.markdown("---")
    st.markdown("### 🔎 Preview")

    selected_row = df.loc[selected_index]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Number:** {selected_row.get('Number', '')}")
        st.markdown(f"**Priority:** {selected_row.get('Priority', '')}")
        st.markdown(f"**Status:** {selected_row.get('Status', '')}")
        st.markdown(f"**Created By:** {selected_row.get('Created By', '')}")
        st.markdown(f"**Assigned To:** {selected_row.get('Assigned To', '')}")

    with col2:
        st.markdown(f"**Created Date:** {selected_row.get('Created Date', '')}")
        st.markdown(f"**Resolution Date:** {selected_row.get('Resolution Date', '')}")
        st.markdown(f"**Source:** {selected_row.get('Source', '')}")

    st.markdown("#### 📝 Description")
    st.info(selected_row.get("Description", ""))
