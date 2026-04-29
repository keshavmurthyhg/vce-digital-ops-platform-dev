from modules.common.utils.parsers import extract_azure_id
from modules.common.utils.formatters import format_description

def get_display(val):
    if isinstance(val, dict):
        return val.get("display_value") or val.get("value")
    return val


def map_incident(row):

    resolution_notes = row.get("resolution_notes") or ""

    return {
        "number": row.get("number"),

        # ✅ Azure
        "azure_bug": extract_azure_id(resolution_notes),

        # ✅ Vendor ticket
        "ptc_case": row.get("vendor_ticket"),

        # ✅ FIXED LOWERCASE KEYS
        "created_by": row.get("opened_by"),
        "assigned_to": row.get("assigned_to"),

        "created_date": row.get("created"),
        "resolved_date": row.get("resolved"),

        "priority": row.get("priority"),

        "short_description": row.get("short_description"),
        "description": format_description(row.get("description")),
    }
