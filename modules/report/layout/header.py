from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.platypus import Table

table = Table(
    data,
    colWidths=[120, 180, 120, 180]   # 👈 ADD THIS
)


def build_pdf_header(data, wrap_link, format_date):
    table = Table([
        ["INCIDENT", wrap_link(data.get("number")),
         "CREATED BY", wrap_link(data.get("created_by"))],

        ["AZURE BUG", wrap_link(data.get("azure_bug")),
         "CREATED DATE", wrap_link(format_date(data.get("created_date")))],

        ["PTC CASE", wrap_link(data.get("ptc_case")),
         "ASSIGNED TO", wrap_link(data.get("assigned_to"))],

        ["PRIORITY", wrap_link(data.get("priority")),
         "RESOLVED DATE", wrap_link(format_date(data.get("resolved_date")))],
    ], colWidths=[100,166,100,166])

    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),   # header bold
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    return table
