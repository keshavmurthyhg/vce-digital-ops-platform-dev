import re

from datetime import datetime
from reportlab.lib import colors

def format_date(val):
    if not val:
        return "-"
    try:
        return datetime.strftime(val, "%d-%b-%Y")
    except:
        return str(val)


def set_cell_bg(cell):
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    shading = parse_xml(r'<w:shd {} w:fill="D9D9D9"/>'.format(nsdecls('w')))
    cell._tc.get_or_add_tcPr().append(shading)

def safe_text(val):
    if val is None:
        return "-"
    return str(val)

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = str(text)

    # 🔴 Remove contact / phone / MS Teams lines
    text = re.sub(
        r"How does the user.*?phone number:.*?\d+",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    text = re.sub(
        r"MS Teams.*?\d+",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"phone number\s*:\s*\+?\d+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # 🔴 Remove standalone phone numbers
    text = re.sub(r"\+?\d{10,15}", "", text)

    # 🔴 Remove extra spaces / newlines
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()
