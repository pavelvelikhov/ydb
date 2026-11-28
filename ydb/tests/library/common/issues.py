import re


RBO_FALLBACK_PREFIX = "Compilation with the new RBO failed: "


def issues_without_rbo_fallback(issues):
    """Filter only the automatic fallback note from protobuf-JSON issue trees."""
    result = []
    for issue in issues:
        is_info = issue.get("severity") == 3
        if is_info and issue.get("issue_code", 0) == 0 and issue.get("message", "").startswith(RBO_FALLBACK_PREFIX):
            continue
        filtered = dict(issue)
        if "issues" in issue:
            filtered["issues"] = issues_without_rbo_fallback(issue["issues"])
            if is_info and issue["issues"] and not filtered["issues"]:
                continue
        result.append(filtered)
    return result


def text_without_rbo_fallback(text):
    """The compile actor flattens this informational note onto a single line."""
    return re.sub(r"^[ \t]*<main>: Info: " + re.escape(RBO_FALLBACK_PREFIX) + r"[^\r\n]*(?:\r?\n|$)",
                  "", text, flags=re.MULTILINE)
