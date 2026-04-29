import streamlit as st
from modules.common.ui.styles import get_table_style
from modules.common.utils.formatters import format_description
from modules.common.utils.formatters import format_date

from modules.common.utils.formatters import safe_text

def _link(value, type_):
    value = safe_text(value)   # ✅ FIX HERE

    if value == "-":
        return "-"


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

    if not data:
        st.warning("No data available for preview")
        return

    style = get_table_style()

    table1 = f"""
    <table class="tbl">
        <tr>
            <td class="hdr">INCIDENT</td>
            <td>{safe_text(_link(data.get("number"), "incident"))}</td>
            <td class="hdr">CREATED BY</td>
            <td>{_val(data.get("created_by"))}</td>
        </tr>
        <tr>
            <td class="hdr">AZURE BUG</td>
            <td>{safe_text(_link(data.get("azure_bug"), "azure"))}</td>
            <td class="hdr">CREATED DATE</td>
            <td>{_val(format_date(data.get("created_date")))}</td>
        </tr>
        <tr>
            <td class="hdr">PTC CASE</td>
            <td>{safe_text(_link(data.get("ptc_case"), "ptc"))}</td>
            <td class="hdr">ASSIGNED TO</td>
            <td>{_val(data.get("assigned_to"))}</td>
        </tr>
        <tr>
            <td class="hdr">PRIORITY</td>
            <td>{_val(data.get("priority"))}</td>
            <td class="hdr">RESOLVED DATE</td>
            <td>{_val(format_date(data.get("resolved_date")))}</td>
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
            <td>{_val(format_description(data.get("description")))}</td>
        </tr>
    </table>
    """

    # 🔥 IMPORTANT FIX
    html = style + table1 + table2

    st.markdown(html, unsafe_allow_html=True)
    #import streamlit.components.v1 as components
    
    #components.html(
        #html,
        #height=800,
        #scrolling=True
    #)
