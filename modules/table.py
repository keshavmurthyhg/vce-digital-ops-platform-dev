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

    df = df.copy()

    # ✅ Clean fields
    df["Created By"] = df["Created By"].apply(clean_name)
    df["Assigned To"] = df["Assigned To"].apply(clean_name)
    df["Description"] = df["Description"].apply(truncate_text)

    # ✅ Create link column
    df["Open"] = df.apply(
        lambda row: build_link(row["Number"], row["Source"]),
        axis=1
    )

    # ✅ Show table safely
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Open": st.column_config.LinkColumn("Open", display_text="Open")
        }
    )
