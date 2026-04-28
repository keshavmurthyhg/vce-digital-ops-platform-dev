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

    # 🔴 Remove contact block fully
    text = re.sub(
        r"How does the user want to be contacted.*?(MS Teams|phone number).*?\d+",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 🔴 Remove MS Teams lines
    text = re.sub(r"MS Teams.*", "", text, flags=re.IGNORECASE)

    # 🔴 Remove phone numbers
    text = re.sub(r"\+?\d{10,15}", "", text)

    # 🔴 Clean spacing
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()
