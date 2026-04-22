import re

# ---------------- CLEAN ---------------- #

def clean_text(text):
    if not text:
        return ""

    # remove timestamps
    text = re.sub(r"\d{4}-\d{2}-\d{2}.*?-", "", text)

    # remove names
    text = re.sub(r"[A-Za-z]+\s+[A-Za-z]+\s*\(.*?\)", "", text)

    # remove attachments
    text = re.sub(r"Attachment:.*", "", text, flags=re.I)

    return text


def split_lines(text):
    return [l.strip() for l in text.split("\n") if l.strip()]


# ---------------- KEYWORD DETECTION ---------------- #

def contains_any(line, keywords):
    return any(k.lower() in line.lower() for k in keywords)


# ---------------- ROOT CAUSE ---------------- #

def build_root_cause(work_notes):
    text = clean_text(work_notes)
    lines = split_lines(text)

    causes = []
    permissions = []
    system = []

    for l in lines:
        if contains_any(l, ["permission", "acl", "access"]):
            permissions.append(l)
        elif contains_any(l, ["blocked", "validator", "delegate"]):
            system.append(l)
        else:
            causes.append(l)

    bullets = []

    if permissions:
        bullets.append(
            "- The issue is primarily caused by access control restrictions, where required permissions are not granted for the affected objects."
        )

    if system:
        bullets.append(
            "- System-level restrictions such as validators or OOTB delegates are preventing the expected functionality."
        )

    if causes:
        bullets.append(
            "- The functionality is not available in the current context due to system design limitations or configuration gaps."
        )

    if not bullets:
        bullets.append("- The issue is caused by a system limitation requiring further validation.")

    return "\n".join(bullets)


# ---------------- TECHNICAL ANALYSIS ---------------- #

def build_l2_analysis(comments):
    text = clean_text(comments)
    lines = split_lines(text)

    validation = []
    findings = []
    vendor = []

    for l in lines:
        if contains_any(l, ["validated", "tested", "verified"]):
            validation.append(l)
        elif contains_any(l, ["ptc", "vendor", "case"]):
            vendor.append(l)
        else:
            findings.append(l)

    bullets = []

    if validation:
        bullets.append(
            "- The issue was reproduced and validated across multiple scenarios to confirm consistent behavior."
        )

    if findings:
        bullets.append(
            "- Analysis confirms that the functionality behaves differently based on permission levels and object states."
        )

    if vendor:
        bullets.append(
            "- Vendor engagement has been initiated, and the issue is under review for a permanent fix in future releases."
        )

    bullets.append(
        "- Current behavior aligns with system constraints and requires controlled configuration changes for resolution."
    )

    return "\n".join(bullets)


# ---------------- RESOLUTION ---------------- #

def build_resolution(resolution_text):
    text = clean_text(resolution_text)

    bullets = []

    if "azure" in text.lower():
        bullets.append(
            "- A feature/bug has been logged in Azure DevOps to address the identified limitation."
        )

    if "permission" in text.lower():
        bullets.append(
            "- Granting appropriate permissions enables the required functionality under supported scenarios."
        )

    bullets.append(
        "- The incident has been closed based on current system behavior and agreed resolution."
    )

    return "\n".join(bullets)


# ---------------- MERGE ---------------- #

def merge_with_user_input(auto_text, user_text):
    if user_text and user_text.strip():
        return user_text
    return auto_text
