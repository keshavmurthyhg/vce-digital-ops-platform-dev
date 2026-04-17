from docx import Document
from io import BytesIO

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT


# ================= HYPERLINK =================
def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    new_run = OxmlElement('w:r')
    new_run.text = text

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


# ================= DOC =================
def generate_word_doc(data, root_cause, l2_analysis, resolution, closure):

    doc = Document()

    doc.add_heading('INCIDENT REPORT', 0)

    # ================= TABLE 1 =================
    table1 = doc.add_table(rows=2, cols=3)
    table1.style = 'Table Grid'

    headers = ["Incident", "Azure Bug", "PTC Case"]

    for i in range(3):
        table1.rows[0].cells[i].text = headers[i]

    # Hyperlinks
    add_hyperlink(
        table1.rows[1].cells[0].paragraphs[0],
        f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}",
        str(data.get("number", ""))
    )

    add_hyperlink(
        table1.rows[1].cells[1].paragraphs[0],
        f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}",
        str(data.get("azure_bug", ""))
    )

    add_hyperlink(
        table1.rows[1].cells[2].paragraphs[0],
        f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}",
        str(data.get("ptc_case", ""))
    )

    # ================= TABLE 2 =================
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

    # ================= TABLE 3 =================
    table3 = doc.add_table(rows=2, cols=2)
    table3.style = 'Table Grid'

    table3.rows[0].cells[0].text = "Short Description"
    table3.rows[0].cells[1].text = "Description"

    table3.rows[1].cells[0].text = data.get("short_description", "")
    table3.rows[1].cells[1].text = data.get("description", "")

    # ================= TEXT =================
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
