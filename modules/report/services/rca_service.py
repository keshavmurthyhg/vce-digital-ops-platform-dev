from modules.report.utils.utils import format_description
from modules.common.utils.parsers import extract_azure_id
from modules.report.domain.rca_generator import generate_rca
import re
from modules.common.utils.formatters import safe_text


IGNORE_PATTERNS = [
    r".*working with l[0-9].*",
    r".*informed l[0-9].*",
    r".*meeting scheduled.*",
    r".*waiting for.*",
    r".*please update.*",
    r".*any update.*",
    r".*priority changed.*",
    r".*changing priority.*",
    r".*assigned to.*",
    r".*call scheduled.*",
    r".*issue still occurring.*",
    r".*attached.*",
    r".*attachment.*",
    r".*\.xlsx.*",
    r".*\.jpg.*",
    r".*\.png.*",
    r".*transaction id.*",
    r".*payload entry.*",
]


def clean_lines(text):
    if not text:
        return []

    cleaned = []

    for line in str(text).split("\n"):
        line = line.strip()

        if not line:
            continue

        # remove timestamps
        line = re.sub(
            r"^\d{4}-\d{2}-\d{2}.*?:",
            "",
            line
        ).strip()

        skip = False
        for pattern in IGNORE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                skip = True
                break

        if skip:
            continue

        cleaned.append(line)

    return cleaned


def extract_resolution_sections(resolution_notes):
    """
    Highest priority source.
    """
    cause = []
    resolution = []

    lines = clean_lines(resolution_notes)

    for line in lines:
        lower = line.lower()

        if "cause" in lower:
            cause.append(
                re.sub(r"(?i)cause\s*[:\-]?", "", line).strip()
            )

        elif any(x in lower for x in [
            "resolved",
            "fixed",
            "implemented",
            "updated",
            "restarted",
            "validated",
            "working fine",
            "resolution"
        ]):
            resolution.append(
                re.sub(
                    r"(?i)resolution\s*[:\-]?",
                    "",
                    line
                ).strip()
            )

    return cause, resolution


def fallback_root_cause(work_notes, comments):
    """
    Use only meaningful technical observations
    when resolution notes don't provide cause.
    """
    combined = "\n".join([
        safe_text(work_notes, default=""),
        safe_text(comments, default="")
    ])

    lines = clean_lines(combined)

    technical_lines = []

    for line in lines:
        lower = line.lower()

        if any(x in lower for x in [
            "error",
            "failed",
            "failure",
            "exception",
            "incorrect path",
            "certificate",
            "missing",
            "validation issue",
            "integration failure",
            "configuration issue",
            "bug"
        ]):
            technical_lines.append(line)

    return technical_lines


def format_output(lines):
    if not lines:
        return ""

    seen = set()
    final_lines = []

    for line in lines:
        if line and line not in seen:
            seen.add(line)
            final_lines.append(f"• {line}")

    return "\n".join(final_lines)


def build_rca(row):
    short_desc = safe_text(
        row.get("short_description"),
        default=""
    )

    description = safe_text(
        row.get("description"),
        default=""
    )

    resolution_notes = safe_text(
        row.get("resolution_notes"),
        default=""
    )

    work_notes = row.get("work_notes")
    comments = row.get("comments")

    # Problem statement
    problem_lines = []

    if short_desc:
        problem_lines.append(short_desc)

    if description:
        problem_lines.append(description)

    # Priority source
    cause_lines, resolution_lines = extract_resolution_sections(
        resolution_notes
    )

    # fallback root cause only if no cause found
    if not cause_lines:
        cause_lines = fallback_root_cause(
            work_notes,
            comments
        )

    return {
        "problem": format_output(problem_lines),
        "analysis": format_output(cause_lines),
        "resolution": format_output(resolution_lines)
    }
