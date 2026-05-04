import os
import tempfile

from datetime import datetime, timezone, timedelta
from modules.word_compare.comparator import compare_documents


def generate_output_file(
    old_file,
    new_file,
    progress_callback=None
):
    old_file.seek(0)
    new_file.seek(0)

    # -----------------------------
    # Step 1: Prepare filenames
    # -----------------------------
    if progress_callback:
        progress_callback(
            10,
            "Preparing output file..."
        )

    base_name = os.path.splitext(
        old_file.name
    )[0]

    # IST timezone (UTC +5:30)
    ist_timezone = timezone(
        timedelta(hours=5, minutes=30)
    )

    current_date = datetime.now(
        ist_timezone
    ).strftime("%d%b%Y")

    output_filename = (
        f"{base_name}"
        f"_Diff-Highlighted_"
        f"{current_date}.docx"
    )

    # -----------------------------
    # Step 2: Create temp file
    # -----------------------------
    if progress_callback:
        progress_callback(
            25,
            "Creating temporary workspace..."
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".docx"
    ) as tmp:
        output_path = tmp.name

    # -----------------------------
    # Step 3: Compare documents
    # -----------------------------
    if progress_callback:
        progress_callback(
            50,
            "Comparing documents and detecting changes..."
        )

    compare_documents(
        old_file,
        new_file,
        output_path
    )

    # -----------------------------
    # Step 4: Read generated file
    # -----------------------------
    if progress_callback:
        progress_callback(
            80,
            "Preparing final document..."
        )

    with open(output_path, "rb") as f:
        file_bytes = f.read()

    # -----------------------------
    # Step 5: Cleanup
    # -----------------------------
    if progress_callback:
        progress_callback(
            95,
            "Cleaning temporary files..."
        )

    os.remove(output_path)

    if progress_callback:
        progress_callback(
            100,
            "Completed successfully."
        )

    return {
        "file_bytes": file_bytes,
        "file_name": output_filename
    }
