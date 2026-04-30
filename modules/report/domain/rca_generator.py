def generate_rca(data):
    """
    Generate structured RCA summary (NOT raw dump)
    """

    work_notes = str(data.get("work_notes", "") or "")
    comments = str(data.get("comments", "") or "")
    resolution_notes = str(data.get("resolution", "") or "")

    combined = f"{work_notes}\n{comments}\n{resolution_notes}".strip()

    if not combined:
        return {
            "problem": data.get("short_description", ""),
            "analysis": "",
            "resolution": ""
        }

    # ---------------- SIMPLE SUMMARIZER ---------------- #
    # (You can replace with LLM later if needed)

    lines = [l.strip() for l in combined.split("\n") if l.strip()]

    # Remove noise lines
    filtered = []
    for l in lines:
        if "Attachment:" in l:
            continue
        if "has been attached" in l:
            continue
        filtered.append(l)

    # Build structured RCA
    problem = data.get("short_description", "")

    analysis = "\n".join(filtered[:5])  # first few meaningful lines

    resolution = resolution_notes if resolution_notes else filtered[-1] if filtered else ""

    return {
        "problem": problem,
        "analysis": analysis,
        "resolution": resolution
    }
