import streamlit as st
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc
import re

def extract_azure_link(text):
    if not text:
        return ""

    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""

# ================= FETCH FUNCTION =================
def get_incident_from_df(df, incident_number):

    df_copy = df.copy()

    # normalize
    df_copy["number"] = df_copy["number"].astype(str).str.strip().str.upper()
    incident_number = incident_number.strip().upper()

    row = df_copy[df_copy["number"] == incident_number]

    if not row.empty:
        row = row.iloc[0]

        return {
    "number": row.get("number", ""),
    "short_description": row.get("short description", ""),
    "description": row.get("description", ""),

    # ✅ FIXED MAPPINGS
    "priority": row.get("priority", ""),
    "created_by": row.get("caller", ""),              # ✅ FIX
    "created_date": row.get("created", ""),           # ✅ FIX
    "assigned_to": row.get("assigned to", ""),
    "resolved_date": row.get("resolved", ""),         # ✅ FIX

    "work_notes": row.get("work notes", ""),
    "comments": row.get("additional comments", ""),
    "resolution": row.get("resolution notes", ""),

    # ✅ FIXED
    "ptc_case": row.get("vendor ticket", ""),

    # ✅ NEW (Azure extraction handled below)
    "azure_bug": extract_azure_link(row.get("resolution notes", ""))
}

    return None


# ================= UI =================
def render_doc_generator():

    st.title("📄 SNOW Incident Report Generator")
    filtered_df = df.copy()
    
    if priority_filter:
        filtered_df = filtered_df[filtered_df["priority"].isin(priority_filter)]
    
    if state_filter and "state" in df.columns:
        filtered_df = filtered_df[filtered_df["state"].isin(state_filter)]
    
    if len(date_filter) == 2:
        filtered_df["created"] = pd.to_datetime(filtered_df["created"], errors='coerce')
        filtered_df = filtered_df[
            (filtered_df["created"] >= pd.to_datetime(date_filter[0])) &
            (filtered_df["created"] <= pd.to_datetime(date_filter[1]))
    ]
    
    df = filtered_df
   
    df = load_snow_data()

    incident_number = st.text_input("Enter Incident Number")
    
    bulk_ids = st.text_area("Bulk Incident Numbers (comma separated)")
    
    col1, col2, col3, col4 = st.columns(4)

    # ================= FETCH =================
    if col1.button("Fetch Incident"):

        data = get_incident_from_df(df, incident_number)

        if data:
            st.session_state["doc_data"] = data

            # auto-fill editable fields
            st.session_state["root"] = data.get("work_notes", "")
            st.session_state["l2"] = data.get("comments", "")
            st.session_state["res"] = data.get("resolution", "")
            st.session_state["closure"] = data.get("resolution", "")

            st.success("✅ Incident loaded")

        else:
            st.warning("❌ Incident not found in Snow data")

    # ================= FORM =================
    root_cause = st.text_area("Root Cause", key="root")
    l2_analysis = st.text_area("L2 Analysis", key="l2")
    resolution = st.text_area("Resolution", key="res")
    closure = st.text_area("Closure Notes", key="closure")

    # ================= GENERATE =================
    if col2.button("Generate Document"):

        if "doc_data" not in st.session_state:
            st.warning("⚠️ Please fetch incident first")
            return

        file = generate_word_doc(
            st.session_state["doc_data"],
            root_cause,
            l2_analysis,
            resolution,
            closure
        )

        st.download_button(
            "📥 Download Report",
            file,
            f"{st.session_state['doc_data']['number']}.docx"
        )
   
    if col3.button("Preview"):
    if "doc_data" in st.session_state:
        st.json(st.session_state["doc_data"])

    if col4.download_button(
        "Download",
        file if "file" in locals() else None,
        f"{st.session_state.get('doc_data', {}).get('number','report')}.docx"
    ):
        pass
   
    if st.button("Bulk Generate"):
    
        ids = [i.strip().upper() for i in bulk_ids.split(",") if i.strip()]
    
        zip_buffer = BytesIO()
        import zipfile
    
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for inc in ids:
                data = get_incident_from_df(df, inc)
                if data:
                    file = generate_word_doc(data, "", "", "", "")
                    zf.writestr(f"{inc}.docx", file.getvalue())
    
        zip_buffer.seek(0)
    
        st.download_button(
            "Download ZIP",
            zip_buffer,
            "incident_reports.zip"
        )
