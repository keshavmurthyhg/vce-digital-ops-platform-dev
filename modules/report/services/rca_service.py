from modules.report.utils.utils import format_description
from modules.common.utils.parsers import extract_azure_id
from modules.report.domain.rca_generator import generate_rca
import re
from modules.common.utils.formatters import safe_text


def extract_section(text, keyword):
    """
    Extract text after keyword until next keyword
    """
    if not text:
        return ""

    pattern = rf"{keyword}\s*:(.*?)(?=Issue:|Cause:|Resolution:|Validation:|$)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""


def clean_bullets(text):
    if not text:
        return ""

    lines = [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
    ]

    return "\n".join([f"• {line}" for line in lines])


def build_rca(row):
    """
    Build structured RCA from SNOW fields
    """

    problem = safe_text(
        row.get("short_description"),
        default=""
    )

    work_notes = safe_text(
        row.get("work_notes"),
        default=""
    )

    resolution_notes = safe_text(
        row.get("resolution_notes"),
        default=""
    )

    # Extract cause from resolution notes
    cause_from_resolution = extract_section(
        resolution_notes,
        "Cause"
    )

    # Extract resolution section
    resolution_fix = extract_section(
        resolution_notes,
        "Resolution"
    )

    # Extract validation section
    validation = extract_section(
        resolution_notes,
        "Validation"
    )

    # Root cause combines:
    # work notes summary + explicit cause
    root_parts = []

    if work_notes:
        root_parts.append(work_notes)

    if cause_from_resolution:
        root_parts.append(cause_from_resolution)

    root_cause = "\n".join(root_parts)

    # Resolution section combines:
    # resolution + validation
    resolution_parts = []

    if resolution_fix:
        resolution_parts.append(resolution_fix)

    if validation:
        resolution_parts.append(validation)

    resolution = "\n".join(resolution_parts)

    return {
        "problem": clean_bullets(problem),
        "analysis": clean_bullets(root_cause),
        "resolution": clean_bullets(resolution)
    }
