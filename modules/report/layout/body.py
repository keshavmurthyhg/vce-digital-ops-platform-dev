from reportlab.platypus import Paragraph, Spacer

def build_sections(elements, root, l2, res, styles, bullet_style, add_images_pdf, images):

    def add_bullets(text):
        for line in (text or "-").split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("-"):
                line = line[1:].strip()

            elements.append(Paragraph(f"• {line}", bullet_style))

    def section(title, content, imgs):
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Spacer(1,6))
        add_bullets(content)
        elements.append(Spacer(1,10))
        add_images_pdf(elements, imgs)

    section("PROBLEM STATEMENT & ROOT CAUSE", root, images.get("root"))
    section("TECHNICAL ANALYSIS", l2, images.get("l2"))
    section("RESOLUTION & RECOMMENDATION", res, images.get("res"))
