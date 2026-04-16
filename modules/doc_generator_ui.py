import streamlit as st
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc


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

            # ✅ KEY FIX (now available)
            "work_notes": row.get("work notes", ""),
            "comments": row.get("additional comments", ""),
            "resolution": row.get("resolution notes", "")
        }

    return None

# ================= UI =================
def render_doc_generator():

    st.title("📄 SNOW Incident Report Generator")

    df = load_snow_data()

    # 🔍 DEBUG START (ADD HERE)
    #st.write("Columns:", df.columns)
    #st.write("Sample Row:", df.head(1))
    # 🔍 DEBUG END

    incident_number = st.text_input("Enter Incident Number")

    col1, col2 = st.columns(2)

    # ================= FETCH =================
    if col1.button("Fetch Incident"):

        data = get_incident_from_df(df, incident_number)

        if data:
            st.session_state["doc_data"] = data

            # ✅ FORCE UPDATE TEXT FIELDS
            st.session_state["root"] = data.get("work_notes", "")
            st.session_state["l2"] = data.get("comments", "")
            st.session_state["res"] = data.get("resolution", "")
            st.session_state["closure"] = data.get("resolution", "")

        else:
            st.warning("❌ Incident not found in dataset")

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
