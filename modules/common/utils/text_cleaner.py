import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    lines = str(text).split("\n")
    cleaned = []

    for line in lines:
        line_lower = line.lower()

        # ❌ remove unwanted lines
        if (
            "how does the user want to be contacted" in line_lower
            or "ms teams" in line_lower
            or "phone number" in line_lower
        ):
            continue

        # ❌ remove numbers
        line = re.sub(r"\+?\d{10,15}", "", line)

        cleaned.append(line.strip())

    return "\n".join([l for l in cleaned if l])


def format_description(text):
    return clean_text(text)


def add_images_pdf(*args, **kwargs):
    return
