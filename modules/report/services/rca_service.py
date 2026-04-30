from modules.report.utils.utils import format_description
from modules.common.utils.parsers import extract_azure_id
from modules.report.domain.rca_generator import generate_rca
import re
from modules.common.utils.formatters import safe_text


def normalize(text):
    if not text:
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()


def bullet(lines):
    seen = set()
    final = []

    for line in lines:
        line = normalize(line)

        if not line:
            continue

        if line.lower() in seen:
            continue

        seen.add(line.lower())
        final.append(f"• {line}")

    return "\n".join(final)


def build_problem(short_desc, description):
    short_desc = normalize(short_desc)
    description = normalize(description)

    problem_lines = []

    if short_desc:
        problem_lines.append(short_desc)

    # avoid duplicate problem statement
    if description and description.lower() != short_desc.lower():
        problem_lines.append(description)

    return bullet(problem_lines)


def build_root_cause(work_notes, comments, resolution_notes):
    combined = "\n".join([
        safe_text(work_notes, default=""),
        safe_text(comments, default=""),
        safe_text(resolution_notes, default="")
    ])

    lower_text = combined.lower()

    root_points = []

    # Certificate issue
    if "pkix" in lower_text or "certificate" in lower_text:
        root_points.append(
            "ODC integration failed due to certificate validation issues in production."
        )

    # Path/config issue
    if "incorrect path" in lower_text:
        root_points.append(
            "Incorrect integration path configuration caused transaction failures."
        )

    # Payload failure
    if "failed to process payload" in lower_text:
        root_points.append(
            "Scheduler payload processing failures impacted ODC integration."
        )

    # Missing/revision issue
    if "missing" in lower_text:
        root_points.append(
            "Required data/version mismatch caused processing failures."
        )

    # Generic error fallback
    if not root_points:
        error_matches = re.findall(
            r".*?(error|exception|failed).*?",
            combined,
            re.IGNORECASE
        )

        if error_matches:
            root_points.append(
                "System errors were identified during incident investigation."
            )

    return bullet(root_points)


def build_resolution(resolution_notes):
    resolution_notes = safe_text(
        resolution_notes,
        default=""
    )

    lower_text = resolution_notes.lower()

    resolution_points = []

    if "path was modified" in lower_text:
        resolution_points.append(
            "Integration path configuration was corrected."
        )

    if "restarted" in lower_text:
        resolution_points.append(
            "Relevant services were restarted after implementing the fix."
        )

    if "validated" in lower_text or "working fine" in lower_text:
        resolution_points.append(
            "Integration was validated successfully after applying the fix."
        )

    if "implemented in production" in lower_text:
        resolution_points.append(
            "Production fix was deployed successfully."
        )

    if "azure" in lower_text:
        resolution_points.append(
            "Azure defect was identified and tracked for permanent resolution."
        )

    if not resolution_points and resolution_notes:
        resolution_points.append(
            "Resolution steps were performed and service functionality was restored."
        )

    return bullet(resolution_points)


def build_rca(row):
    return {
        "problem": build_problem(
            row.get("short_description"),
            row.get("description")
        ),

        "analysis": build_root_cause(
            row.get("work_notes"),
            row.get("comments"),
            row.get("resolution_notes")
        ),

        "resolution": build_resolution(
            row.get("resolution_notes")
        )
    }
