from modules.common.utils.links import extract_azure_id
from modules.report.doc_generator import (
    generate_pdf,
    generate_word_doc_wrapper
)

# ✅ USE NEW RCA ENGINE
from modules.report.services.rca_service import build_rca


def safe_text(val):
    if val is None:
        return ""

    if isinstance(val, list):
        val = "\n".join([str(v) for v in val])

    val = str(val)

    MAX_LEN = 800
    lines = []

    for raw in val.split("\n"):
        if len(raw) > MAX_LEN:
            chunks = [
                raw[i:i + MAX_LEN]
                for i in range(0, len(raw), MAX_LEN)
            ]
            lines.extend(chunks)
        else:
            lines.append(raw)

    return "\n".join(lines)


# -----------------------------------
# BUILD BULK REPORTS
# -----------------------------------
def build_bulk_reports(
    df,
    incident_list,
    images_map=None
):
    results = []

    for inc in incident_list:

        row = df[df["number"] == inc]

        if row.empty:
            continue

        r = row.iloc[0]
        
        # Build notes FIRST
        combined_notes = " ".join([
            str(r.get("work notes", "")),
            str(r.get("additional comments", "")),
            str(r.get("resolution notes", ""))
        ])
        
        data = {
        
            "azure_bug": extract_azure_id(combined_notes),
            
            "ptc_case": r.get(
                "vendor ticket"
            ),

            # -----------------------------
            # CRITICAL FIX
            # -----------------------------
            "work notes": r.get(
                "work notes", ""
            ),

            "additional comments": r.get(
                "additional comments", ""
            ),

            "resolution notes": r.get(
                "resolution notes", ""
            ),

            # optional underscore versions
            "work_notes": r.get(
                "work notes", ""
            ),

            "additional_comments": r.get(
                "additional comments", ""
            ),

            "resolution_notes": r.get(
                "resolution notes", ""
            )
        }

        # ✅ NEW RCA LOGIC
        rca = build_rca(data)

        images = (
            images_map.get(inc, {})
            if images_map
            else {}
        )

        results.append({
            "data": data,

            "root": safe_text(
                rca.get(
                    "problem_statement",
                    ""
                )
            ),

            "l2": safe_text(
                rca.get(
                    "root_cause",
                    ""
                )
            ),

            "res": safe_text(
                rca.get(
                    "resolution",
                    ""
                )
            ),

            "images": images
        })

    return results


# -----------------------------------
# GENERATE ZIP
# -----------------------------------
def generate_bulk_zip(reports):
    import zipfile
    from io import BytesIO

    zip_buffer = BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w"
    ) as z:

        for r in reports:
            number = r["data"]["number"]

            try:
                pdf_bytes = generate_pdf(**r)
                word_bytes = generate_word_doc_wrapper(**r)

                z.writestr(
                    f"{number}.pdf",
                    pdf_bytes
                )

                z.writestr(
                    f"{number}.docx",
                    word_bytes
                )

            except Exception as e:
                print(
                    f"Failed bulk report for {number}: {e}"
                )
                continue

    zip_buffer.seek(0)
    return zip_buffer
