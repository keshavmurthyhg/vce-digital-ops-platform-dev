import streamlit as st
from modules.common.utils.formatters import format_date
from modules.common.utils.links import make_ui_link


def render_preview(data):

    st.subheader("Preview")

    # ---------- TABLE 1 (FULL INCIDENT DETAILS) ----------
    html = f"""
    <style>
        .report-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 14px;
        }}
        .report-table td, .report-table th {{
            border: 1px solid #000;
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
            <td>{make_ui_link(data.get("number"))}</td>
            <td class="report-header">CREATED BY</td>
            <td>{data.get("opened_by","-")}</td>
        </tr>
        <tr>
            <td class="report-header">AZURE BUG</td>
            <td>{make_ui_link(data.get("azure_bug"))}</td>
            <td class="report-header">CREATED DATE</td>
            <td>{format_date(data.get("created"))}</td>
        </tr>
        <tr>
            <td class="report-header">PTC CASE</td>
            <td>{make_ui_link(data.get("ptc_case"))}</td>
            <td class="report-header">ASSIGNED TO</td>
            <td>{data.get("assigned_to","-")}</td>
        </tr>
        <tr>
            <td class="report-header">PRIORITY</td>
            <td>{data.get("priority","-")}</td>
            <td class="report-header">RESOLVED DATE</td>
            <td>{format_date(data.get("resolved"))}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)

    # ---------- TABLE 2 ----------
    desc_html = f"""
    <table class="report-table">
        <tr>
            <td class="report-header">SHORT DESCRIPTION</td>
            <td class="report-header">DESCRIPTION</td>
        </tr>
        <tr>
            <td>{data.get("short_description","-")}</td>
            <td>{data.get("description","-")}</td>
        </tr>
    </table>
    """

    st.markdown(desc_html, unsafe_allow_html=True)
