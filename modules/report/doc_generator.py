from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc
from modules.common.utils.text_cleaner import format_description
from modules.common.utils.links import extract_azure_id
from modules.report.domain.rca_generator import generate_rca


def enrich_data(data):
    notes = " ".join([
        str(data.get("resolution_notes", "")),
        str(data.get("work_notes", "")),
        str(data.get("comments", "")),
        str(data.get("additional_comments", ""))
    ])

    if not data.get("azure_bug"):
        data["azure_bug"] = extract_azure_id(notes)

    return data


def prepare_data(data):
    data = enrich_data(data)
    safe_data = data.copy()

    safe_data["description"] = format_description(data.get("description"))

    rca = generate_rca(data)
    safe_data["problem"] = rca["problem"]
    safe_data["analysis"] = rca["analysis"]
    safe_data["resolution"] = rca["resolution"]

    return safe_data


def generate_pdf(data, root=None, l2=None, res=None, images=None):
    data = prepare_data(data)

    # Always use latest RCA from prepare_data
    root = data.get("problem")
    l2 = data.get("analysis")
    res = data.get("resolution")

    return generate_pdf_doc(
        data=data,
        root=data.get("problem"),
        l2=data.get("analysis"),
        res=data.get("resolution")
        images=images or {}
    )


def generate_word_doc_wrapper(data, root=None, l2=None, res=None, images=None, ppt_data=None):
    data = prepare_data(data)

    root = data.get("problem")
    l2 = data.get("analysis")
    res = data.get("resolution")

    return generate_word_doc(
        data=data,
        root=data.get("problem"),
        l2=data.get("analysis"),
        res=data.get("resolution")
        images=images or {},
        ppt_data=ppt_data
    )
