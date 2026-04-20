from docx import Document
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from io import BytesIO
import re


# ================= SAFE TEXT =================
def safe_text(text):
    if text is None:
        return ""
    text = str(text)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", "", text)
    return text.strip()


# ================= SHADE CELL =================
def shade_cell(cell, color="D9D9D9"):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    cell._element.get_or_add_tcPr().append(shading)


# ================= FOOTER =================
def add_footer(doc, data):
    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.text = f"{safe_text(data.get('number'))}    |    {safe_text(data.get('priority'))}"


# ================= WORD DOC =================
def generate_word_doc(data, root, l2, res):

    doc = Document()

    # ===== TITLE =====
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.runs[0]
    run.bold = True
    run.font.color.rgb = RGBColor(31, 78, 121)

    # ===== TABLE 1 =====
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(row, col, key, value):
        h = table.rows[row].cells[col]
        v = table.rows[row].cells[col + 1]

        h.text = safe_text(key.upper())
        shade_cell(h)

        for r in h.paragraphs[0].runs:
            r.bold = True

        v.text = safe_text(value)

    fill(0, 0, "Incident", data.get("number"))
    fill(0, 2, "Created By", data.get("created_by"))

    fill(1, 0, "Azure Bug", data.get("azure_bug"))
    fill(1, 2, "Created Date", data.get("created_date"))

    fill(2, 0, "PTC Case", data.get("ptc_case"))
    fill(2, 2, "Assigned To", data.get("assigned_to"))

    fill(3, 0, "Priority", data.get("priority"))
    fill(3, 2, "Resolved Date", data.get("resolved_date"))

    doc.add_paragraph("")

    # ===== DESCRIPTION TABLE =====
    desc_table = doc.add_table(rows=2, cols=2)
    desc_table.style = "Table Grid"

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]

    for i in range(2):
        cell = desc_table.rows[0].cells[i]
        cell.text = headers[i]
        shade_cell(cell)

        for r in cell.paragraphs[0].runs:
            r.bold = True

    desc_table.rows[1].cells[0].text = safe_text(data.get("short_description"))
    desc_table.rows[1].cells[1].text = safe_text(data.get("description"))

    # ===== TEXT =====
    doc.add_heading("ROOT CAUSE", 1)
    doc.add_paragraph(safe_text(root))

    doc.add_heading("L2 ANALYSIS", 1)
    doc.add_paragraph(safe_text(l2))

    doc.add_heading("RESOLUTION", 1)
    doc.add_paragraph(safe_text(res))

    # ===== FOOTER =====
    add_footer(doc, data)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer
