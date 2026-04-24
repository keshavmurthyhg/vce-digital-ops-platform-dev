from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from modules.report.layout.footer import apply_word_footer
from modules.report.utils.links import apply_word_link
from modules.report.utils.utils import format_date, set_cell_bg, format_description
from modules.report.utils.utils import clean_text
import os


def generate_word_doc(data, root, l2, res, images, ppt_data=None):

    doc = Document()
    doc.add_heading("INCIDENT REPORT", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # HEADER TABLE
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(r, c, key, val):
        h = table.rows[r].cells[c]
        v = table.rows[r].cells[c + 1]

        p = h.paragraphs[0]
        run = p.add_run(key.upper())
        run.bold = True
        set_cell_bg(h)

        p = v.paragraphs[0]
        apply_word_link(p, key, val)

    fill(0, 0, "Incident", data.get("number"))
    fill(0, 2, "Created By", data.get("created_by"))
    fill(1, 0, "Azure Bug", data.get("azure_bug"))
    fill(1, 2, "Created Date", format_date(data.get("created_date")))
    fill(2, 0, "PTC Case", data.get("ptc_case"))
    fill(2, 2, "Assigned To", data.get("assigned_to"))
    fill(3, 0, "Priority", data.get("priority"))
    fill(3, 2, "Resolved Date", format_date(data.get("resolved_date")))

    doc.add_paragraph("")

    # DESCRIPTION TABLE
    t2 = doc.add_table(rows=2, cols=2)
    t2.style = "Table Grid"

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]

    for i, text in enumerate(headers):
        p = t2.rows[0].cells[i].paragraphs[0]
        run = p.add_run(text)
        run.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(t2.rows[0].cells[i])
    
    # ✅ CLEAN DESCRIPTION (REMOVES PERSONAL INFO)
    t2.rows[1].cells[0].text = clean_text(data.get("short_description"))
    t2.rows[1].cells[1].text = clean_text(format_description(data.get("description")))
    # BODY
    sections = {
        "PROBLEM STATEMENT & ROOT CAUSE": root,
        "TECHNICAL ANALYSIS": l2,
        "RESOLUTION & RECOMMENDATION": res
    }

    for title, content in sections.items():
        doc.add_heading(title, 1)

        for line in (content or "-").split("\n"):
            if line.strip():
                doc.add_paragraph(clean_text(line.strip("- ").strip()), style="List Bullet")

    # FOOTER
    apply_word_footer(doc, data)

    # ---------------- PPT CONTENT ---------------- #
    if ppt_data:

        doc.add_page_break()

        for slide in ppt_data:

            doc.add_heading(slide["title"], level=1)

            for txt in slide["texts"]:
                doc.add_paragraph(clean_text(txt))

            for img in slide["images"]:
                if os.path.exists(img):
                    try:
                        doc.add_picture(img, width=Inches(5))
                    except Exception:
                        continue

    # SAVE
    from io import BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()
