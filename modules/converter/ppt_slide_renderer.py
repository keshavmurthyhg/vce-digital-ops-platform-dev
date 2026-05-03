import os
import time
import tempfile
import subprocess

from pdf2image import convert_from_path
from PIL import Image


# -----------------------------------
# Remove title/empty slides
# -----------------------------------
def should_skip_slide(img_path):
    try:
        img = Image.open(img_path).convert("RGB")

        width, height = img.size

        center = img.crop((
            width * 0.2,
            height * 0.2,
            width * 0.8,
            height * 0.8
        ))

        gray = center.convert("L")
        hist = gray.histogram()

        white_pixels = hist[255]
        total_pixels = sum(hist)

        white_ratio = white_pixels / total_pixels

        return white_ratio > 0.92

    except:
        return False


# -----------------------------------
# Clean PPT using LibreOffice UNO
# -----------------------------------
def clean_ppt_theme(input_ppt, output_ppt):
    """
    Opens PPT in LibreOffice and removes
    master/layout formatting
    """

    uno_script = f"""
import uno
import os
from com.sun.star.beans import PropertyValue

local_ctx = uno.getComponentContext()
resolver = local_ctx.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver",
    local_ctx
)

ctx = resolver.resolve(
    "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
)

smgr = ctx.ServiceManager
desktop = smgr.createInstanceWithContext(
    "com.sun.star.frame.Desktop",
    ctx
)

def to_url(path):
    return "file://" + os.path.abspath(path)

props = []

doc = desktop.loadComponentFromURL(
    to_url(r"{input_ppt}"),
    "_blank",
    0,
    tuple(props)
)

slides = doc.getDrawPages()

for i in range(slides.getCount()):
    slide = slides.getByIndex(i)

    try:
        slide.setMasterPage(None)
    except:
        pass

doc.storeAsURL(
    to_url(r"{output_ppt}"),
    tuple(props)
)

doc.close(True)
"""

    script_file = os.path.join(
        tempfile.gettempdir(),
        "clean_ppt_theme.py"
    )

    with open(script_file, "w") as f:
        f.write(uno_script)

    # Start LibreOffice listener
    subprocess.Popen([
        "soffice",
        "--headless",
        "--accept=socket,host=localhost,port=2002;urp;"
    ])

    time.sleep(5)

    subprocess.run(
        ["python3", script_file],
        check=True
    )


# -----------------------------------
# Convert PPT → images
# -----------------------------------
def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        cleaned_ppt = os.path.join(
            temp_dir,
            "cleaned.pptx"
        )

        # Step 1 → remove theme
        clean_ppt_theme(
            ppt_path,
            cleaned_ppt
        )

        # Step 2 → convert to PDF
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            cleaned_ppt,
            "--outdir",
            temp_dir
        ], check=True)

        pdf_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.endswith(".pdf")
        ]

        if not pdf_files:
            raise Exception("PDF not generated")

        pdf_path = pdf_files[0]

        pages = convert_from_path(
            pdf_path,
            dpi=200
        )

        final_images = []

        for i, page in enumerate(pages):
            img_path = os.path.join(
                temp_dir,
                f"slide_{i+1}.png"
            )

            page.save(img_path)

            if should_skip_slide(img_path):
                print(f"Skipping slide {i+1}")
                continue

            final_images.append(img_path)

        return final_images

    except Exception as e:
        print(f"PPT processing failed: {e}")
        return []
