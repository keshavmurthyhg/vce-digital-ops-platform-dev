def calculate_kpi(df):
    if df.empty:
        return {
            "total": 0,
            "open": 0,
            "closed": 0,
            "cancelled": 0
        }

    status_col = "Status"

    total = len(df)

    open_count = df[df[status_col].str.contains("open", case=False, na=False)].shape[0]

    closed_count = df[df[status_col].str.contains("closed", case=False, na=False)].shape[0]

    cancelled_count = df[df[status_col].str.contains("cancel", case=False, na=False)].shape[0]

    return {
        "total": total,
        "open": open_count,
        "closed": closed_count,
        "cancelled": cancelled_count
    }
