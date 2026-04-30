from modules.report.utils.utils import format_description
from modules.common.utils.parsers import extract_azure_id
from modules.report.domain.rca_generator import generate_rca
import re
import pandas as pd
from modules.common.utils.formatters import safe_text


# -----------------------------
# Generic cleanup
# -----------------------------
def normalize(text):
    if not text:
        return ""

    text = str(text)

    text = re.sub(r'\s+', ' ', text)
    text = text.replace("\xa0", " ")

    return text.strip()


def clean_noise(text):
    """
    Remove junk from work notes/comments:
    - timestamps
    - names
    - greetings
    - attachments
    - waiting messages
    - thanks
    """

    if not text:
        return ""

    lines = str(text).splitlines()
    cleaned = []

    skip_patterns = [
        r'^\d{4}-\d{2}-\d{2}',                     # timestamps
        r'attachment',
        r'thanks',
        r'thank you',
        r'hello',
        r'hi team',
        r'good morning',
        r'good evening',
        r'please update',
        r'waiting for',
        r'call scheduled',
        r'meeting scheduled',
        r'let me know',
        r'kindly check',
        r'assigning to',
        r'priority changed',
        r'changed priority',
        r'working with l3',
        r'working with aom',
        r'we have informed',
        r'please find attached'
    ]

    for line in lines:
        line = normalize(line)

        if not line:
            continue

        skip = False
        for pattern in skip_patterns:
            if re.search(pattern, line.lower()):
                skip = True
                break

        if not skip:
            cleaned.append(line)

    return "\n".join(cleaned)


def split_lines(text):
    if not text:
        return []

    lines = []

    for line in text.split("\n"):
        line = normalize(line)

        if line and line not in lines:
            lines.append(line)

    return lines


def bulletize(lines):
    if not lines:
        return ""

    return "\n".join([f"• {line}" for line in lines])


# -----------------------------
# Problem statement
# -----------------------------
def is_similar(a, b):
    a = normalize(a).lower()
    b = normalize(b).lower()

    if not a or not b:
        return False

    if a in b or b in a:
        return True

    a_words = set(a.split())
    b_words = set(b.split())

    overlap = len(a_words & b_words)
    similarity = overlap / max(len(a_words), len(b_words))

    return similarity > 0.7


def build_problem(short_desc, description):
    short_desc = normalize(short_desc)
    description = normalize(description)

    problem_lines = []

    if short_desc:
        problem_lines.append(short_desc)

    if description and not is_similar(short_desc, description):
        problem_lines.append(description)

    return bulletize(problem_lines)


# -----------------------------
# Root Cause
# -----------------------------
def extract_root_from_resolution(resolution_notes):
    """
    First preference:
    Try extracting explicit Cause from resolution notes
    """

    if not resolution_notes:
        return []

    lines = resolution_notes.splitlines()
    causes = []

    for line in lines:
        lower = line.lower()

        if (
            "cause:" in lower
            or "root cause:" in lower
            or "reason:" in lower
        ):
            cleaned = re.sub(
                r'(?i)(cause:|root cause:|reason:)',
                '',
                line
            ).strip()

            if cleaned:
                causes.append(cleaned)

    return causes


def build_root_cause(work_notes, additional_comments, resolution_notes):
    # First preference → resolution notes
    explicit_causes = extract_root_from_resolution(resolution_notes)

    if explicit_causes:
        return bulletize(explicit_causes)

    combined = f"{work_notes}\n{additional_comments}"
    combined = clean_noise(combined).lower()

    root_lines = []

    if "certificate" in combined or "pkix" in combined:
        root_lines.append(
            "Certificate validation failure in production prevented ODC integration processing."
        )

    if "scheduler" in combined and "payload" in combined:
        root_lines.append(
            "Scheduler failed to process MCN payload updates, causing ODC integration failures."
        )

    if "path issue" in combined:
        root_lines.append(
            "Incorrect system path configuration caused transaction failures."
        )

    if "permission" in combined:
        root_lines.append(
            "Missing system permissions caused functionality failure."
        )

    if not root_lines:
        root_lines = split_lines(clean_noise(combined))[:3]

    return bulletize(root_lines)


# -----------------------------
# Resolution
# -----------------------------
def extract_resolution_only(resolution_notes):
    if not resolution_notes:
        return []

    lines = resolution_notes.splitlines()
    resolution_lines = []

    for line in lines:
        lower = line.lower()

        # Skip explicit cause lines
        if (
            "cause:" in lower
            or "root cause:" in lower
            or "reason:" in lower
        ):
            continue

        # Skip noise
        if any(x in lower for x in [
            "thanks",
            "thank you",
            "hello",
            "hi",
            "waiting for update"
        ]):
            continue

        cleaned = normalize(line)

        if cleaned:
            resolution_lines.append(cleaned)

    return resolution_lines


def build_resolution(resolution_notes):
    resolution_lines = extract_resolution_only(resolution_notes)

    return bulletize(resolution_lines)


# -----------------------------
# Main RCA Builder
# -----------------------------
def build_rca(row):
    if row is None:
        return {
            "problem_statement": "",
            "root_cause": "",
            "resolution": ""
        }

    # Actual Snow column names
    short_desc = safe_text(
        row.get("short description"),
        default=""
    )

    description = safe_text(
        row.get("description"),
        default=""
    )

    work_notes = safe_text(
        row.get("work notes"),
        default=""
    )

    additional_comments = safe_text(
        row.get("additional comments"),
        default=""
    )

    resolution_notes = safe_text(
        row.get("resolution notes"),
        default=""
    )

    return {
        "problem_statement": build_problem(
            short_desc,
            description
        ),
        "root_cause": build_root_cause(
            work_notes,
            additional_comments,
            resolution_notes
        ),
        "resolution": build_resolution(
            resolution_notes
        )
    }
