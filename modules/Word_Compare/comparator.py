import difflib
import pandas as pd

def compare_lists(old_list, new_list, section_name):
    results = []

    diff = difflib.ndiff(old_list, new_list)

    for line in diff:
        status = line[:2]
        text = line[2:]

        if status == "- ":
            results.append({
                "section": section_name,
                "type": "Removed",
                "content": text
            })

        elif status == "+ ":
            results.append({
                "section": section_name,
                "type": "Added",
                "content": text
            })

    return results


def compare_documents(old_doc, new_doc):
    results = []

    results.extend(
        compare_lists(
            old_doc["paragraphs"],
            new_doc["paragraphs"],
            "Paragraph"
        )
    )

    old_tables = [str(t["data"]) for t in old_doc["tables"]]
    new_tables = [str(t["data"]) for t in new_doc["tables"]]

    results.extend(
        compare_lists(
            old_tables,
            new_tables,
            "Table"
        )
    )

    return pd.DataFrame(results)
