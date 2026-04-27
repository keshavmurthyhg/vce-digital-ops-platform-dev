import re


# ---------------- CLEAN HELPERS ---------------- #

def clean_text(text):
    return str(text or "").strip()


def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text) if text else []


def remove_noise_lines(lines):
    cleaned = []

    for l in lines:
        l = l.strip()
        if not l:
            continue

        l_low = l.lower()

        # remove useless / conversational
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
            "additional comments",
            "(",
            ")"
        ]):
            continue

        cleaned.append(l)

    return cleaned


# ---------------- PROBLEM ---------------- #

def summarize_problem(short_desc, desc):
    lines = []

    if short_desc:
        lines.append(short_desc.strip())

    desc_lines = split_sentences(desc)

    for l in desc_lines:
        l = l.strip()

        # remove unclear sentences
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

        # ❌ remove conversation noise
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

        # ❌ remove weak / incomplete lines
        if l_low.startswith("this allows"):
            continue

        # ❌ remove validation logs
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

    # ✅ fallback only if NOTHING meaningful
    if not cleaned:
        return ["Resolution details not available"]

    return cleaned[:3]
