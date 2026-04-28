import re


# ---------------- HELPERS ---------------- #

def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text) if text else []


def remove_noise_lines(lines):
    cleaned = []

    for l in lines:
        l = l.strip()
        if not l:
            continue

        l_low = l.lower()

        # remove noise
        if any(x in l_low for x in [
            "keep you posted",
            "waiting",
            "thanks",
            "as discussed",
            "as confirmed",
            "over teams",
            "closing the incident",
            "attachment",
            "has been attached",
            "work notes",
            "additional comments"
        ]):
            continue

        cleaned.append(l)

    return cleaned


# ---------------- PROBLEM ---------------- #

def summarize_problem(short_desc, desc):
    lines = []

    if short_desc:
        lines.append(short_desc.strip())

    for l in split_sentences(desc):
        l = l.strip()

        if l.lower().startswith("this"):
            continue

        if len(l) > 20:
            lines.append(l)

    return lines[:3]


# ---------------- ROOT CAUSE ---------------- #

def detect_root_cause_type(text):
    t = text.lower()

    if "permission" in t or "access" in t:
        return "Permission Issue"

    if "blocked" in t:
        return "System Restriction"

    if "error" in t or "exception" in t:
        return "Application Error"

    return "System Behavior"


def summarize_root_cause(lines):
    cause_lines = []

    for l in lines:
        l_low = l.lower()

        if any(k in l_low for k in [
            "blocked",
            "missing",
            "not available",
            "not allowed",
            "permission"
        ]):
            cause_lines.append(l)

    if not cause_lines:
        cause_lines = lines[:2]

    return cause_lines[:3]


# ---------------- RESOLUTION ---------------- #

def summarize_resolution(lines):
    cleaned = []

    for l in lines:
        l_low = l.lower().strip()

        # remove noise
        if any(x in l_low for x in [
            "as discussed",
            "as confirmed",
            "over teams",
            "closing the incident",
            "thanks",
            "we will",
            "please",
            "kindly"
        ]):
            continue

        # remove weak lines
        if l_low.startswith("this allows"):
            continue

        if any(x in l_low for x in [
            "validation",
            "test user",
            "environment",
            "objects tested",
            "observation"
        ]):
            continue

        if len(l.strip()) < 15:
            continue

        cleaned.append(l.strip())

    if not cleaned:
        return ["Resolution details not available"]

    return cleaned[:3]


# ---------------- MAIN RCA ---------------- #

def generate_rca(data):
    from modules.report.utils.utils import format_description

    short_desc = data.get("short_description", "")
    desc = format_description(data.get("description", ""))
    work_notes = data.get("work_notes", "")
    comments = data.get("comments", "")
    resolution = data.get("resolution", "")

    # PROBLEM
    problem_lines = summarize_problem(short_desc, desc)

    # ROOT CAUSE
    combined = "\n".join([work_notes, comments])
    lines = split_sentences(combined)
    lines = remove_noise_lines(lines)

    root_type = detect_root_cause_type(combined)
    root_lines = summarize_root_cause(lines)

    root_output = [f"Root Cause Type: {root_type}"] + root_lines

    # RESOLUTION
    res_lines = split_sentences(resolution)
    res_lines = remove_noise_lines(res_lines)
    res_lines = summarize_resolution(res_lines)

    return {
        "problem": "\n".join(f"• {l}" for l in problem_lines),
        "analysis": "\n".join(f"• {l}" for l in root_output),
        "resolution": "\n".join(f"• {l}" for l in res_lines),
    }
