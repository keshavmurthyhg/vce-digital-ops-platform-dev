def format_date(value):
    if not value:
        return "-"
    try:
        return value.strftime("%d-%b-%Y")
    except:
        return str(value)


def safe_text(value):
    return value if value else "-"
