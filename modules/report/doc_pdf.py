from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO


def generate_pdf(data, root, l2, res, images=None):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Incident: {data.get('number')}", styles["Normal"]))
    elements.append(Paragraph(f"Priority: {data.get('priority')}", styles["Normal"]))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("ROOT CAUSE", styles["Heading2"]))
    elements.append(Paragraph(root or "", styles["Normal"]))

    elements.append(Paragraph("L2 ANALYSIS", styles["Heading2"]))
    elements.append(Paragraph(l2 or "", styles["Normal"]))

    elements.append(Paragraph("RESOLUTION", styles["Heading2"]))
    elements.append(Paragraph(res or "", styles["Normal"]))

    doc.build(elements)

    buffer.seek(0)
    return buffer
