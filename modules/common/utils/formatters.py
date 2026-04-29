import re
from datetime import datetime
from reportlab.lib import colors


# ---------------- DATE ---------------- #
def format_date(val):
    if not val:
        return "-"
    try:
        if isinstance(val, str):
            val = datetime.fromisoformat(val)
        return val.strftime("%d-%b-%Y")
    except Exception:
        return str(val)


# ---------------- WORD TABLE ---------------- #
def set_cell_bg(cell):
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    shading = parse_xml(
        r'<w:shd {} w:fill="D9D9D9"/>'.format(nsdecls('w'))
    )
    cell._tc.get_or_add_tcPr().append(shading)


# ---------------- SAFE TEXT ---------------- #
def safe_text(val):
    if val is None:
        return "-"
    val = str(val).strip()
    if val.lower() in ["nan", "none", ""]:
        return "-"
    return val


# ---------------- CLEAN DESCRIPTION ---------------- #
def format_description(text: str) -> str:
    """
    Clean ServiceNow description:
    - remove contact info
    - remove phone numbers
    - remove MS Teams lines
    """

    if not text:
        return ""

    text = str(text)

    # 🔴 Remove full contact block
    text = re.sub(
        r"How does the user want to be contacted.*?(MS Teams|phone number).*?\d+",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 🔴 Remove MS Teams lines
    text = re.sub(
        r"MS Teams.*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # 🔴 Remove phone numbers
    text = re.sub(
        r"\+?\d[\d\s]{7,}",
        "",
        text
    )

    # 🔴 Normalize spacing
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()
