import streamlit as st

# ================= LINK BUILDER =================
def build_link(num, src):
    if src == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{num}"
    return ""


# ================= TABLE RENDER =================
def render_table(df):

    html = """
    <table style="width:100%; border-collapse: collapse;">
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

        # ✅ SAFE LINK (NO MULTILINE ERROR)
        if link:
            open_link = (
                f'<span onclick="window.open(\'{link}\', \'_blank\')" '
                f'style="color:#1f77b4; cursor:pointer; text-decoration:underline;">'
                f'🔗 Open</span>'
            )
        else:
            open_link = "-"

        html += f"""
        <tr>
            <td>{row.get('SL No','')}</td>
            <td>{number}</td>
            <td style="text-align:left; max-width:350px; overflow:hidden; text-overflow:ellipsis;">
                {row.get('Description','')}
            </td>
            <td>{row.get('Priority','')}</td>
            <td>{row.get('Status','')}</td>
            <td>{row.get('Created By','')}</td>
            <td>{row.get('Created Date','')}</td>
            <td>{row.get('Assigned To','')}</td>
            <td>{row.get('Resolved Date','')}</td>
            <td>{source}</td>
            <td>{open_link}</td>
        </tr>
        """

    html += "</tbody></table>"

    st.markdown(html, unsafe_allow_html=True)
