from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc
from modules.report.utils.utils import format_description
from modules.report.utils.utils import extract_azure_id
from modules.report.utils.rca_generator import generate_rca

def enrich_data(data):
    print("===== DEBUG AZURE EXTRACTION =====")

    print("resolution_notes:", data.get("resolution_notes"))
    print("work_notes:", data.get("work_notes"))
    print("comments:", data.get("comments"))
    print("additional_comments:", data.get("additional_comments"))
    
    notes = " ".join([
        str(data.get("resolution_notes", "")),
        str(data.get("work_notes", "")),
        str(data.get("comments", "")),
        str(data.get("additional_comments", ""))
    ])
    
    
    if not data.get("azure_bug") or str(data.get("azure_bug")).strip() == "":
        data["azure_bug"] = extract_azure_id(notes)

    return data

def prepare_data(data):
    """
    Central place for all sanitization & formatting
    """
    data = enrich_data(data)
    safe_data = data.copy()
st.write("DEBUG BEFORE RCA:", data.get("short_description"))
    # existing logic
    safe_data["description"] = format_description(data.get("description"))

    # ✅ ADD RCA GENERATION
    rca = generate_rca(data)

    safe_data["problem"] = rca["problem"]
st.write("DEBUG AFTER RCA:", safe_data.get("problem"))
    safe_data["analysis"] = rca["analysis"]
    safe_data["resolution"] = rca["resolution"]

    return safe_data

def safe_images(images):
    if not isinstance(images, dict):
        return {"root": [], "l2": [], "res": []}
    return images

def generate_pdf(data, root, l2, res, images=None):
    images = safe_images(images)

    data = prepare_data(data)
    
    return generate_pdf_doc(
        data=data,
        root=root,
        l2=l2,
        res=res,
        images=images
    )

def generate_word_doc_wrapper(data, root, l2, res, images=None, ppt_data=None):
    images = safe_images(images)

    data = prepare_data(data)
    
    return generate_word_doc(
        data=data,
        root=root,
        l2=l2,
        res=res,
        images=images,
        ppt_data=ppt_data
    )

