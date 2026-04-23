from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


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
    ],
    colWidths=[120, 180, 120, 180]   # ✅ correct place
    )

    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    return table
