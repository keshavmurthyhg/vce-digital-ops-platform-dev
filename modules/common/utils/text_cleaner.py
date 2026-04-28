def clean_description(text):
    if not text:
        return ""

    lines = text.split("\n")
    cleaned = []

    for l in lines:
        l_low = l.lower()

        if any(x in l_low for x in [
            "contact", "phone", "email", "ms teams",
            "how does the user"
        ]):
            continue

        if len(l.strip()) > 10:
            cleaned.append(l.strip())

    return " ".join(cleaned)
