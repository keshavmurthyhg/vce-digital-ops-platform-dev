from modules.report.doc_generator import generate_pdf, generate_word_doc_wrapper
from modules.report.domain.rca_generator import generate_rca


# ✅ SAFE TEXT HANDLER (CRITICAL)
def safe_text(val):
    if val is None:
        return ""

    if isinstance(val, list):
        val = "\n".join([str(v) for v in val])
    else:
        val = str(val)

    # 🔴 Prevent ReportLab crash (very long lines)
    MAX_LEN = 800
    lines = []

    for raw in val.split("\n"):
        if len(raw) > MAX_LEN:
            chunks = [raw[i:i+MAX_LEN] for i in range(0, len(raw), MAX_LEN)]
            lines.extend(chunks)
        else:
            lines.append(raw)

    return "\n".join(lines)


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

        # 🔴 RCA
        rca = generate_rca(data)

        images = images_map.get(inc, {}) if images_map else {}

        results.append({
            "data": data,
            "root": safe_text(rca.get("problem")),
            "l2": safe_text(rca.get("analysis")),
            "res": safe_text(rca.get("resolution")),
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

            try:
                # ✅ SAFE GENERATION (DON’T BREAK WHOLE ZIP)
                pdf_bytes = generate_pdf(**r)
                word_bytes = generate_word_doc_wrapper(**r)

                z.writestr(f"{number}.pdf", pdf_bytes)
                z.writestr(f"{number}.docx", word_bytes)

            except Exception as e:
                # 🔴 VERY IMPORTANT: skip bad incidents
                print(f"❌ Failed for {number}: {e}")
                continue

    zip_buffer.seek(0)
    return zip_buffer
