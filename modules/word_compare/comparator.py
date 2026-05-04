from docx import Document
from docx.shared import RGBColor
from copy import deepcopy
import hashlib
import io


def highlight_run(run, color="yellow"):
    if color == "yellow":
        run.font.highlight_color = 7
    elif color == "red":
        run.font.color.rgb = RGBColor(255, 0, 0)
    elif color == "green":
        run.font.color.rgb = RGBColor(0, 128, 0)


def compare_paragraphs(old_doc, new_doc, output_doc):
    old_paras = old_doc.paragraphs
    new_paras = new_doc.paragraphs

    max_len = max(len(old_paras), len(new_paras))

    for i in range(max_len):
        if i >= len(old_paras):
            p = output_doc.add_paragraph()
            run = p.add_run(new_paras[i].text)
            highlight_run(run, "green")
            continue

        if i >= len(new_paras):
            continue

        if old_paras[i].text != new_paras[i].text:
            output_doc.paragraphs[i].clear()
            run = output_doc.paragraphs[i].add_run(new_paras[i].text)
            highlight_run(run, "yellow")


def compare_tables(old_doc, new_doc, output_doc):
    old_tables = old_doc.tables
    new_tables = new_doc.tables

    for t_idx in range(min(len(old_tables), len(new_tables))):
        old_table = old_tables[t_idx]
        new_table = new_tables[t_idx]
        out_table = output_doc.tables[t_idx]

        for r_idx in range(min(len(old_table.rows), len(new_table.rows))):
            for c_idx in range(min(len(old_table.rows[r_idx].cells),
                                   len(new_table.rows[r_idx].cells))):

                old_text = old_table.rows[r_idx].cells[c_idx].text
                new_text = new_table.rows[r_idx].cells[c_idx].text

                if old_text != new_text:
                    cell = out_table.rows[r_idx].cells[c_idx]
                    cell.text = new_text

                    for para in cell.paragraphs:
                        for run in para.runs:
                            highlight_run(run, "yellow")


def get_image_hashes(doc):
    hashes = []

    rels = doc.part.rels

    for rel in rels.values():
        try:
            # Skip external references
            if rel.is_external:
                continue

            if "image" in rel.target_ref.lower():
                img_data = rel.target_part.blob
                img_hash = hashlib.md5(img_data).hexdigest()
                hashes.append(img_hash)

        except Exception:
            # Skip problematic relationships
            continue

    return hashes


def compare_images(old_doc, new_doc, output_doc):
    old_images = set(get_image_hashes(old_doc))
    new_images = set(get_image_hashes(new_doc))

    added = new_images - old_images
    removed = old_images - new_images

    if added:
        p = output_doc.add_paragraph()
        run = p.add_run(
            f"New Images Added: {len(added)}"
        )
        highlight_run(run, "green")

    if removed:
        p = output_doc.add_paragraph()
        run = p.add_run(
            f"Images Removed: {len(removed)}"
        )
        highlight_run(run, "red")


def compare_documents(old_file, new_file, output_path):
    old_doc = Document(old_file)
    new_doc = Document(new_file)

    output_doc = deepcopy(old_doc)

    compare_paragraphs(old_doc, new_doc, output_doc)
    compare_tables(old_doc, new_doc, output_doc)
    compare_images(old_doc, new_doc, output_doc)

    output_doc.save(output_path)
