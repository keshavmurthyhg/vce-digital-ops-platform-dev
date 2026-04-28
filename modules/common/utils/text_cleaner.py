import re

def clean_text(text):
    if not text:
        return ""

    # remove phone numbers
    text = re.sub(r'\+?\d[\d\s\-]{7,}', '', text)

    # remove contact phrases
    text = re.sub(r'How does the user.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'contact.*', '', text, flags=re.IGNORECASE)

    return text.strip()


def format_description(text):
    return clean_text(text)


def add_images_pdf(*args, **kwargs):
    return
