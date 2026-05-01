import re


# ---------------- SAFE VALUE ---------------- #
def safe_text(val):
    if val is None:
        return ""

    val = str(val).strip()

    if val.lower() in ["nan", "nat", "none"]:
        return ""

    return val


# ---------------- CLEAN NOISE ---------------- #
def clean_lines(text):
    if not text:
        return []

    lines = []

    noise_words = [
        "hello",
        "hi team",
        "thanks",
        "thank you",
        "regards",
        "br,",
        "please close",
        "closing incident",
        "call scheduled",
        "waiting for response",
        "waiting for update",
        "attached",
        "attachment:",
    ]

    for raw in text.split("\n"):
        line = raw.strip()

        if not line:
            continue

        lower = line.lower()

        # remove timestamps
        if re.match(r"^\d{4}-\d{2}-\d{2}", line):
            continue

        # remove names-only lines
        if len(line.split()) <= 2 and line.istitle():
            continue

        # remove noise
        if any(x in lower for x in noise_words):
            continue

        lines.append(line)

    return lines


# ---------------- PROBLEM ---------------- #
def build_problem(data):
    short_desc = safe_text(data.get("short_description"))
    desc = safe_text(data.get("description"))

    problem_lines = []

    if short_desc:
        problem_lines.append(short_desc)

    if desc:
        short_clean = short_desc.lower().strip()
        desc_clean = desc.lower().strip()

        # Avoid duplicate/near duplicate statements
        if (
            desc_clean != short_clean
            and short_clean not in desc_clean
            and desc_clean not in short_clean
        ):
            problem_lines.append(desc)

    # remove duplicates while preserving order
    problem_lines = list(dict.fromkeys(problem_lines))

    return "\n".join(
        [f"• {x}" for x in problem_lines[:2]]
    )


# ---------------- ROOT CAUSE ---------------- #
def build_root_cause(data):
    resolution_notes = safe_text(data.get("resolution notes"))
    work_notes = safe_text(data.get("work notes"))
    comments = safe_text(data.get("additional comments"))

    combined = "\n".join([
        resolution_notes,
        work_notes,
        comments
    ])

    lines = clean_lines(combined)

    root_lines = []

    for line in lines:
        lower = line.lower()

        # Highest priority = explicit cause
        if "cause:" in lower:
            root_lines.append(line)

        elif "root cause" in lower:
            root_lines.append(line)

        elif "failed due to" in lower:
            root_lines.append(line)

        elif "error" in lower:
            root_lines.append(line)

        elif "certificate" in lower:
            root_lines.append(line)

        elif "path issue" in lower:
            root_lines.append(line)

        elif "incorrect path" in lower:
            root_lines.append(line)

        elif "validation issue" in lower:
            root_lines.append(line)

    root_lines = list(dict.fromkeys(root_lines))

    return "\n".join(
        [f"• {x}" for x in root_lines[:5]]
    )


# ---------------- RESOLUTION ---------------- #
def build_resolution(data):
    resolution_notes = safe_text(data.get("resolution notes"))

    lines = clean_lines(resolution_notes)

    resolution_lines = []

    for line in lines:
        lower = line.lower()

        if "resolution:" in lower:
            resolution_lines.append(line)

        elif "fixed" in lower:
            resolution_lines.append(line)

        elif "implemented" in lower:
            resolution_lines.append(line)

        elif "restarted" in lower:
            resolution_lines.append(line)

        elif "validated" in lower:
            resolution_lines.append(line)

        elif "working fine" in lower:
            resolution_lines.append(line)

        elif "success" in lower:
            resolution_lines.append(line)

    resolution_lines = list(dict.fromkeys(resolution_lines))

    return "\n".join(
        [f"• {x}" for x in resolution_lines[:5]]
    )


# ---------------- MAIN ---------------- #
def build_rca(data):
    return {
        "problem_statement": build_problem(data),
        "root_cause": build_root_cause(data),
        "resolution": build_resolution(data)
    }
