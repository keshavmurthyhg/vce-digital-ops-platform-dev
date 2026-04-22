import re

# ---------------- CLEAN TEXT ---------------- #

def clean_lines(text):
    if not text:
        return []

    lines = str(text).split("\n")
    cleaned = []

    for line in lines:
        # remove timestamps
        line = re.sub(r"\d{4}-\d{2}-\d{2}.*?-", "", line)

        # remove names (rough)
        line = re.sub(r"-?\s*[A-Za-z]+\s+[A-Za-z]+\s*\(.*?\)\s*-", "", line)

        # remove "Attachment:"
        line = re.sub(r"Attachment:.*", "", line, flags=re.I)

        # remove empty noise
        line = line.strip()

        if line and len(line) > 5:
            cleaned.append(line)

    return cleaned


# ---------------- GROUP LOGIC ---------------- #

def group_meaningful_points(lines):
    """
    Convert raw lines into meaningful grouped statements
    """

    points = []

    buffer = ""

    for line in lines:
        # If line looks like continuation → append
        if len(line) < 80:
            buffer += " " + line
        else:
            if buffer:
                points.append(buffer.strip())
                buffer = ""
            points.append(line)

    if buffer:
        points.append(buffer.strip())

    return points


# ---------------- ROOT CAUSE ---------------- #

def build_root_cause(work_notes):
    lines = clean_lines(work_notes)

    if not lines:
        return "- Issue identified as system limitation."

    grouped = group_meaningful_points(lines)

    # 🔥 Transform into proper RCA style
    bullets = []
    for g in grouped:
        bullets.append(f"- {g}")

    return "\n".join(bullets)


# ---------------- L2 ANALYSIS ---------------- #

def build_l2_analysis(comments):
    lines = clean_lines(comments)

    if not lines:
        return "- Issue analyzed and validated."

    grouped = group_meaningful_points(lines)

    bullets = []
    for g in grouped:
        bullets.append(f"- {g}")

    return "\n".join(bullets)


# ---------------- MERGE ---------------- #

def merge_with_user_input(auto_text, user_text):
    if user_text and user_text.strip():
        return user_text
    return auto_text
