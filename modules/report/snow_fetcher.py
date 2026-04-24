def fetch_snow_data_from_incident(incident):

    from modules.data.snow_loader import load_snow_data

    df = load_snow_data()  # returns DataFrame

    # ✅ FIX: Proper empty check for DataFrame
    if df is None:
        return None

    if hasattr(df, "empty") and df.empty:
        return None

    # ✅ Convert DataFrame → list of dicts
    all_data = df.to_dict(orient="records")

    # 🔍 Find matching incident
    data = None
    for row in all_data:
        if str(row.get("number", "")).strip().upper() == incident.upper():
            data = row
            break

    if data is None:
        return None

    # 🔄 Normalize structure
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
