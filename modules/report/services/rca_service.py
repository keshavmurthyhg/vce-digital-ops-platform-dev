from modules.report.utils.utils import format_description
from modules.common.utils.parsers import extract_azure_id
from modules.report.domain.rca_generator import generate_rca


def build_rca(data):

    # Combine only relevant fields for Azure extraction
    notes = " ".join([
        str(data.get("resolution", "") or ""),
        str(data.get("work_notes", "") or ""),
        str(data.get("comments", "") or "")
    ])

    cleaned = {
        "short_description": data.get("short_description"),
        "description": format_description(data.get("description")),
        "work_notes": data.get("work_notes"),
        "comments": data.get("comments"),
        "resolution": data.get("resolution"),

        # Extract proper Azure bug
        "azure_bug": extract_azure_id(notes)
    }

    return generate_rca(cleaned)
