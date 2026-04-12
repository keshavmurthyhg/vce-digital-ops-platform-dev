import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")  # change if needed
    return df

df = load_data()

# -------------------------------
# BUILD LINK
# -------------------------------
def build_link(row):
    num = str(row.get("Number", ""))
    src = row.get("Source", "")

    if src == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        return f"https://dev.azure.com/.../{num}"
    return ""

df["Open"] = df.apply(lambda x: f'<a href="{build_link(x)}" target="_blank">Open</a>', axis=1)

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("Menu")
st.sidebar.selectbox("Search Tool", ["Search Tool"])

sources = st.sidebar.multiselect(
    "Source",
    ["AZURE", "SNOW", "PTC"],
    default=["AZURE", "SNOW", "PTC"]
)

status = st.sidebar.selectbox("Status", ["ALL"] + sorted(df["Status"].dropna().unique()))
priority = st.sidebar.selectbox("Priority", ["ALL"] + sorted(df["Priority"].dropna().unique()))

# -------------------------------
# SEARCH + CLEAR
# -------------------------------
if "search_box" not in st.session_state:
    st.session_state.search_box = ""

col1, col2 = st.columns([20, 1])

with col1:
    search = st.text_input(
        "🔎 Search",
        key="search_box",
        placeholder="Type keyword..."
    )

with col2:
    if st.button("❌"):
        st.session_state.search_box = ""
        st.rerun()

# -------------------------------
# FILTERING
# -------------------------------
filtered = df.copy()

if sources:
    filtered = filtered[filtered["Source"].isin(sources)]

if status != "ALL":
    filtered = filtered[filtered["Status"] == status]

if priority != "ALL":
    filtered = filtered[filtered["Priority"] == priority]

if search:
    filtered = filtered[
        filtered.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    ]

# -------------------------------
# COUNTS
# -------------------------------
total = len(filtered)
azure_count = len(filtered[filtered["Source"] == "AZURE"])
snow_count = len(filtered[filtered["Source"] == "SNOW"])
ptc_count = len(filtered[filtered["Source"] == "PTC"])

# -------------------------------
# PAGINATION
# -------------------------------
page_size = 10
if "page" not in st.session_state:
    st.session_state.page = 1

total_pages = max(1, (total - 1) // page_size + 1)

start = (st.session_state.page - 1) * page_size
end = start + page_size
page_df = filtered.iloc[start:end]

# -------------------------------
# HEADER ROW (RESULT + DOWNLOAD + PAGINATION)
# -------------------------------
col1, col2, col3 = st.columns([4, 2, 3])

with col1:
    st.markdown(
        f"<h5 style='margin-bottom:0;'>Results: {total}</h5>",
        unsafe_allow_html=True
    )
    st.caption(f"AZURE: {azure_count} | SNOW: {snow_count} | PTC: {ptc_count}")

with col2:
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.download_button(
        "📥 Download Excel",
        data=filtered.to_csv(index=False),
        file_name="ops_data.csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    col_prev, col_page, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("◀") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()

    with col_page:
        st.markdown(f"<div style='text-align:center;'>Page {st.session_state.page}/{total_pages}</div>", unsafe_allow_html=True)

    with col_next:
        if st.button("▶") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()

# -------------------------------
# TABLE STYLING
# -------------------------------
def style_table(df):
    return df.style.set_table_styles([
        {"selector": "th", "props": [("text-align", "center"), ("font-size", "12px")]},
        {"selector": "td", "props": [("font-size", "12px")]},
    ]).set_properties(subset=["Description"], **{
        "width": "400px",
        "white-space": "nowrap",
        "overflow": "hidden",
        "text-overflow": "ellipsis"
    })

# Auto fit other columns
st.markdown("""
<style>
td {
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# DISPLAY TABLE
# -------------------------------
st.write(style_table(page_df).to_html(escape=False), unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.caption("Last refreshed: Just now")
