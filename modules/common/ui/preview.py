import streamlit as st
from modules.common.utils.formatters import format_date


def safe(val):
    return val if val not in [None, "", "None"] else "-"


def render_preview(data):

    st.subheader("Preview")

    html = f"""
    <style>
        .report-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 14px;
        }}
        .report-table td {{
            border: 1px solid black;
            padding: 6px;
        }}
        .report-header {{
            font-weight: bold;
            background-color: #f2f2f2;
        }}
    </style>

    <table class="report-table">
        <tr>
            <td class="report-header">INCIDENT</td>
            <td>{safe(data.get("number"))}</td>
            <td class="report-header">CREATED BY</td>
            <td>{safe(data.get("opened_by"))}</td>
        </tr>
        <tr>
            <td class="report-header">AZURE BUG</td>
            <td>{safe(data.get("azure_bug"))}</td>
            <td class="report-header">CREATED DATE</td>
            <td>{format_date(data.get("created"))}</td>
        </tr>
        <tr>
            <td class="report-header">PTC CASE</td>
            <td>{safe(data.get("ptc_case"))}</td>
            <td class="report-header">ASSIGNED TO</td>
            <td>{safe(data.get("assigned_to"))}</td>
        </tr>
        <tr>
            <td class="report-header">PRIORITY</td>
            <td>{safe(data.get("priority"))}</td>
            <td class="report-header">RESOLVED DATE</td>
            <td>{format_date(data.get("resolved"))}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)

    desc_html = f"""
    <table class="report-table">
        <tr>
            <td class="report-header">SHORT DESCRIPTION</td>
            <td class="report-header">DESCRIPTION</td>
        </tr>
        <tr>
            <td>{safe(data.get("short_description"))}</td>
            <td>{safe(data.get("description"))}</td>
        </tr>
    </table>
    """

    st.markdown(desc_html, unsafe_allow_html=True)
