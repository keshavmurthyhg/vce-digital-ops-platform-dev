import re


def clean_text(text):
    return str(text or "")


def remove_noise_lines(lines):
    filtered = []
    for l in lines:
        l = l.strip()

        if not l:
            continue

        if any(x in l.lower() for x in [
            "keep you posted",
            "waiting",
            "thanks",
            "(", ")",
            "attachment",
            "has been attached",
            "additional comments",
            "work notes"
        ]):
            continue

        filtered.append(l)

    return filtered


def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text) if text else []


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
    # extract meaningful cause (not actions)
    cause_lines = []

    for l in lines:
        if any(k in l.lower() for k in [
            "blocked", "missing", "not available",
            "permission", "not allowed"
        ]):
            cause_lines.append(l)

    if not cause_lines:
        cause_lines = lines[:2]

    return cause_lines


def summarize_resolution(lines):
    result = []

    for l in lines:
        if "created" in l.lower() or "provided" in l.lower():
            result.append(l)

        elif "allow" in l.lower():
            # expand incomplete line
            result.append(l.replace("This allows", "This change allows users to"))

    if not result:
        result = lines[:2]

    return result


def generate_rca(data):

    short_desc = clean_text(data.get("short_description"))
    desc = clean_text(data.get("description"))

    work = clean_text(data.get("work_notes"))
    comments = clean_text(data.get("comments"))
    add_comments = clean_text(data.get("additional_comments"))

    resolution_notes = clean_text(
        data.get("resolution_notes") or data.get("resolution")
    )

    # ---------------- PROBLEM ---------------- #
    problem_text = f"{short_desc}. {desc}"
    problem_lines = remove_noise_lines(split_sentences(problem_text))

    problem = "\n".join(f"• {l}" for l in problem_lines[:3])

    # ---------------- ROOT CAUSE ---------------- #
    rc_source = " ".join([work, comments, add_comments])
    rc_lines = remove_noise_lines(split_sentences(rc_source))

    rc_type = detect_root_cause_type(rc_source)

    cause_lines = summarize_root_cause(rc_lines)

    root_cause = f"Root Cause Type: {rc_type}\n"
    root_cause += "\n".join(f"• {l}" for l in cause_lines[:3])

    # ---------------- RESOLUTION ---------------- #
    res_lines = remove_noise_lines(
        split_sentences(resolution_notes if resolution_notes else rc_source)
    )

    res_lines = summarize_resolution(res_lines)

    resolution = "\n".join(f"• {l}" for l in res_lines[:3])

    return {
        "problem": problem,
        "analysis": root_cause,
        "resolution": resolution
    }
