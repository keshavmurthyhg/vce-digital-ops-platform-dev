import streamlit as st
from modules.report.utils.rca_generator import generate_rca
from modules.report.doc_generator import generate_pdf, generate_word_doc_wrapper
from modules.report.bulk_generator import build_bulk_reports, generate_bulk_zip
from modules.report.utils.utils import clean_nan, format_date, extract_azure_id


# ---------------- PREVIEW TABLE ---------------- #

def render_preview_table(data):

    def val(x):
        return x if x else "-"

    def link(value, type_):
        if not value:
            return "-"

        if type_ == "incident":
            url = f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={value}"

        elif type_ == "azure":
            url = f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{value}"

        elif type_ == "ptc":
            url = f"https://support.ptc.com/appserver/cs/view/solution.jsp?n={value}"

        else:
            return value

        return f'<a href="{url}" target="_blank">{value}</a>'

    html = f"""
    <table style="width:100%; border-collapse: collapse; font-size:14px;">
        <tr>
            <td><b>INCIDENT</b></td>
            <td>{link(data.get("number"), "incident")}</td>
            <td><b>CREATED BY</b></td>
            <td>{val(data.get("created_by"))}</td>
        </tr>
        <tr>
            <td><b>AZURE BUG</b></td>
            <td>{link(data.get("azure_bug"), "azure")}</td>
            <td><b>CREATED DATE</b></td>
            <td>{val(data.get("created_date"))}</td>
        </tr>
        <tr>
            <td><b>PTC CASE</b></td>
            <td>{link(data.get("ptc_case"), "ptc")}</td>
            <td><b>ASSIGNED TO</b></td>
            <td>{val(data.get("assigned_to"))}</td>
        </tr>
        <tr>
            <td><b>PRIORITY</b></td>
            <td>{val(data.get("priority"))}</td>
            <td><b>RESOLVED DATE</b></td>
            <td>{val(data.get("resolved_date"))}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_description_table(data):
    def val(x):
        return x if x else "-"

    html = f"""
    <table style="width:100%; border-collapse: collapse; font-size:14px;">
        <tr>
            <td><b>SHORT DESCRIPTION</b></td>
            <td><b>DESCRIPTION</b></td>
        </tr>
        <tr>
            <td>{val(data.get("short_description"))}</td>
            <td>{val(data.get("description"))}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)


# ---------------- GET INCIDENT ---------------- #

def get_incident(df, inc):

    incident_col = "number" if "number" in df.columns else df.columns[0]

    row = df[df[incident_col].astype(str).str.upper() == inc.upper()]

    if row.empty:
        return None

    r = row.iloc[0]

    resolution_text = r.get("resolution notes", "")
    azure_id = extract_azure_id(resolution_text)

    return {
        "number": clean_nan(r.get("number")),
        "short_description": clean_nan(r.get("short description")),
        "description": clean_nan(r.get("description")),
        "priority": clean_nan(r.get("priority")),
        "created_by": clean_nan(r.get("caller")),
        "created_date": format_date(r.get("created")),
        "assigned_to": clean_nan(r.get("assigned to")),
        "resolved_date": format_date(r.get("resolved")),

        "work_notes": r.get("work notes", ""),
        "comments": r.get("additional comments", ""),
        "resolution": resolution_text,

        "azure_bug": azure_id if azure_id else clean_nan(r.get("azure bug")),
        "ptc_case": clean_nan(r.get("vendor ticket")),
    }


# ---------------- MAIN UI ---------------- #

def render_main(df):

    st.title("Incident Report Generator")

    # INIT STATE
    for key in ["root", "l2", "res", "images"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "images" else {"root": [], "l2": [], "res": []}

    # INCIDENT SELECT
    col1, col2 = st.columns([4, 1])

    with col1:
        incident_col = "number" if "number" in df.columns else df.columns[0]

        incident = st.selectbox(
            "Select Incident",
            df[incident_col].dropna().astype(str).unique()
        )

    with col2:
        st.write("")
        st.write("")
        fetch = st.button("Fetch", use_container_width=True)

    msg = st.empty()

    # FETCH
    if fetch:
        data = get_incident(df, incident)

        if data:
            st.session_state["data"] = data

            rca = generate_rca(data)

            st.session_state["root"] = rca["problem"]
            st.session_state["l2"] = rca["analysis"]
            st.session_state["res"] = rca["resolution"]

            msg.success("Loaded successfully")
        else:
            msg.error("Incident not found")

    # BULK
    st.markdown("### Bulk Incident Numbers")
    bulk_input = st.text_area("Enter comma-separated incident numbers", key="bulk_ids")

    # BUTTONS
    colA, colB, colC, colD, colE = st.columns(5)

    with colA:
        pdf_btn = st.button("Generate PDF", use_container_width=True)

    with colB:
        word_btn = st.button("Generate Word", use_container_width=True)

    with colC:
        bulk_btn = st.button("Bulk Generate", use_container_width=True)

    with colD:
        clear_btn = st.button("Clear", use_container_width=True)

    with colE:
        preview_btn = st.button("Preview", use_container_width=True)

    # CLEAR
    if clear_btn:
        st.session_state.clear()
        st.rerun()

    # PREVIEW
    if preview_btn and "data" in st.session_state:
        data = st.session_state["data"]

        st.markdown("### Preview")
        render_preview_table(data)
        render_description_table(data)

    # EDIT
    st.subheader("Edit Report Details")

    st.session_state["root"] = st.text_area(
        "PROBLEM STATEMENT",
        value=st.session_state.get("root", ""),
        height=150
    )

    root_imgs = st.file_uploader("Root Images", accept_multiple_files=True, key="root_img")

    st.session_state["l2"] = st.text_area(
        "ROOT CAUSE",
        value=st.session_state.get("l2", ""),
        height=150
    )

    l2_imgs = st.file_uploader("L2 Images", accept_multiple_files=True, key="l2_img")

    st.session_state["res"] = st.text_area(
        "RESOLUTION & RECOMMENDATION",
        value=st.session_state.get("res", ""),
        height=150
    )

    res_imgs = st.file_uploader("Resolution Images", accept_multiple_files=True, key="res_img")

    st.session_state["images"] = {
        "root": root_imgs or [],
        "l2": l2_imgs or [],
        "res": res_imgs or []
    }

    # PDF
    if pdf_btn:
        if "data" not in st.session_state:
            st.warning("Fetch incident first")
        else:
            pdf_bytes = generate_pdf(
                st.session_state["data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"],
                st.session_state["images"]
            )

            st.download_button("Download PDF", pdf_bytes, "report.pdf")

    # WORD
    if word_btn:
        if "data" not in st.session_state:
            st.warning("Fetch incident first")
        else:
            word_bytes = generate_word_doc_wrapper(
                st.session_state["data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"],
                st.session_state["images"]
            )

            st.download_button("Download Word", word_bytes, "report.docx")
