from modules.common.utils.parsers import extract_azure_id
from modules.common.utils.formatters import format_description

def get_display(val):
    if isinstance(val, dict):
        return val.get("display_value") or val.get("value")
    return val


def map_incident(row):

    resolution_notes = row.get("resolution notes") or ""

    return {
        "number": row.get("number"),

        # ✅ Azure from resolution notes
        "azure_bug": extract_azure_id(resolution_notes),

        # ✅ PTC = Vendor Ticket
        "ptc_case": row.get("vendor ticket"),

        # ✅ FIXED KEYS (WITH SPACES)
        "created_by": row.get("opened by"),
        "assigned_to": row.get("assigned to"),

        "created_date": row.get("created"),
        "resolved_date": row.get("resolved"),

        "priority": row.get("priority"),

        "short_description": row.get("short description"),
        "description": format_description(row.get("description")),
    }
