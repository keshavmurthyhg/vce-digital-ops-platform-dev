import re


def clean_text(text):
    if not text:
        return ""
    return str(text).replace("\n", " ").strip()


def split_sentences(text):
    if not text:
        return []
    return re.split(r'(?<=[.!?])\s+', text)


def pick_meaningful(lines, max_lines=3):
    return [l.strip() for l in lines if l.strip()][:max_lines]


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
    problem_parts = [short_desc, desc]
    problem_sentences = split_sentences(" ".join(problem_parts))
    problem = "\n".join(f"• {s}" for s in pick_meaningful(problem_sentences))

    # ---------------- ROOT CAUSE ---------------- #
    rc_source = " ".join([work, comments, add_comments])
    rc_sentences = split_sentences(rc_source)

    root_cause = "\n".join(
        f"• {s}" for s in pick_meaningful(rc_sentences)
    )

    # ---------------- RESOLUTION ---------------- #
    if resolution_notes:
        res_sentences = split_sentences(resolution_notes)
    else:
        # fallback if resolution notes missing
        res_sentences = split_sentences(rc_source)

    resolution = "\n".join(
        f"• {s}" for s in pick_meaningful(res_sentences)
    )

    return {
        "problem": problem or "",
        "analysis": root_cause or "",   # reuse key
        "resolution": resolution or ""
    }
