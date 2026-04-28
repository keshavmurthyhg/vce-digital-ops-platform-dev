def generate_rca(data):

    problem = data.get("short_description", "")

    root = data.get("work_notes", "")
    resolution = data.get("resolution", "")

    return {
        "problem": problem,
        "analysis": root,
        "resolution": resolution
    }
