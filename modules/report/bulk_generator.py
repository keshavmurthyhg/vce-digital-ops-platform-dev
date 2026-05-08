from io import BytesIO, StringIO
import zipfile
import csv
from datetime import datetime
import streamlit as st

from modules.common.utils.links import extract_azure_id
from modules.report.doc_generator import (
    generate_pdf,
    generate_word_doc_wrapper,
    get_download_filename
)
from modules.report.services.rca_service import build_rca


def safe_text(val):
    if val is None:
        return ""

    if isinstance(val, list):
        val = "\n".join([str(v) for v in val])

    val = str(val).strip()

    if val.lower() in ["nan", "none", "nat"]:
        return ""

    return val


# ---------------- BUILD REPORTS ---------------- #
def build_bulk_reports(df, incident_list, images_map=None):
    results = []

    for inc in incident_list:
        try:
            row = df[df["number"] == inc]

            if row.empty:
                continue

            r = row.iloc[0]

            resolution_notes = str(r.get("resolution notes", ""))
            azure_bug = extract_azure_id(resolution_notes)

            data = {
                "number": r.get("number"),
                "short_description": r.get("short description"),
                "description": r.get("description"),
                "priority": r.get("priority"),
                "created_by": r.get("opened by"),
                "created_date": r.get("created"),
                "assigned_to": r.get("assigned to"),
                "resolved_date": r.get("resolved"),
                "azure_bug": azure_bug,
                "ptc_case": r.get("vendor ticket"),
                "work notes": r.get("work notes", ""),
                "additional comments": r.get("additional comments", ""),
                "resolution notes": r.get("resolution notes", "")
            }

            rca = build_rca(data)

            images = images_map.get(inc, {}) if images_map else {}

            results.append({
                "data": data,
                "root": safe_text(rca.get("problem_statement")),
                "l2": safe_text(rca.get("root_cause")),
                "res": safe_text(rca.get("resolution")),
                "images": images
            })

        except Exception:
            continue

    return results


# ---------------- BULK ZIP ---------------- #
def generate_bulk_zip(
    reports,
    file_type="both",      # pdf / word / both
    group_by="priority"    # priority / date / none
):
    zip_buffer = BytesIO()
    failed_reports = []

    total = len(reports)
    progress = st.progress(0)
    status = st.empty()

    current_date = datetime.now().strftime("%d%b%Y")

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:

        for i, report in enumerate(reports, start=1):
            try:
                data = report["data"]
                number = str(data.get("number", "unknown")).strip().replace(" ", "_")

                pdf_name = get_download_filename(data, "pdf")
                word_name = get_download_filename(data, "docx")

                # -------- GROUPING -------- #
                if group_by == "priority":
                    priority = str(data.get("priority", "unknown")).strip()
                    folder = f"{priority}/{number}/"
                elif group_by == "date":
                    folder = f"{current_date}/{number}/"
                else:
                    folder = f"{number}/"

                # -------- GENERATE -------- #
                if file_type in ["pdf", "both"]:
                    pdf_bytes = generate_pdf(
                        data, report["root"], report["l2"], report["res"], report["images"]
                    )
                    z.writestr(f"{folder}{pdf_name}", pdf_bytes)

                if file_type in ["word", "both"]:
                    word_bytes = generate_word_doc_wrapper(
                        data, report["root"], report["l2"], report["res"], report["images"]
                    )
                    z.writestr(f"{folder}{word_name}", word_bytes)

            except Exception as e:
                failed_reports.append({
                    "incident": data.get("number"),
                    "error": str(e)
                })

            # -------- PROGRESS -------- #
            percent = int((i / total) * 100)
            progress.progress(percent)
            status.text(f"Processing {i}/{total} ({percent}%)")

        # -------- FAILED CSV -------- #
        if failed_reports:
            buffer = StringIO()
            writer = csv.DictWriter(buffer, fieldnames=["incident", "error"])
            writer.writeheader()
            writer.writerows(failed_reports)

            z.writestr("failed_reports.csv", buffer.getvalue())

    zip_buffer.seek(0)
    status.text("✅ Bulk completed")

    return zip_buffer
