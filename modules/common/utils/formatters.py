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
