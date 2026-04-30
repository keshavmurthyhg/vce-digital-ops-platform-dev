from modules.common.utils.parsers import extract_azure_id
from modules.common.utils.formatters import format_description, safe_text


def map_incident(row):

    work_notes = row.get("work notes") or ""
    comments = row.get("additional comments") or ""
    resolution_notes = row.get("resolution notes") or ""

    combined_notes = " ".join([
        str(work_notes),
        str(comments),
        str(resolution_notes)
    ])

    return {
        "number": safe_text(row.get("number")),

        # Azure only from actual notes
        "azure_bug": extract_azure_id(combined_notes),

        "ptc_case": safe_text(row.get("vendor ticket")),

        "created_by": safe_text(row.get("opened by")),
        "assigned_to": safe_text(row.get("assigned to")),

        "created_date": row.get("created"),
        "resolved_date": row.get("resolved"),

        "priority": safe_text(row.get("priority")),

        "short_description": safe_text(row.get("short description")),
        "description": format_description(row.get("description")),

        # REQUIRED FOR RCA
        "work_notes": work_notes,
        "comments": comments,
        "resolution": resolution_notes
    }
