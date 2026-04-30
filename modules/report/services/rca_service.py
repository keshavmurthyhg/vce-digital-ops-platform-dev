import re
import pandas as pd


# -----------------------------
# Safe field reader
# -----------------------------
def get_field_value(row, field_name):
    value = row.get(field_name, "")

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except:
        pass

    value = str(value).strip()

    if value.lower() in ["nan", "nat", "none"]:
        return ""

    return value


# -----------------------------
# Generic cleanup
# -----------------------------
def normalize(text):
    if not text:
        return ""

    text = str(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_noise(text):
    if not text:
        return ""

    lines = str(text).splitlines()
    cleaned = []

    skip_patterns = [
        r'^\d{4}-\d{2}-\d{2}',   # timestamps
        r'attachment',
        r'has been attached',
        r'thanks',
        r'thank you',
        r'hello',
        r'hi team',
        r'good morning',
        r'good evening',
        r'please update',
        r'waiting for update',
        r'call scheduled',
        r'meeting scheduled',
        r'assigning to',
        r'priority changed',
        r'working with l3',
        r'working with aom',
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


def bulletize(lines):
    if not lines:
        return ""

    unique_lines = []

    for line in lines:
        line = normalize(line)

        if line and line not in unique_lines:
            unique_lines.append(line)

    return "\n".join([f"• {line}" for line in unique_lines])


# -----------------------------
# Problem Statement
# -----------------------------
def is_similar(a, b):
    a = normalize(a).lower()
    b = normalize(b).lower()

    if not a or not b:
        return False

    if a in b or b in a:
        return True

    return False


def build_problem(short_desc, description):
    problem_lines = []

    short_desc = normalize(short_desc)
    description = normalize(description)

    if short_desc:
        problem_lines.append(short_desc)

    if description and not is_similar(short_desc, description):
        problem_lines.append(description)

    return bulletize(problem_lines)


# -----------------------------
# Root Cause
# -----------------------------
def extract_root_from_resolution(resolution_notes):
    if not resolution_notes:
        return []

    causes = []

    for line in resolution_notes.splitlines():
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
    # First preference → explicit cause from resolution notes
    explicit_causes = extract_root_from_resolution(resolution_notes)

    if explicit_causes:
        return bulletize(explicit_causes)

    combined = f"{work_notes}\n{additional_comments}"
    cleaned_text = clean_noise(combined).lower()

    root_lines = []

    if "pkix" in cleaned_text or "certificate" in cleaned_text:
        root_lines.append(
            "Certificate validation failure caused integration failures in production."
        )

    if "scheduler" in cleaned_text and "payload" in cleaned_text:
        root_lines.append(
            "Scheduler payload processing failures impacted ODC integration."
        )

    if "permission" in cleaned_text:
        root_lines.append(
            "Missing permissions caused system functionality failure."
        )

    if "path" in cleaned_text:
        root_lines.append(
            "Incorrect path configuration caused transaction failures."
        )

    if not root_lines:
        useful_lines = []

        for line in clean_noise(combined).splitlines():
            line = normalize(line)

            if line:
                useful_lines.append(line)

        root_lines = useful_lines[:3]

    return bulletize(root_lines)


# -----------------------------
# Resolution
# -----------------------------
def build_resolution(resolution_notes):
    if not resolution_notes:
        return ""

    resolution_lines = []

    for line in resolution_notes.splitlines():
        lower = line.lower()

        # Skip cause lines → already used in root cause
        if (
            "cause:" in lower
            or "root cause:" in lower
            or "reason:" in lower
        ):
            continue

        # Skip junk
        if any(x in lower for x in [
            "thanks",
            "thank you",
            "hello",
            "waiting for update"
        ]):
            continue

        cleaned = normalize(line)

        if cleaned:
            resolution_lines.append(cleaned)

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

    # Actual Snow columns
    short_desc = get_field_value(row, "short description")
    description = get_field_value(row, "description")
    work_notes = get_field_value(row, "work notes")
    additional_comments = get_field_value(row, "additional comments")
    resolution_notes = get_field_value(row, "resolution notes")

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
