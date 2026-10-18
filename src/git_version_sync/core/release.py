from typing import Iterable

from packaging.version import Version, InvalidVersion

from git_version_sync.core.git import get_commit_since_tag, create_github_release, is_tag_already_has_release
from git_version_sync.core.tags import get_previous_tag


def generate_release(
        release_tags: Iterable[str],
        local_tags: Iterable[str],
        notes: str = "",
        check_release: bool = False
) -> None:
    for target_tag in release_tags:
        # Skip non semver
        try:
            Version(target_tag)
        except InvalidVersion:
            continue

        # Skip creating release if tag already has release version
        if check_release and is_tag_already_has_release(target_tag):
            continue

        if notes.strip():
            change_log = notes
        else:
            prev_tag = get_previous_tag(Version(target_tag), set(local_tags))
            commits = get_commit_since_tag(prev_tag, target_tag)
            change_log = generate_changelog(commits)

        create_github_release(target_tag, change_log)
        print(f"Created GitHub Release for {target_tag}")

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