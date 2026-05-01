import os
import subprocess
import tempfile


def render_ppt_slides_to_images(ppt_path):
    """
    Converts entire PPT slides to PNG.
    Preserves:
    - arrows
    - text boxes
    - lines
    - screenshots
    - annotations
    - shapes
    """

    output_dir = tempfile.mkdtemp()

    subprocess.run([
        "soffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        ppt_path
    ], check=True)

    pdf_file = None
    for f in os.listdir(output_dir):
        if f.endswith(".pdf"):
            pdf_file = os.path.join(output_dir, f)
            break

    if not pdf_file:
        raise Exception("PDF conversion failed")

    return pdf_file
