from modules.common.utils.parsers import extract_azure_id
from modules.common.utils.formatters import format_description

def get_display(val):
    if isinstance(val, dict):
        return val.get("display_value") or val.get("value")
    return val


def map_incident(row):

    resolution_notes = row.get("Resolution_notes") or ""

    return {
        "number": row.get("Number"),

        # ✅ Azure
        "azure_bug": extract_azure_id(Resolution_notes),

        # ✅ Vendor ticket
        "ptc_case": row.get("Vendor_ticket"),

        # ✅ FIXED LOWERCASE KEYS
        "created_by": row.get("Opened_by"),
        "assigned_to": row.get("Assigned_to"),

        "created_date": row.get("Created"),
        "resolved_date": row.get("Resolved"),

        "priority": row.get("priority"),

        "short_description": row.get("short_description"),
        "description": format_description(row.get("description")),
    }
