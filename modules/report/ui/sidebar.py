import streamlit as st
import pandas as pd
from datetime import date, timedelta

def render_sidebar(df):

    st.sidebar.header("Filters")

    priorities = st.sidebar.multiselect(
        "Priority",
        options=sorted(df["priority"].dropna().unique())
    )

    date_range = st.sidebar.date_input(
        "Created Date Range",
        value=(),
    )

    preset = st.sidebar.selectbox(
        "Quick Filter",
        ["None", "Last 7 Days", "Last 30 Days"]
    )

    from datetime import date, timedelta
    
    if preset == "Last 7 Days":
        date_range = (date.today() - timedelta(days=7), date.today())
    
    elif preset == "Last 30 Days":
        date_range = (date.today() - timedelta(days=30), date.today())
    
    # Apply filters
    filtered = df.copy()

    # Priority filter
    if priorities:
        filtered = filtered[filtered["priority"].isin(priorities)]

    # 🔹 Convert timestamp safely
    filtered["created"] = pd.to_datetime(filtered["created"], errors="coerce")

    # 🔹 Date filter (safe handling)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
    
        filtered["created"] = pd.to_datetime(filtered["created"], errors="coerce")
    
        filtered = filtered[
            (filtered["created"].dt.date >= start) &
            (filtered["created"].dt.date <= end)
        ]

    # 🔹 Apply to bulk
    st.sidebar.markdown("### Actions")

    if st.sidebar.button("Apply to Bulk"):
        st.session_state["apply_bulk"] = True

    if st.session_state.get("apply_bulk"):

        df = st.session_state.get("filtered_df")
        bulk_input = st.session_state.get("bulk_incidents", "")
    
        if df is None:
            st.sidebar.error("No data available")
        
        elif not bulk_input.strip():
            st.sidebar.warning("Enter bulk incident numbers first")
    
        else:
            bulk_ids = [i.strip() for i in bulk_input.split(",") if i.strip()]
    
            bulk_data = []
    
            for inc in bulk_ids:
                incident_col = next(
                    (c for c in df.columns if "number" in c.lower()),
                    None
                )
    
                if not incident_col:
                    continue
    
                row = df[df[incident_col].astype(str).str.upper() == inc.upper()]
    
                if row.empty:
                    continue
    
                data = row.iloc[0].to_dict()
    
                # ✅ APPLY CURRENT EDITED CONTENT
                data["problem"] = st.session_state.get("problem", "")
                data["analysis"] = st.session_state.get("analysis", "")
                data["resolution"] = st.session_state.get("resolution", "")
    
                # ✅ APPLY IMAGES
                data["images"] = st.session_state.get("images", {})
    
                bulk_data.append(data)
    
            st.session_state["bulk_data"] = bulk_data
    
            st.sidebar.success(f"Applied to {len(bulk_data)} incidents")

    
    #================= DOWNLOAD BUTTONS ================================
    st.sidebar.markdown("### Download")
    
    if "pdf_bytes" in st.session_state and "data" in st.session_state:
        st.sidebar.download_button(
            "⬇ Download PDF",
            data=st.session_state["pdf_bytes"],
            file_name=f"{st.session_state['data']['number']}.pdf",
            mime="application/pdf"
        )
    
    if "word_bytes" in st.session_state and "data" in st.session_state:
        st.sidebar.download_button(
            "⬇ Download Word",
            data=st.session_state["word_bytes"],
            file_name=f"{st.session_state['data']['number']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    if "zip_bytes" in st.session_state:
        st.sidebar.download_button(
            "⬇ Download ZIP",
            data=st.session_state["zip_bytes"],
            file_name="Bulk_Report.zip",
            mime="application/zip"
        )
    
    # ✅ CRITICAL FIX
    return filtered
