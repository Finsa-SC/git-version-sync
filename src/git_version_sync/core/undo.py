from packaging.version import Version, InvalidVersion

from git_version_sync.core.check import parse_highest_version
from git_version_sync.core.git import (
    delete_tag,
    delete_remote_tag,
    get_tag_commit,
    get_head_commit,
    reset_soft_head,
    get_remote_tags, get_local_tags, has_remote
)
from git_version_sync.exception import GitRemoteError, GitVersionSyncError
from git_version_sync.models import UndoRequest
from git_version_sync.utils import get_config_version


def get_previous_version(version_list: set[str]) -> Version|None:
    parsed_versions = []

    for ver in version_list:
        try:
            parsed_versions.append(Version(ver.lstrip("v")))

        except InvalidVersion:
            continue

    sorted_tags = sorted(parsed_versions)

    if len(sorted_tags) <= 1:
        return None
    return sorted_tags[-2]

def do_undo(request: UndoRequest) -> None:
    from git_version_sync.core.bump import bump_config_version

    # Validate remote if use remote argument
    if request.remote_name is not None:
        if not has_remote(request.remote_name):
            raise GitRemoteError(f"No remote repository found for {request.remote_name}.")

    config_version = get_config_version(request.config_name)
    local_tags = get_local_tags()
    latest_tag = parse_highest_version(local_tags)

    if latest_tag is None:
        raise GitVersionSyncError("No local tag found.")

    target_tag = Version(request.undo_tag.lstrip('v')) if request.undo_tag else latest_tag
    is_latest = (target_tag == latest_tag)

    previous_version = get_previous_version(local_tags)

    # User confirmation
    if not request.force:
        target_str = f"v{target_tag}"
        remote_info = " and REMOTE" if request.remote_name else ""
        confirm = input(f"Are you sure you want to undo tag {target_str} (LOCAL{remote_info}) and revert to v{previous_version}? [y/N]: ").strip().lower()
        print()
        if confirm not in ["y", "yes", "yeah", "ye", "yee"]:
            print("Undo operation canceled.")
            return

    if is_latest:
        tag_commit = get_tag_commit(f"v{target_tag}")
        head_commit = get_head_commit()

        if tag_commit and tag_commit == head_commit:
            reset_soft_head()
            print("Reset last git commit.")

        if previous_version:
            for config_path in config_version.keys():
                bump_config_version(previous_version, config_path)

                print(f"Reverted {config_path.name} version to 'v{previous_version}'.")
        else:
            print(f"Skipped config revert (no previous tag found).")

    else:
        print(f"Tag v{target_tag} is not the latest version (current: v{latest_tag}).")
        print(f"Skipped resetting config and git commit to preserve history.")

    if request.remote_name:
        if target_tag not in get_remote_tags(request.remote_name):
            print(f"Skipped remote tag deletion (tag 'v{target_tag}' not found on remote).")
        else:
            delete_remote_tag(target_tag, request.remote_name)
            print(f"Deleted remote tag 'v{target_tag}'.")

    delete_tag(target_tag)
    print(f"Deleted local tag 'v{target_tag}'.")

    # Check deleted tag in remote
    remote_tags = get_remote_tags()
    if not request.remote_name and (f"v{target_tag}" in remote_tags or str(target_tag) in remote_tags):
        print(f"Note: v{target_tag} still exists on remote. Run with '-r' to delete it from remote.")

    print(f"\nSuccessfully reverted version from 'v{latest_tag}' -> 'v{previous_version}'")