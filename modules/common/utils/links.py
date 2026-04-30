import re

def extract_azure_id(text):
    if not text:
        return None

    match = re.search(r'/edit/(\d+)', text)
    if match:
        return match.group(1)

    match = re.search(r'\b\d{6,}\b', text)
    return match.group(0) if match else None


def get_url(field, value):
    if not value or value == "-":
        return None

    value = str(value).strip()

    field = field.lower()

    if field == "incident":
        return (
            "https://volvoitsm.service-now.com/"
            f"nav_to.do?uri=incident.do?sysparm_query=number={value}"
        )

    elif field == "azure bug":
        return (
            "https://dev.azure.com/VolvoGroup-DVP/"
            f"VCEWindchillPLM/_workitems/edit/{value}"
        )

    elif field == "ptc case":
        return (
            "https://support.ptc.com/"
            f"appserver/cs/view/case.jsp?n={value}"
        )

    return None


def make_pdf_link(value, url, styles):
    from reportlab.platypus import Paragraph
    if not value or not url:
        return Paragraph("-", styles["Normal"])

    return Paragraph(f'<link href="{url}">{value}</link>', styles["Normal"])


def apply_word_link(paragraph, key, value):
    from docx.shared import RGBColor

    url = get_url(key.lower(), value)
    run = paragraph.add_run(str(value or "-"))

    if url:
        run.font.color.rgb = RGBColor(0, 0, 255)

def make_ui_link(type_, value):
    url = get_url(type_, value)
    if not value:
        return "-"
    if not url:
        return str(value)
    return f'<a href="{url}" target="_blank">{value}</a>'
