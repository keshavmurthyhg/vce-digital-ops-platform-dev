import streamlit as st
from modules.doc_generator import generate_word_doc, generate_pdf

st.set_page_config(layout="wide")

# ================= SIDEBAR =================
st.sidebar.title("Module")
module = st.sidebar.selectbox("Select Module", ["Word Report Generator"])

st.sidebar.title("Filters")

priority_filter = st.sidebar.multiselect(
    "Priority",
    ["Priority 1", "Priority 2", "Priority 3", "Priority 4"]
)

date_range = st.sidebar.date_input("Created Date Range", [])

if st.sidebar.button("Apply Filters to Bulk"):
    # Example logic (keep your existing logic if any)
    if priority_filter:
        st.session_state["bulk"] = ",".join(["INC123", "INC456"])
        st.session_state["msg"] = "Filters applied to bulk"

# CLEAR BUTTON (FIXED)
if st.sidebar.button("Clear"):
    st.session_state.clear()
    st.rerun()


# ================= MAIN =================
st.title("SNOW Incident Report Generator")

incident = st.text_input("Enter Incident Number", key="incident")

bulk = st.text_area(
    "Bulk Incident Numbers (comma separated)",
    key="bulk"
)

# ================= BUTTON ROW =================
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

# FETCH
with col1:
    if st.button("Fetch"):
        st.session_state["doc_data"] = {
            "number": incident,
            "azure_bug": "695698",
            "ptc_case": "18007559",
            "priority": "Priority 4",
            "created_by": "Jordan Bingaman",
            "created_date": "2026-01-29",
            "assigned_to": "Keshavamurthy Hg",
            "resolved_date": "2026-02-16",
            "short_description": "Edit Association button is missing",
            "description": "Users need to be able to edit association..."
        }
        st.session_state["msg"] = "Incident loaded"


# WORD
with col2:
    if st.button("Word") and "doc_data" in st.session_state:
        st.session_state["word_file"] = generate_word_doc(
            st.session_state["doc_data"],
            st.session_state.get("root", ""),
            st.session_state.get("l2", ""),
            st.session_state.get("res", ""),
            st.session_state.get("images")
        )
        st.session_state["msg"] = "Word generated"

    if "word_file" in st.session_state:
        st.download_button(
            "⬇",
            st.session_state["word_file"],
            file_name=f"{st.session_state['doc_data']['number']}.docx"
        )


# PDF
with col3:
    if st.button("PDF") and "doc_data" in st.session_state:
        st.session_state["pdf_file"] = generate_pdf(
            st.session_state["doc_data"],
            st.session_state.get("root", ""),
            st.session_state.get("l2", ""),
            st.session_state.get("res", ""),
            st.session_state.get("images")
        )
        st.session_state["msg"] = "PDF generated"

    if "pdf_file" in st.session_state:
        st.download_button(
            "⬇",
            st.session_state["pdf_file"],
            file_name=f"{st.session_state['doc_data']['number']}.pdf"
        )


# BULK
with col4:
    if st.button("Bulk"):
        st.session_state["msg"] = "Bulk ZIP ready"


# PREVIEW (FIXED — NOT RAW JSON)
with col5:
    if st.button("Preview") and "doc_data" in st.session_state:
        st.session_state["preview"] = True


# ================= MESSAGE =================
if "msg" in st.session_state:
    st.success(st.session_state["msg"])


# ================= PREVIEW =================
if st.session_state.get("preview") and "doc_data" in st.session_state:

    st.markdown("## INCIDENT REPORT")

    d = st.session_state["doc_data"]

    st.markdown(f"""
    **Incident:** {d['number']}  
    **Azure Bug:** {d['azure_bug']}  
    **PTC Case:** {d['ptc_case']}  
    **Priority:** {d['priority']}  
    """)

    st.markdown("### Short Description")
    st.write(d["short_description"])

    st.markdown("### Description")
    st.write(d["description"])


# ================= TEXT INPUTS =================
st.markdown("---")

root = st.text_area("Root Cause", key="root")
l2 = st.text_area("L2 Analysis", key="l2")
res = st.text_area("Resolution", key="res")


# ================= IMAGE SUPPORT =================
st.markdown("### Attach Images")

root_img = st.file_uploader("Root Image", key="root_img")
l2_img = st.file_uploader("L2 Image", key="l2_img")
res_img = st.file_uploader("Resolution Image", key="res_img")

st.session_state["images"] = {
    "root": root_img,
    "l2": l2_img,
    "res": res_img
}
