import streamlit as st
import pandas as pd
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc, generate_pdf
import re
from io import BytesIO
import zipfile


# ================= AZURE ID =================
def extract_azure_link(text):
    if not text:
        return ""
    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""


# ================= DATE FORMAT =================
def format_date(date_val):
    if not date_val:
        return ""
    try:
        return pd.to_datetime(date_val).strftime("%d-%b-%Y")
    except:
        return str(date_val)


# ================= FETCH =================
def get_incident_from_df(df, incident_number):

    df_copy = df.copy()

    df_copy["number"] = df_copy["number"].astype(str).str.strip().str.upper()
    incident_number = incident_number.strip().upper()

    row = df_copy[df_copy["number"] == incident_number]

    if not row.empty:
        row = row.iloc[0]

        return {
            "number": row.get("number", ""),
            "short_description": row.get("short description", ""),
            "description": row.get("description", ""),

            "priority": row.get("priority", ""),
            "created_by": row.get("caller", ""),
            "created_date": format_date(row.get("created", "")),
            "assigned_to": row.get("assigned to", ""),
            "resolved_date": format_date(row.get("resolved", "")),

            "work_notes": row.get("work notes", ""),
            "comments": row.get("additional comments", ""),
            "resolution": row.get("resolution notes", ""),

            "ptc_case": row.get("vendor ticket", ""),
            "azure_bug": extract_azure_link(row.get("resolution notes", ""))
        }

    return None


# ================= UI =================
def render_doc_generator():

    st.title("📄 SNOW Incident Report Generator")

    df = load_snow_data()

    if "state" in df.columns:
        df["state"] = df["state"].fillna("Unknown").astype(str)

    # ================= SIDEBAR =================
        # ---------- SIDEBAR ----------
   # st.sidebar.markdown("## 📊 Module")
    
   # options = [
   #     "Search Dashboard",
   #     "Insights Dashboard",
   #     "Word Report Generator"
 #   ]
    
    # ✅ Safe default
 #   if "page" not in st.session_state or st.session_state.page not in options:
  #      st.session_state.page = "Search Dashboard"
    
   # page = st.sidebar.selectbox(
    #    "Module",
    #    options,
     #   index=options.index(st.session_state.page),
   #     label_visibility="collapsed"
   # )
    
    # ✅ Persist selection
   # st.session_state.page = page

    # ================= INPUT =================
    incident_number = st.text_input("Enter Incident Number")

    bulk_ids = st.text_area(
        "Bulk Incident Numbers (comma separated)",
        key="bulk_ids"
    )

    col1, col2, col3, col4 = st.columns(4)

    # ================= FETCH =================
    if col1.button("Fetch"):
        data = get_incident_from_df(df, incident_number)

        if data:
            st.session_state["doc_data"] = data
            st.session_state["root"] = data.get("work_notes", "")
            st.session_state["l2"] = data.get("comments", "")
            st.session_state["res"] = data.get("resolution", "")

            st.success("✅ Incident loaded")
        else:
            st.warning("❌ Incident not found")

   

    # ================= WORD =================

    if st.button("📄 Generate Word Report"):
    
        if "doc_data" not in st.session_state:
            st.warning("❌ Please fetch incident first")
    
        else:
            try:
                buffer = generate_word_doc(
                    st.session_state["doc_data"],
                    st.session_state.get("root", ""),
                    st.session_state.get("l2", ""),
                    st.session_state.get("res", "")
                )
    
                # ✅ CRITICAL FIX (deep copy of bytes)
                word_bytes = buffer.getvalue()
                st.session_state["word_file"] = bytes(word_bytes)
    
                st.success("✅ Word generated successfully")
    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    
    # ✅ DOWNLOAD (stable)
    if "word_file" in st.session_state:
        st.download_button(
            "⬇ Download Word",
            data=st.session_state["word_file"],
            file_name=f"{st.session_state['doc_data']['number']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    # ================= PDF =================
    if col3.button("PDF"):
        if "doc_data" in st.session_state:
            st.session_state["pdf_file"] = generate_pdf(
                st.session_state["doc_data"],
                st.session_state.get("root", ""),
                st.session_state.get("l2", ""),
                st.session_state.get("res", "")
            )

    if "pdf_file" in st.session_state:
        col3.download_button(
            "⬇",
            st.session_state["pdf_file"],
            f"{st.session_state['doc_data']['number']}.pdf"
        )

    # ================= BULK =================
    if col4.button("Bulk"):

        ids = [i.strip().upper() for i in bulk_ids.split(",") if i.strip()]

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for inc in ids:
                data = get_incident_from_df(df, inc)
                if data:
                    file = generate_word_doc(data, "", "", "")
                    zf.writestr(f"{inc}.docx", file.getvalue())

        zip_buffer.seek(0)
        st.session_state["zip_file"] = zip_buffer

    if "zip_file" in st.session_state:
        col4.download_button(
            "⬇ ZIP",
            st.session_state["zip_file"],
            "incident_reports.zip"
        )

    # ================= TEXT AREAS =================
    st.text_area("Root Cause", key="root")
    st.text_area("L2 Analysis", key="l2")
    st.text_area("Resolution", key="res")
