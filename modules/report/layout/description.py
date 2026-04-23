from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors

def build_pdf_description(data, center_style, clean_text, styles):

    def wrap(x):
        return Paragraph(str(x or ""), styles["Normal"])

    table = Table([
        [
            Paragraph("<b>SHORT DESCRIPTION</b>", center_style),
            Paragraph("<b>DESCRIPTION</b>", center_style)
        ],
        [
            wrap(clean_text(data.get("short_description"))),
            wrap(clean_text(data.get("description")))
        ]
    ], colWidths=[266,266])

    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    return table
