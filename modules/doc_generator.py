from docx import Document
from io import BytesIO


def generate_word_doc(data, root_cause, l2_analysis, resolution, closure):

    doc = Document()

    doc.add_heading('INCIDENT REPORT', 0)

    # ================= TABLE 1 (LINKS) =================
    table1 = doc.add_table(rows=2, cols=3)
    table1.style = 'Table Grid'

    headers = ["Incident", "Azure Bug", "PTC Case"]
    values = [
        data.get("number", ""),
        data.get("azure_bug", ""),
        data.get("ptc_case", "")
    ]

    for i in range(3):
        table1.rows[0].cells[i].text = headers[i]
        table1.rows[1].cells[i].text = str(values[i])

    # ================= TABLE 2 (DETAILS) =================
    table2 = doc.add_table(rows=2, cols=5)
    table2.style = 'Table Grid'

    headers2 = ["Priority", "Created By", "Created Date", "Assigned To", "Resolved Date"]
    values2 = [
        str(data.get("priority", "")),
        str(data.get("created_by", "")),
        str(data.get("created_date", "")),
        str(data.get("assigned_to", "")),
        str(data.get("resolved_date", ""))
    ]

    for i in range(5):
        table2.rows[0].cells[i].text = headers2[i]
        table2.rows[1].cells[i].text = values2[i]

    # ================= TABLE 3 (DESCRIPTION) =================
    table3 = doc.add_table(rows=2, cols=2)
    table3.style = 'Table Grid'

    table3.rows[0].cells[0].text = "Short Description"
    table3.rows[0].cells[1].text = "Description"

    table3.rows[1].cells[0].text = data.get("short_description", "")
    table3.rows[1].cells[1].text = data.get("description", "")

    # ================= TEXT SECTIONS =================
    doc.add_heading('Root Cause', 1)
    doc.add_paragraph(root_cause)

    doc.add_heading('L2 Analysis', 1)
    doc.add_paragraph(l2_analysis)

    doc.add_heading('Resolution', 1)
    doc.add_paragraph(resolution)

    doc.add_heading('Closure Notes', 1)
    doc.add_paragraph(closure)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer
