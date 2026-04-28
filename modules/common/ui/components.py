import streamlit as st

from modules.common.ui.styles import TABLE_STYLE, CELL_STYLE, HEADER_CELL_STYLE
from modules.common.utils.links import make_ui_link
from modules.common.utils.text_cleaner import format_description
from modules.common.utils.formatters import safe_text


def render_preview_table(data):

    html = f"""
    <table style="{TABLE_STYLE}">
        <tr>
            <td style="{HEADER_CELL_STYLE}">INCIDENT</td>
            <td style="{CELL_STYLE}">{make_ui_link("incident", data.get("number"))}</td>
            <td style="{HEADER_CELL_STYLE}">CREATED BY</td>
            <td style="{CELL_STYLE}">{safe_text(data.get("created_by"))}</td>
        </tr>
        <tr>
            <td style="{HEADER_CELL_STYLE}">AZURE</td>
            <td style="{CELL_STYLE}">{make_ui_link("azure", data.get("azure_bug"))}</td>
            <td style="{HEADER_CELL_STYLE}">DATE</td>
            <td style="{CELL_STYLE}">{safe_text(data.get("created_date"))}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_description_table(data):

    desc = format_description(data.get("description"))

    html = f"""
    <table style="{TABLE_STYLE}">
        <tr>
            <td style="{HEADER_CELL_STYLE}">SHORT DESCRIPTION</td>
            <td style="{HEADER_CELL_STYLE}">DESCRIPTION</td>
        </tr>
        <tr>
            <td style="{CELL_STYLE}">{safe_text(data.get("short_description"))}</td>
            <td style="{CELL_STYLE}">{safe_text(desc)}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)
