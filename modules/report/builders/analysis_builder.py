import re


def clean_description(text):
    if not text:
        return ""

    lines = text.split("\n")
    cleaned = []

    for l in lines:
        l_low = l.lower().strip()

        # remove contact / noise
        if any(x in l_low for x in [
            "how does the user",
            "contact",
            "ms teams",
            "phone",
            "mobile",
            "+",
            "email"
        ]):
            continue

        # remove phone numbers
        if "+" in l or "phone" in l_low:
            continue

        if len(l.strip()) > 10:
            cleaned.append(l.strip())

    return "\n".join(cleaned)
