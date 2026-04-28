import streamlit as st


def _val(x):
    return x if x and x != "-" else "-"


def _link(value, type_):
    if not value or value == "-":
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


def render_preview(data):

    style = """
    <style>
    .tbl {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .tbl td {
        border: 1px solid black;
        padding: 8px;
    }
    .hdr {
        font-weight: bold;
        background: #f2f2f2;
        width: 20%;
    }
    </style>
    """

    table1 = f"""
    <table class="tbl">
        <tr>
            <td class="hdr">INCIDENT</td>
            <td>{_link(data.get("number"), "incident")}</td>
            <td class="hdr">CREATED BY</td>
            <td>{_val(data.get("created_by"))}</td>
        </tr>
        <tr>
            <td class="hdr">AZURE BUG</td>
            <td>{_link(data.get("azure_bug"), "azure")}</td>
            <td class="hdr">CREATED DATE</td>
            <td>{_val(data.get("created_date"))}</td>
        </tr>
        <tr>
            <td class="hdr">PTC CASE</td>
            <td>{_link(data.get("ptc_case"), "ptc")}</td>
            <td class="hdr">ASSIGNED TO</td>
            <td>{_val(data.get("assigned_to"))}</td>
        </tr>
        <tr>
            <td class="hdr">PRIORITY</td>
            <td>{_val(data.get("priority"))}</td>
            <td class="hdr">RESOLVED DATE</td>
            <td>{_val(data.get("resolved_date"))}</td>
        </tr>
    </table>
    """

    table2 = f"""
    <table class="tbl">
        <tr>
            <td class="hdr">SHORT DESCRIPTION</td>
            <td class="hdr">DESCRIPTION</td>
        </tr>
        <tr>
            <td>{_val(data.get("short_description"))}</td>
            <td>{_val(data.get("description"))}</td>
        </tr>
    </table>
    """

    # ✅ CRITICAL FIX HERE
    st.markdown(style + table1 + table2, unsafe_allow_html=True)
