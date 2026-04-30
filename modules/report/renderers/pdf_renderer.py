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


# ================= SAFE HEADER VALUE ================= #
def clean_header_value(val):
    if not val:
        return ""

    val = str(val)

    # Escape problematic characters (CRITICAL)
    val = val.replace("&", "&amp;")
    val = val.replace("<", "&lt;")
    val = val.replace(">", "&gt;")

    # Prevent very long values
    return val[:200]


# ================= SAFE BODY TEXT ================= #
def sanitize_text(val):
    if not val:
        return ""

    val = str(val)

    # Escape HTML-breaking chars
    val = val.replace("&", "&amp;")
    val = val.replace("<", "&lt;")
    val = val.replace(">", "&gt;")

    # Break very long lines (prevents LayoutError)
    MAX_LEN = 800
    safe_lines = []

    for line in val.split("\n"):
        if len(line) > MAX_LEN:
            chunks = [line[i:i+MAX_LEN] for i in range(0, len(line), MAX_LEN)]
            safe_lines.extend(chunks)
        else:
            safe_lines.append(line)

    return "\n".join(safe_lines)


# ================= MAIN PDF GENERATOR ================= #
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

    # ================= HEADER ================= #
    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    try:
        header = build_pdf_header(
            data,
            lambda field, value: make_pdf_link(
                clean_header_value(value),   # ✅ FIXED
                get_url(field, value),
                styles
            ),
            format_date
        )

        elements.append(header)

    except Exception as e:
        # 🔴 Fail-safe (never crash PDF)
        elements.append(Paragraph("Header could not be rendered", styles["Normal"]))
        print("Header error:", e)

    elements.append(Spacer(1, 15))

    # ================= DESCRIPTION ================= #
    try:
        desc = build_pdf_description(data, center_style, styles)
        elements.append(desc)
    except Exception as e:
        elements.append(Paragraph("Description error", styles["Normal"]))
        print("Description error:", e)

    elements.append(Spacer(1, 20))

    # ================= SANITIZE BODY ================= #
    root = sanitize_text(root)
    l2 = sanitize_text(l2)
    res = sanitize_text(res)

    # ================= BODY ================= #
    try:
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
    except Exception as e:
        elements.append(Paragraph("Body content could not be rendered", styles["Normal"]))
        print("Body error:", e)

    # ================= FOOTER ================= #
    footer = pdf_footer(data)

    try:
        doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    except Exception as e:
        print("PDF build error:", e)
        raise e  # still raise so you can debug if needed

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
