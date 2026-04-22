from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO


def generate_pdf(data, root, l2, res, images=None, full_df=None):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Incident: {data.get('number')}", styles["Normal"]))
    elements.append(Paragraph(f"Priority: {data.get('priority')}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    for title, content, img_key in [
        ("ROOT CAUSE", root, "root"),
        ("L2 ANALYSIS", l2, "l2"),
        ("RESOLUTION", res, "res"),
    ]:
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Paragraph(content or "", styles["Normal"]))

        if images and images.get(img_key):
            elements.append(Image(images[img_key], width=400, height=200))

        elements.append(Spacer(1, 10))

    doc.build(elements)

    buffer.seek(0)
    return buffer
