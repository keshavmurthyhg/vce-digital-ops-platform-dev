from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc
from modules.common.utils.text_cleaner import format_description
from modules.common.utils.links import extract_azure_id
#from modules.common.formatters import safe_text

# ✅ USE NEW RCA SERVICE
from modules.report.services.rca_service import build_rca


def enrich_data(data):
    """
    Keep existing Azure handling intact
    """
    if not data.get("azure_bug"):
        data["azure_bug"] = "-"

    return data


def prepare_data(data):
    """
    Common preparation for UI/PDF/Word/Bulk
    """
    data = enrich_data(data)
    safe_data = data.copy()

    # Keep description formatting intact
    safe_data["description"] = format_description(
        data.get("description")
    )

    # ✅ SINGLE SOURCE OF TRUTH
    rca = build_rca(data)

    safe_data["problem"] = rca.get(
        "problem_statement",
        ""
    )

    safe_data["analysis"] = rca.get(
        "root_cause",
        ""
    )

    safe_data["resolution"] = rca.get(
        "resolution",
        ""
    )

    return safe_data


# ---------------- PDF ---------------- #
def generate_pdf(
    data,
    root=None,
    l2=None,
    res=None,
    images=None
):
    data = prepare_data(data)

    return generate_pdf_doc(
        data=data,
        root=data.get("problem"),
        l2=data.get("analysis"),
        res=data.get("resolution"),
        images=images or {}
    )


# ---------------- WORD ---------------- #
def generate_word_doc_wrapper(
    data,
    root=None,
    l2=None,
    res=None,
    images=None,
    ppt_data=None
):
    data = prepare_data(data)

    return generate_word_doc(
        data=data,
        root=data.get("problem"),
        l2=data.get("analysis"),
        res=data.get("resolution"),
        images=images or {},
        ppt_data=ppt_data
    )
