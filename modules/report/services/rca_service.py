from modules.common.utils.text_cleaner import clean_description
from modules.common.utils.parsers import extract_azure_id
from modules.report.domain.rca_generator import generate_rca


def build_rca(data):

    cleaned = {
        "short_description": data.get("short_description"),
        "description": clean_description(data.get("description")),
        "work_notes": data.get("work_notes"),
        "resolution": data.get("resolution"),
        "azure_bug": extract_azure_id(data.get("resolution"))
    }

    return generate_rca(cleaned)
