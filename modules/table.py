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

    for i, row in df.iterrows():

        number = row.get("Number", "")
        source = row.get("Source", "")

        link = build_link(number, source)

        # ✅ CRITICAL FIX (NEW TAB)
        if link:
    open_link = (
        f'<span onclick="window.open(\'{link}\', \'_blank\')" '
        f'style="color:#1f77b4; cursor:pointer; text-decoration:underline;">'
        f'🔗 Open</span>'
    )
else:
    open_link = "-"
        <tr>
            <td style="text-align:center;">{i+1}</td>
            <td style="text-align:center;">{number}</td>

            <td style="text-align:left; max-width:350px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                {row.get('Description','')}
            </td>

            <td style="text-align:center;">{row.get('Priority','')}</td>
            <td style="text-align:center;">{row.get('Status','')}</td>
            <td style="text-align:center;">{row.get('Created By','')}</td>
            <td style="text-align:center;">{row.get('Created Date','')}</td>
            <td style="text-align:center;">{row.get('Assigned To','')}</td>
            <td style="text-align:center;">{row.get('Resolved Date','')}</td>
            <td style="text-align:center;">{source}</td>

            <td style="text-align:center;">{open_link}</td>
        </tr>
        """

    html += "</tbody></table>"

    st.markdown(html, unsafe_allow_html=True)
