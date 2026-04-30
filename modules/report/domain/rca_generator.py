import re


def summarize_notes(text):
    if not text:
        return ""

    lines = []

    for line in str(text).split("\n"):
        line = line.strip()

        if not line:
            continue

        if "attachment:" in line.lower():
            continue

        if "has been attached" in line.lower():
            continue

        if "hcl integration" in line.lower():
            continue

        if re.match(r"^\d{4}-\d{2}-\d{2}", line):
            continue

        lines.append(line)

    if not lines:
        return ""

    # Return concise summary instead of raw dump
    summary = " ".join(lines[:3])

    return summary[:1000]


def generate_rca(data):

    problem = data.get("short_description", "")

    analysis_text = (
        str(data.get("work_notes", "") or "") +
        "\n" +
        str(data.get("comments", "") or "")
    )

    resolution_raw = data.get("resolution")

    if resolution_raw is None:
        resolution_text = ""
    else:
        resolution_text = str(resolution_raw).strip()
    
    if resolution_text.lower() in ["nan", "nat", "none"]:
        resolution_text = ""

    analysis = summarize_notes(analysis_text)
    resolution = summarize_notes(resolution_text)

    return {
        "problem": problem,
        "analysis": analysis,
        "resolution": resolution
    }
