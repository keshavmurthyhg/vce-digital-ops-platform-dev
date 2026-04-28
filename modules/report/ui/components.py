from modules.report.ui.styles import TABLE_STYLE, CELL_STYLE
from modules.report.utils.utils import format_description

def render_preview_table(data):
    def val(x): return x if x else "-"

    html = f"""
    <table style="{TABLE_STYLE}">
        <tr>
            <td style="{CELL_STYLE}"><b>INCIDENT</b></td>
            <td style="{CELL_STYLE}">{val(data.get("number"))}</td>
        </tr>
    </table>
    """
    return html
