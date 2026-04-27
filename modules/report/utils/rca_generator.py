import re


def clean_text(text):
    if not text:
        return ""
    return str(text)


def remove_noise(text):
    if not text:
        return ""

    # remove timestamps
    text = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "", text)

    # remove names like "Keshavamurthy Hg"
    text = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "", text)

    # remove keywords
    text = re.sub(r"(Work notes|Additional comments|Attachment:)", "", text, flags=re.I)

    return text.strip()


def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text) if text else []


def filter_meaningful(lines):
    cleaned = []
    for l in lines:
        l = l.strip()

        if not l:
            continue

        # remove noise lines
        if any(x in l.lower() for x in [
            "attachment", "has been attached", "closing the incident",
            "as confirmed", "as discussed", "thanks"
        ]):
            continue

        cleaned.append(l)

    return cleaned


def detect_root_cause(text):
    t = text.lower()

    if any(k in t for k in ["permission", "access", "not allowed"]):
        return "Permission Issue"

    if any(k in t for k in ["bug", "defect", "error"]):
        return "Application Bug"

    if any(k in t for k in ["config", "setting", "setup"]):
        return "Configuration Issue"

    return "System Behavior"


def highlight_ids(text):
    # highlight Azure IDs
    return re.sub(r"\b\d{6,7}\b", r"[AZURE:\g<0>]", text)


def generate_rca(data):

    short_desc = clean_text(data.get("short_description"))
    desc = clean_text(data.get("description"))

    work = remove_noise(clean_text(data.get("work_notes")))
    comments = remove_noise(clean_text(data.get("comments")))
    add_comments = remove_noise(clean_text(data.get("additional_comments")))

    resolution_notes = remove_noise(
        clean_text(data.get("resolution_notes") or data.get("resolution"))
    )

    # ---------------- PROBLEM ---------------- #
    problem_text = f"{short_desc}. {desc}"
    problem_lines = filter_meaningful(split_sentences(problem_text))

    problem = "\n".join(f"• {highlight_ids(l)}" for l in problem_lines[:3])

    # ---------------- ROOT CAUSE ---------------- #
    rc_source = " ".join([work, comments, add_comments])
    rc_lines = filter_meaningful(split_sentences(rc_source))

    rc_type = detect_root_cause(rc_source)

    root_cause = f"Root Cause Type: {rc_type}\n"
    root_cause += "\n".join(f"• {highlight_ids(l)}" for l in rc_lines[:3])

    # ---------------- RESOLUTION ---------------- #
    if resolution_notes:
        res_lines = filter_meaningful(split_sentences(resolution_notes))
    else:
        res_lines = filter_meaningful(split_sentences(rc_source))

    resolution = "\n".join(f"• {highlight_ids(l)}" for l in res_lines[:3])

    return {
        "problem": problem,
        "analysis": root_cause,
        "resolution": resolution
    }
