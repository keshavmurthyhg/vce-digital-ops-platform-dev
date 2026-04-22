import streamlit as st
from io import BytesIO
import zipfile
import re

from modules.search.snow_loader import load_snow_data
from modules.report.doc_generator import generate_word, generate_pdf_report


# ---------------- CLEAR ---------------- #
def clear_all():
    st.session_state["uploader_reset"] = st.session_state.get("uploader_reset", 0) + 1

    for key in [
        "data", "word_file", "pdf_file", "zip_file",
        "root", "l2", "res", "bulk_ids"
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


# ---------------- HELPERS ---------------- #
def extract_azure_link(text):
    if not text:
        return ""
    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""


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
        "work_notes": r.get("work notes", ""),
        "comments": r.get("additional comments", ""),
        "resolution": r.get("resolution notes", ""),
        "ptc_case": r.get("vendor ticket"),
        "azure_bug": extract_azure_link(r.get("resolution notes"))
    }


# ---------------- MAIN UI ---------------- #
def render():

    st.title("📄 SNOW Incident Report Generator")

    df = load_snow_data()

    # ---------- SIDEBAR ----------
    st.sidebar.header("Filters")

    priority_sel = st.sidebar.multiselect(
        "Priority",
        df["priority"].dropna().unique()
    )

    if st.sidebar.button("Apply Filters to Bulk"):
        filtered = df.copy()

        if priority_sel:
            filtered = filtered[filtered["priority"].isin(priority_sel)]

        st.session_state["bulk_ids"] = ", ".join(
            filtered["number"].astype(str).tolist()
        )

    if st.sidebar.button("Clear All"):
        clear_all()

    # ---------- INPUT ----------
    inc = st.text_input("Enter Incident Number", key="inc_input")
    bulk = st.text_area("Bulk Incident Numbers", key="bulk_ids")

    col_fetch, col_word, col_pdf, col_bulk, col_prev = st.columns(5)

    # ---------- FETCH ----------
    with col_fetch:
        if st.button("Fetch", use_container_width=True):
            data = get_incident(df, inc)

            if data:
                st.session_state["data"] = data
                st.session_state["root"] = data["work_notes"]
                st.session_state["l2"] = data["comments"]
                st.session_state["res"] = data["resolution"]
                st.success("Loaded")
            else:
                st.error("Not found")

    # ---------- WORD ----------
    with col_word:
        if st.button("Word", use_container_width=True):
            if "data" in st.session_state:
                st.session_state["word_file"] = generate_word(
                    st.session_state["data"],
                    st.session_state.get("root", ""),
                    st.session_state.get("l2", ""),
                    st.session_state.get("res", ""),
                    st.session_state.get("images")
                )

        if "word_file" in st.session_state:
            st.download_button(
                "⬇ Word",
                st.session_state["word_file"],
                file_name=f"{st.session_state['data']['number']}_report.docx",
                use_container_width=True
            )

    # ---------- PDF ----------
    with col_pdf:
        if st.button("PDF", use_container_width=True):
            if "data" in st.session_state:
                st.session_state["pdf_file"] = generate_pdf_report(
                    st.session_state["data"],
                    st.session_state.get("root", ""),
                    st.session_state.get("l2", ""),
                    st.session_state.get("res", ""),
                    st.session_state.get("images")
                )

        if "pdf_file" in st.session_state:
            st.download_button(
                "⬇ PDF",
                st.session_state["pdf_file"],
                file_name=f"{st.session_state['data']['number']}_report.pdf",
                use_container_width=True
            )

    # ---------- BULK ----------
    with col_bulk:
        if st.button("Bulk", use_container_width=True):

            ids = [i.strip() for i in bulk.split(",") if i.strip()]

            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as z:
                for i in ids:
                    d = get_incident(df, i)

                    if d:
                        file = generate_word(d, "", "", "")
                        z.writestr(f"{i}_report.docx", file.getvalue())

            zip_buffer.seek(0)
            st.session_state["zip_file"] = zip_buffer

        if "zip_file" in st.session_state:
            st.download_button(
                "⬇ ZIP",
                st.session_state["zip_file"],
                "bulk_reports.zip",
                use_container_width=True
            )

    # ---------- PREVIEW ----------
    with col_prev:
        show_prev = st.button("Preview", use_container_width=True)

    if show_prev and "data" in st.session_state:
        with st.expander("Preview", True):
            st.write(f"**Short Description:** {st.session_state['data']['short_description']}")
            st.write(f"**Root Cause:** {st.session_state.get('root')}")

    # ---------- EDIT ----------
    st.subheader("Edit Report")

    reset_id = st.session_state.get("uploader_reset", 0)

    st.text_area("Root Cause", key="root")
    root_img = st.file_uploader("Root Image", type=["png", "jpg"], key=f"root_{reset_id}")

    st.text_area("L2 Analysis", key="l2")
    l2_img = st.file_uploader("L2 Image", type=["png", "jpg"], key=f"l2_{reset_id}")

    st.text_area("Resolution", key="res")
    res_img = st.file_uploader("Resolution Image", type=["png", "jpg"], key=f"res_{reset_id}")

    st.session_state["images"] = {
        "root": root_img,
        "l2": l2_img,
        "res": res_img
    }
