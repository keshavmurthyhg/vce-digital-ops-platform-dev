import re


def clean_noise(lines):
    cleaned = []

    for line in lines:
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

        cleaned.append(line)

    return cleaned


def generate_rca(data):

    work_notes = str(data.get("work_notes", "") or "")
    comments = str(data.get("comments", "") or "")
    resolution_notes = str(data.get("resolution", "") or "")

    all_notes = f"{work_notes}\n{comments}".strip()

    lines = all_notes.split("\n")
    cleaned_lines = clean_noise(lines)

    problem = data.get("short_description", "")

    analysis = "\n".join(cleaned_lines[:5])

    resolution = resolution_notes.strip()

    return {
        "problem": problem,
        "analysis": analysis,
        "resolution": resolution
    }
