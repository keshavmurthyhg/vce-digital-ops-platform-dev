def get_display(val):
    if isinstance(val, dict):
        return val.get("display_value") or val.get("value")
    return val


def map_incident(row_raw):
    return {
        "number": row_raw.get("number"),

        "short_description": (
            row_raw.get("short_description")
            or row_raw.get("short description")
            or "-"
        ),

        "description": row_raw.get("description") or "-",

        "priority": get_display(row_raw.get("priority")) or "-",

        "opened_by": get_display(
            row_raw.get("opened_by") or row_raw.get("sys_created_by")
        ) or "-",

        "assigned_to": get_display(row_raw.get("assigned_to")) or "-",

        "created": (
            row_raw.get("sys_created_on")
            or row_raw.get("opened_at")
            or row_raw.get("created")
        ),

        "resolved": (
            row_raw.get("closed_at")
            or row_raw.get("resolved_at")
        ),

        "azure_bug": (
            row_raw.get("azure_bug")
            or row_raw.get("u_azure_bug")
            or "-"
        ),

        "ptc_case": (
            row_raw.get("ptc_case")
            or row_raw.get("u_ptc_case")
            or "-"
        ),
    }
