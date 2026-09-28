def generate_changelog(commits: list) -> str:
    categories = {
        "Breaking Changes": [],
        "Features": [],
        "Fixes": [],
        "Refactoring & Improvements": [],
        "Other": []
    }

    for commit in commits:
        commit_hash: str = commit['hash']
        msg: str = commit['message']

        if "breaking change:" in msg.lower() or "!:" in msg:
            categories["Breaking Changes"].append(f"- {msg} (`{commit_hash}`)")
        elif msg.startswith("feat"):
            categories["Features"].append(f"- {msg} (`{commit_hash}`)")
        elif msg.startswith("fix"):
            categories["Fixes"].append(f"- {msg} (`{commit_hash}`)")
        elif msg.startswith(("refactor", "perf", "style")):
            categories["Refactoring & Improvements"].append(f"- {msg} (`{commit_hash}`)")
        else:
            categories["Other"].append(f"- {msg} (`{commit_hash}`)")

    changelog_lines = ["## What's Changed\n"]
    for cat, items in categories.items():
        if items:
            changelog_lines.append(f"### {cat}")
            changelog_lines.extend(items)
            changelog_lines.append("")

    return "\n".join(changelog_lines).strip()