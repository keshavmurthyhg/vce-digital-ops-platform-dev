import re

def extract_azure_id(text):
    if not text:
        return None

    match = re.search(r'\b\d{6,7}\b', text)
    return match.group(0) if match else None
