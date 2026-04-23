# ---------------- URL BUILDERS ---------------- #

def get_snow_url(id):
    return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={id}" if id else None

def get_ptc_url(id):
    return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={id}" if id else None

def get_azure_url(id):
    return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{id}" if id else None


# ---------------- GENERIC ROUTER ---------------- #

def get_url(field, value):
    if not value:
        return None

    field = field.lower()

    if "incident" in field:
        return get_snow_url(value)

    if "ptc" in field:
        return get_ptc_url(value)

    if "azure" in field:
        return get_azure_url(value)

    return None


# ---------------- PDF ---------------- #

def make_pdf_link(text, url, styles):
    from reportlab.platypus import Paragraph

    if not text:
        return Paragraph("", styles["Normal"])

    if url:
        return Paragraph(f'<link href="{url}">{text}</link>', styles["Normal"])

    return Paragraph(str(text), styles["Normal"])


# ---------------- WORD ---------------- #

def apply_word_link(paragraph, field, value):
    from modules.report.utils.utils import add_hyperlink

    url = get_url(field, value)

    if url:
        add_hyperlink(paragraph, url, value)
    else:
        paragraph.text = str(value or "")


# ---------------- STREAMLIT UI ---------------- #

def make_ui_link(field, value):
    if not value:
        return ""

    url = get_url(field, value)

    if url:
        return f"[{value}]({url})"

    return value
