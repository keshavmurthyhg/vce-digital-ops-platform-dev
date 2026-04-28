from modules.report.doc_generator import generate_pdf, generate_word_doc_wrapper
from modules.report.utils.rca_generator import generate_rca


def build_bulk_reports(df, incident_list, images_map=None):
    results = []

    for inc in incident_list:
        row = df[df["number"] == inc]

        if row.empty:
            continue

        r = row.iloc[0]

        data = {
            "number": r.get("number"),
            "short_description": r.get("short description"),
            "description": r.get("description"),
            "priority": r.get("priority"),
            "created_by": r.get("caller"),
            "created_date": str(r.get("created")).split()[0],
            "assigned_to": r.get("assigned to"),
            "resolved_date": str(r.get("resolved")).split()[0],
            "work_notes": r.get("work notes", ""),
            "comments": r.get("additional comments", ""),
            "resolution": r.get("resolution notes", ""),
            "azure_bug": r.get("azure bug"),
            "ptc_case": r.get("vendor ticket"),
        }

        rca = generate_rca(data)

        report = {
            "data": data,
            "problem": rca["problem"],
            "analysis": rca["analysis"],
            "resolution": rca["resolution"]
        }

        images = images_map.get(inc, {}) if images_map else {}

        results.append({
            "data": data,
            "root": root,
            "l2": l2,
            "res": res,
            "images": images
        })

    return results


def generate_bulk_zip(reports):
    import zipfile
    from io import BytesIO

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:
        for r in reports:
            number = r["data"]["number"]

            pdf_bytes = generate_pdf(**r)
            word_bytes = generate_word_doc_wrapper(**r)

            z.writestr(f"{number}.pdf", pdf_bytes)
            z.writestr(f"{number}.docx", word_bytes)

    zip_buffer.seek(0)
    return zip_buffer
