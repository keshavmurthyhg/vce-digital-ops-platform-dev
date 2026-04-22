import re

# -----------------------------
# CLEAN TEXT (REMOVE TIMESTAMPS)
# -----------------------------
def clean_text(text):
    if not text:
        return ""

    lines = str(text).split("\n")

    cleaned = []
    for line in lines:
        # remove timestamps like 2024-01-01 10:20 or [10:20]
        line = re.sub(r"\[?\d{1,2}:\d{2}(:\d{2})?\]?", "", line)
        line = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "", line)

        line = line.strip()
        if line:
            cleaned.append(line)

    return cleaned


# -----------------------------
# ROOT CAUSE GENERATOR
# -----------------------------
def build_root_cause(work_notes):
    lines = clean_text(work_notes)

    bullets = []

    for l in lines:
        bullets.append(f"- {l}")

    # fallback if empty
    if not bullets:
        bullets = [
            "- Issue identified as system/product limitation.",
            "- Behavior deviates from expected functionality.",
            "- Requires vendor/product fix."
        ]

    return "\n".join(bullets)


# -----------------------------
# L2 ANALYSIS GENERATOR
# -----------------------------
def build_l2_analysis(comments):
    lines = clean_text(comments)

    bullets = []

    for l in lines:
        bullets.append(f"- {l}")

    if not bullets:
        bullets = [
            "- Issue validated in latest supported version.",
            "- Reproducible scenario identified.",
            "- Vendor engagement initiated for fix."
        ]

    return "\n".join(bullets)


# -----------------------------
# MERGE USER EDITS (IMPORTANT)
# -----------------------------
def merge_with_user_input(auto_text, user_text):
    """
    If user edits, preserve their version.
    If empty, use auto-generated.
    """
    if user_text and user_text.strip():
        return user_text
    return auto_text
