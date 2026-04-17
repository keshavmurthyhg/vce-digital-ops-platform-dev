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
import streamlit as st
import pandas as pd


def build_link(num, src):
    if src == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{num}"
    return ""


def render_table(df):

    df = df.copy()

    # ✅ Create clickable link column
    df["Open"] = df.apply(
        lambda row: f"[Open]({build_link(row['Number'], row['Source'])})"
        if build_link(row["Number"], row["Source"]) else "-",
        axis=1
    )

    # ✅ Truncate description (no wrap)
    df["Description"] = df["Description"].astype(str).str.slice(0, 80) + "..."

    # ✅ Display table
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Open": st.column_config.LinkColumn("Open")
        }
    )
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
