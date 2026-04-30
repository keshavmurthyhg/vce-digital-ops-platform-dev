import re

def extract_azure_id(text):
    if not text:
        return ""

    text = str(text)

    # ✅ Only pick 6 digit numbers (Azure IDs)
    matches = re.findall(r"\b\d{6}\b", text)

    if not matches:
        return ""

    # Optional: take first valid Azure ID
    return matches[0]
