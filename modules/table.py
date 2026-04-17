import streamlit as st


def build_link(num, src):
    if src == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{num}"
    return ""


def clean_name(val):
    if not val:
        return ""
    return str(val).split("<")[0].strip()


def truncate_text(text, length=60):
    text = str(text)
    return text[:length] + "..." if len(text) > length else text


def render_table(df):

    html = """
    <style>
    table {width:100%; border-collapse:collapse; font-size:13px;}
    th, td {padding:6px; border:1px solid #ddd; text-align:center; white-space:nowrap;}
    th {background-color:#f5f5f5;}
    td.desc {text-align:left; max-width:350px; overflow:hidden; text-overflow:ellipsis;}
    </style>

    <table>
    <thead>
    <tr>
        <th>SL No</th>
        <th>Number</th>
        <th>Description</th>
        <th>Priority</th>
        <th>Status</th>
        <th>Created By</th>
        <th>Created Date</th>
        <th>Assigned To</th>
        <th>Resolved Date</th>
        <th>Source</th>
        <th>Open</th>
    </tr>
    </thead>
    <tbody>
    """

    for _, row in df.iterrows():

        number = row.get("Number", "")
        source = row.get("Source", "")
        link = build_link(number, source)

        open_link = f'<a href="{link}" target="_blank">Open</a>' if link else "-"

        html += f"""
        <tr>
            <td>{row.get('SL No','')}</td>
            <td>{number}</td>
            <td class="desc">{truncate_text(row.get('Description',''))}</td>
            <td>{row.get('Priority','')}</td>
            <td>{row.get('Status','')}</td>
            <td>{clean_name(row.get('Created By',''))}</td>
            <td>{row.get('Created Date','')}</td>
            <td>{clean_name(row.get('Assigned To',''))}</td>
            <td>{row.get('Resolved Date','')}</td>
            <td>{source}</td>
            <td>{open_link}</td>
        </tr>
        """

    html += "</tbody></table>"

    # ONLY THIS — NO st.write anywhere
    st.markdown(html, unsafe_allow_html=True)
