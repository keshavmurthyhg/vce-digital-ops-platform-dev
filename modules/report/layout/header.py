from reportlab.platypus import Table, TableStyle, Paragraph
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
    ], colWidths=[100,166,100,166])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
    ]))

    return table
