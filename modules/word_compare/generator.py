import os
import tempfile
from datetime import datetime

from modules.word_compare.comparator import compare_documents


def generate_output_file(
    old_file,
    new_file
):
    old_file.seek(0)
    new_file.seek(0)

    base_name = os.path.splitext(
        old_file.name
    )[0]

    current_date = datetime.now().strftime(
        "%d%b%Y"
    )

    output_filename = (
        f"{base_name}"
        f"_Diff-Highlighted_"
        f"{current_date}.docx"
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".docx"
    ) as tmp:
        output_path = tmp.name

    compare_documents(
        old_file,
        new_file,
        output_path
    )

    with open(output_path, "rb") as f:
        file_bytes = f.read()

    os.remove(output_path)

    return {
        "file_bytes": file_bytes,
        "file_name": output_filename
    }
