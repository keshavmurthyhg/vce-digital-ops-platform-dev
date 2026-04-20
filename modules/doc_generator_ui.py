import streamlit as st
import pandas as pd
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc, generate_pdf
from io import BytesIO
import zipfile
import re


# ================= CLEAR =================
def clear_all():
    st.session_state.clear()
    st.rerun()


# ================= AZURE EXTRACT =================
def extract_azure_link(text):
    if not text:
        return ""
    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""


# ================= FETCH =================
def get_incident(df, inc):
    df["number"] = df["number"].astype(str).str.upper()
    row = df[df["number"] == inc.upper()]

    if row.empty:
        return None

    r = row.iloc[0]

    return {
        "number": r.get("number"),
        "short_description": r.get("short description"),
        "description": r.get("description"),
        "priority": r.get("priority"),
        "created_by": r.get("caller"),
        "created_date": str(r.get("created")).split()[0],
        "assigned_to": r.get("assigned to"),
        "resolved_date": str(r.get("resolved")).split()[0],
        "work_notes": r.get("work notes"),
        "comments": r.get("additional comments"),
        "resolution": r.get("resolution notes"),
        "ptc_case": r.get("vendor ticket"),
        "azure_bug": extract_azure_link(r.get("resolution notes"))
    }


# ================= UI =================
def render_doc_generator():

    st.title("📄 SNOW Incident Report Generator")

    df = load_snow_data()

    # ================= SIDEBAR =================
    st.sidebar.header("Filters")

    priority = st.sidebar.multiselect(
        "Priority", df["priority"].dropna().unique()
    )

    date_range = st.sidebar.date_input("Created Date Range", [])

    if st.sidebar.button("Apply Filters to Bulk"):
        filtered = df.copy()

        if priority:
            filtered = filtered[filtered["priority"].isin(priority)]

        st.session_state["bulk_ids"] = ", ".join(
            filtered["number"].astype(str).tolist()
        )

    if st.sidebar.button("Clear"):
        clear_all()

    # ================= INPUT =================
    inc = st.text_input("Enter Incident Number")

    bulk = st.text_area("Bulk Incident Numbers", key="bulk_ids")

    # ================= STATUS =================
    status = st.empty()

    # ================= BUTTON ROW =================
    col1, col2, col3, col4, col5 = st.columns(5)

    # ================= FETCH =================
    if col1.button("Fetch"):
        data = get_incident(df, inc)

        if data:
            st.session_state["data"] = data
            st.session_state["root"] = data["work_notes"]
            st.session_state["l2"] = data["comments"]
            st.session_state["res"] = data["resolution"]
            status.success("✅ Incident loaded")
        else:
            status.error("❌ Incident not found")

    # ================= WORD =================
    if col2.button("Word"):
        if "data" in st.session_state:
            st.session_state["word"] = generate_word_doc(
                st.session_state["data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"],
                st.session_state.get("images")
            )
            status.success("✅ Word generated")

    if "word" in st.session_state:
        col2.download_button(
            "⬇",
            st.session_state["word"],
            file_name=f"{st.session_state['data']['number']}.docx"
        )

    # ================= PDF =================
    if col3.button("PDF"):
        if "data" in st.session_state:
            st.session_state["pdf"] = generate_pdf(
                st.session_state["data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"],
                st.session_state.get("images")
            )
            status.success("✅ PDF generated")

    if "pdf" in st.session_state:
        col3.download_button(
            "⬇",
            st.session_state["pdf"],
            file_name=f"{st.session_state['data']['number']}.pdf"
        )

    # ================= BULK =================
    if col4.button("Bulk"):
        ids = [i.strip() for i in bulk.split(",") if i.strip()]

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for i in ids:
                d = get_incident(df, i)
                if d:
                    f = generate_word_doc(d, "", "", "")
                    z.writestr(f"{i}.docx", f.getvalue())

        zip_buffer.seek(0)
        st.session_state["zip"] = zip_buffer
        status.success("✅ Bulk ZIP ready")

    if "zip" in st.session_state:
        col4.download_button("⬇ ZIP", st.session_state["zip"], "reports.zip")

    # ================= PREVIEW =================
    if col5.button("Preview"):
        if "data" in st.session_state:
            st.write("### Preview")

            st.markdown("**Short Description**")
            st.write(st.session_state["data"]["short_description"])

            st.markdown("**Description**")
            st.write(st.session_state["data"]["description"])

            st.markdown("**Root Cause**")
            st.write(st.session_state.get("root"))

            st.markdown("**L2 Analysis**")
            st.write(st.session_state.get("l2"))

            st.markdown("**Resolution**")
            st.write(st.session_state.get("res"))

    # ================= TEXT =================
    st.text_area("Root Cause", key="root")
    root_img = st.file_uploader("Root Image", type=["png", "jpg"])

    st.text_area("L2 Analysis", key="l2")
    l2_img = st.file_uploader("L2 Image", type=["png", "jpg"])

    st.text_area("Resolution", key="res")
    res_img = st.file_uploader("Resolution Image", type=["png", "jpg"])

    # ================= STORE IMAGES =================
    st.session_state["images"] = {
        "root": root_img,
        "l2": l2_img,
        "res": res_img
    }
