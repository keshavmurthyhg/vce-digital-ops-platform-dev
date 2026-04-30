from modules.report.utils.utils import format_description
from modules.common.utils.parsers import extract_azure_id
from modules.report.domain.rca_generator import generate_rca
import re
from modules.common.utils.formatters import safe_text


NOISE_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}.*$",                 # timestamps
    r".*\(Work notes\).*",
    r".*\(Additional comments\).*",
    r"^Hi\b.*",
    r"^Hello\b.*",
    r"^Thanks\b.*",
    r"^Thank you\b.*",
    r"^BR\b.*",
    r"^Regards\b.*",
    r"^Waiting for.*",
    r"^Please update.*",
    r"^Any update.*",
    r"^Attachment:.*",
    r".*\.xlsx$",
    r".*\.jpg$",
    r".*\.png$",
    r".*\.pdf$",
]


def clean_note_lines(text):
    """
    Remove timestamps, greetings, attachments, signatures,
    and useless operational chatter.
    """
    if not text:
        return []

    cleaned = []

    for line in str(text).split("\n"):
        line = line.strip()

        if not line:
            continue

        skip = False
        for pattern in NOISE_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                skip = True
                break

        if skip:
            continue

        cleaned.append(line)

    return cleaned


def extract_resolution_parts(lines):
    """
    Split meaningful lines into:
    - root cause
    - resolution
    """

    root_lines = []
    resolution_lines = []

    for line in lines:
        lower = line.lower()

        if any(word in lower for word in [
            "fixed",
            "resolved",
            "updated",
            "implemented",
            "validated",
            "restarted",
            "working fine",
            "closed"
        ]):
            resolution_lines.append(line)

        elif "cause" in lower:
            root_lines.append(line)

        else:
            root_lines.append(line)

    return root_lines, resolution_lines


def format_bullets(lines):
    if not lines:
        return ""

    unique_lines = []
    seen = set()

    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    return "\n".join([f"• {x}" for x in unique_lines])


def build_rca(row):
    """
    Intelligent RCA builder using SNOW fields
    """

    problem = safe_text(
        row.get("short_description"),
        default=""
    )

    work_notes = safe_text(
        row.get("work_notes"),
        default=""
    )

    additional_comments = safe_text(
        row.get("comments"),
        default=""
    )

    resolution_notes = safe_text(
        row.get("resolution_notes"),
        default=""
    )

    combined_notes = "\n".join([
        work_notes,
        additional_comments,
        resolution_notes
    ])

    cleaned_lines = clean_note_lines(combined_notes)

    root_lines, resolution_lines = extract_resolution_parts(
        cleaned_lines
    )

    return {
        "problem": format_bullets([problem]),
        "analysis": format_bullets(root_lines),
        "resolution": format_bullets(resolution_lines)
    }
