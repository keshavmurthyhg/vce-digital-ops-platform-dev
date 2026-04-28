from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from modules.common.utils.links import get_url, make_pdf_link

def build_pdf_header(data, wrap_link, format_date):

    def wrap(x):
        return Paragraph(str(x or ""), style=None)

    table = Table([
        [
            "INCIDENT",
            wrap_link("incident", data.get("number")),
            "CREATED BY",
            wrap(data.get("created_by"))
        ],
        [
            "AZURE BUG",
            wrap_link("azure", data.get("azure_bug")),
            "CREATED DATE",
            wrap(format_date(data.get("created_date")))
        ],
        [
            "PTC CASE",
            wrap_link("ptc", data.get("ptc_case")),
            "ASSIGNED TO",
            wrap(data.get("assigned_to"))
        ],
        [
            "PRIORITY",
            wrap(data.get("priority")),
            "RESOLVED DATE",
            wrap(format_date(data.get("resolved_date")))
        ]
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
