from packaging.version import Version

from git_version_sync.core.bump import bump_config_version
from git_version_sync.core.check import get_local_tags, parse_highest_verion
from git_version_sync.core.git import (
    fetch_remote_tags,
    delete_tag,
    delete_remote_tag,
    get_tag_commit,
    get_head_commit,
    reset_soft_head,
    get_remote_tags
)

def get_previous_version(version_list: set[str]) -> Version|None:
    parsed_versions = [Version(ver.lstrip("v")) for ver in version_list]

    sorted_tags = sorted(parsed_versions)

    if len(sorted_tags) <= 1:
        return None
    return sorted_tags[-2]

def do_undo(tag: str|None=None, remote:bool=False, force:bool=False) -> None:
    local_tags = get_local_tags()
    latest_tag = parse_highest_verion(local_tags)

    if latest_tag is None:
        raise RuntimeError("No local tag found.")

    target_tag = Version(tag.lstrip('v')) if tag else latest_tag
    is_latest = (target_tag == latest_tag)

    if is_latest:
        tag_commit = get_tag_commit(f"v{target_tag}")
        head_commit = get_head_commit()

        confirm = input("Are you sure you want to undo tag {target_str} (LOCAL{remote_info})? [y/N]: ").strip().lower()
        if confirm not in ["y", "yes", 'yeah', 'ye', 'yee']:
            print("Undo operation canceled.")
            return

        if tag_commit and tag_commit == head_commit:
            reset_soft_head()
            print("Reset last git commit.")

        previous_version = get_previous_version(local_tags)

        if previous_version:
            bump_config_version(previous_version)
            print(f"Reverted pyproject.toml version to v{previous_version}")
        else:
            print("Skipped pyproject.toml revert (no previous tag found).")

    else:
        print(f"Tag v{target_tag} is not the latest version (current: v{latest_tag}).")
        print("Skipped resetting pyproject.toml and git commit to preserve history.")

    if remote:
        delete_remote_tag(target_tag)
        print(f"Deleted remote tag v{target_tag}")

    delete_tag(target_tag)
    print(f"Deleted local tag v{target_tag}")

    # Check deleted tag in remote
    remote_tags = get_remote_tags()
    if not remote and (f"v{target_tag}" in remote_tags or str(target_tag) in remote_tags):
        print(f"Note: v{target_tag} still exists on remote. Run with '-r' to delete it from remote.")