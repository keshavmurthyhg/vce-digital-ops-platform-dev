from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from io import BytesIO

from modules.report.layout.header import build_pdf_header
from modules.report.layout.description import build_pdf_description
from modules.report.layout.body import build_sections
from modules.report.layout.styles import get_pdf_styles
from modules.report.layout.footer import pdf_footer

from modules.common.utils.links import get_url, make_pdf_link
from modules.common.utils.formatters import format_date
from modules.common.utils.text_cleaner import add_images_pdf


def generate_pdf_doc(data, root, l2, res, images):

    styles, center_style, bullet_style = get_pdf_styles()

    buffer = BytesIO()
    elements = []

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=50
    )
    print("PDF DATA AZURE:", data.get("azure_bug"))
    # ================= HEADER ================= #
    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    header = build_pdf_header(
        data,
        lambda field, value: make_pdf_link(value, get_url(field, value), styles),
        format_date
    )

    elements.append(header)
    elements.append(Spacer(1, 15))

    # ================= DESCRIPTION ================= #
    desc = build_pdf_description(data, center_style, styles)
    elements.append(desc)
    elements.append(Spacer(1, 20))

    # ================= BODY ================= #
    build_sections(
        elements,
        root,
        l2,
        res,
        styles,
        bullet_style,
        add_images_pdf,
        images
    )

    # ================= FOOTER ================= #
    footer = pdf_footer(data)

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
