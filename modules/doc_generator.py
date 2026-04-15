from docx import Document
from io import BytesIO

def generate_word_doc(data, root_cause, l2_analysis, resolution, closure):
    doc = Document()

    doc.add_heading('INCIDENT REPORT', 0)

    # TABLE
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'

    def add_row(field, value):
        row = table.add_row().cells
        row[0].text = field
        row[1].text = str(value)

    add_row("Incident Number", data.get("number", ""))
    add_row("Short Description", data.get("short_description", ""))
    add_row("Description", data.get("description", ""))
    add_row("Priority", data.get("priority", ""))
    add_row("State", data.get("state", ""))

    # SECTIONS
    doc.add_heading('Issue Description', 1)
    doc.add_paragraph(data.get("description", ""))

    doc.add_heading('Root Cause', 1)
    doc.add_paragraph(root_cause)

    doc.add_heading('L2 Analysis', 1)
    doc.add_paragraph(l2_analysis)

    doc.add_heading('Test Cases / Validation', 1)
    doc.add_paragraph("1.\n2.\n3.")

    doc.add_heading('Resolution', 1)
    doc.add_paragraph(resolution)

    doc.add_heading('Closure Notes', 1)
    doc.add_paragraph(closure)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer
