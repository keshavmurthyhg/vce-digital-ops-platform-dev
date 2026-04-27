import re

def clean_text(text):
    if not text:
        return ""
    return str(text).replace("\n", " ").strip()


def extract_sentences(text):
    if not text:
        return []
    return re.split(r'(?<=[.!?])\s+', text)


def generate_rca(data):
    short_desc = clean_text(data.get("short_description"))
    desc = clean_text(data.get("description"))
    work = clean_text(data.get("work_notes"))
    comments = clean_text(data.get("comments"))
    add_comments = clean_text(data.get("additional_comments"))
    resolution = clean_text(data.get("resolution_notes"))

    combined = " ".join([
        short_desc, desc, work, comments, add_comments
    ])

    sentences = extract_sentences(combined)

    # ---------------- PROBLEM ---------------- #
    problem = short_desc if short_desc else (sentences[0] if sentences else "Issue reported")

    # ---------------- ANALYSIS ---------------- #
    analysis_points = []

    KEYWORDS = [
        "error", "fail", "issue", "not working",
        "unable", "blocked", "exception", "missing"
    ]
    
    for s in sentences:
        if any(k in s.lower() for k in KEYWORDS):
            analysis_points.append(s)
    
    # ✅ fallback if nothing matched
    if not analysis_points:
        analysis_points = sentences[:3]

    analysis = "\n".join(f"• {s}" for s in analysis_points[:3]) or "• Analysis not available"

    # ---------------- RESOLUTION ---------------- #
    res_sentences = extract_sentences(resolution)

    resolution_text = "\n".join(f"• {s}" for s in res_sentences[:3]) \
        if res_sentences else "• Resolution details not available"

    return {
        "problem": problem,
        "analysis": analysis,
        "resolution": resolution_text
    }
