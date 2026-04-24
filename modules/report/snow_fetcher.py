def fetch_snow_data_from_incident(incident):
    """
    Reuse existing SNOW loader logic
    """

    # 👇 IMPORT your existing loader
    from modules.data.snow_loader import load_snow_data  # adjust if different

    data = load_snow_data(incident)

    if not data:
        return None

    # Ensure correct structure for doc_generator
    return {
        "number": data.get("number"),
        "short_description": data.get("short_description"),
        "description": data.get("description"),
        "created_by": data.get("created_by"),
        "created_date": data.get("created_date"),
        "assigned_to": data.get("assigned_to"),
        "priority": data.get("priority"),
        "resolved_date": data.get("resolved_date"),
        "azure_bug": data.get("azure_bug"),
        "ptc_case": data.get("ptc_case")
    }
