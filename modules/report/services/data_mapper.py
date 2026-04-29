from modules.common.utils.parsers import extract_azure_id
from modules.common.utils.formatters import format_description

def get_display(val):
    if isinstance(val, dict):
        return val.get("display_value") or val.get("value")
    return val


def map_incident(row):

    resolution_notes = row.get("Resolution notes") or ""

    return {
        "number": row.get("Number"),

        # ✅ Azure from resolution notes
        "azure_bug": extract_azure_id(resolution_notes),

        # ✅ PTC = Vendor Ticket
        "ptc_case": row.get("Vendor ticket") or row.get("Vendor Ticket"),

        "created_by": row.get("Opened by") or row.get("Created by"),
        "assigned_to": row.get("Assigned to"),

        "created_date": row.get("Created"),
        "resolved_date": row.get("Resolved"),

        "priority": row.get("Priority"),

        "short_description": row.get("Short description"),

        # ✅ Clean description here itself (better than preview)
        "description": format_description(row.get("Description")),
    }
