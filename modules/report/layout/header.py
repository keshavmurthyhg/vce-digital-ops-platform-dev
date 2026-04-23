from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from modules.report.utils.links import get_url, make_pdf_link

def wrap_link(field, value, styles):
    url = get_url(field, value)
    return make_pdf_link(value, url, styles)

def build_pdf_header(data, wrap_link, format_date):

    table = Table([
        ["INCIDENT", wrap_link("incident", data.get("number")),
         "CREATED BY", wrap_link(data.get("created_by"))],

        ["AZURE BUG", wrap_link("azure", data.get("azure_bug")),
         "CREATED DATE", wrap_link(format_date(data.get("created_date")))],

        ["PTC CASE", wrap_link("ptc", data.get("ptc_case")),
         "ASSIGNED TO", wrap_link(data.get("assigned_to"))],

        ["PRIORITY", wrap_link(data.get("priority")),
         "RESOLVED DATE", wrap_link(format_date(data.get("resolved_date")))],
    ],
    colWidths=[100, 160, 100, 160]   # ✅ correct place
    )

    table.setStyle(TableStyle([
        # 🔹 GRID
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    
        # 🔹 GREY BACKGROUND (LABEL COLUMNS)
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('BACKGROUND', (2,0), (2,-1), colors.lightgrey),
    
        # 🔹 BOLD LABELS
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
    
        # 🔹 NORMAL TEXT
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
    
        # 🔹 ALIGNMENT
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    return table
