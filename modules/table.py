import streamlit as st

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

    # Create link column
    links = []
    for _, row in df.iterrows():
        link = build_link(row.get("Number", ""), row.get("Source", ""))
        links.append(link if link else "")

    df["Open"] = links

    # Limit description length (no wrap)
    df["Description"] = df["Description"].astype(str).str[:80]

    st.dataframe(df, use_container_width=True)
