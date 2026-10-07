from pathlib import Path
from packaging.version import Version

from .bump import bump_config_version, bump_git_tag
from .check import get_config_tag, parse_highest_version, is_all_config_match
from .git import (
    fetch_remote_tags,
    get_local_tags,
    check_remote_connection,
    has_remote,
    get_remote_tags,
    get_remote_tag_commit_hash,
    is_commit_in_current_branch, get_tag_commit_hash
)
from ..exception import GitRemoteError, ConfigFileVersionError
from ..models import SyncRequest
from ..utils import get_config_version

def sync_version(
        request: SyncRequest,
        highest_local_tag:Version|None,
        config_tag: Version,
        config_version: dict[Path,Version]
) -> None:

    if request.to_git:
        if highest_local_tag:
            for config_path in config_version.keys():
                bump_config_version(highest_local_tag, config_path)
                print(f"Synced {config_path.name} version to match Git tag v{highest_local_tag}.")
        else:
            raise RuntimeError("No git tag found on local.")

    elif request.to_config and highest_local_tag:
        bump_git_tag(config_tag, message=f"Sync git tag to v{config_tag}.")
        print(f"Synced Git tag to match config version v{config_tag}.")

    else:
        if highest_local_tag:
            target_version = max(config_tag, highest_local_tag)
        else:
            target_version = config_tag

        all_config_match = is_all_config_match(config_version)
        if highest_local_tag and (not all_config_match or highest_local_tag > config_tag):
            for config_path in config_version.keys():
                bump_config_version(target_version, config_path)
                print(f"Synced {config_path.name} version to match v{target_version}.")

        elif highest_local_tag and highest_local_tag < config_tag:
            bump_git_tag(target_version)
            print(f"Synced Git tag to match with v{target_version}.")

        else:
            return

        print(f"\nSynced workspace to highest version v{target_version}.")

def sync_remote(remote_name: str) -> None:
    # Validate remote
    check_remote_connection(remote_name)
    if not has_remote(remote_name):
        raise GitRemoteError(
            f"Git remote '{remote_name}' was not found.\n"
            f"Hint: Run 'git remote -v' to view existing remotes, or add it using 'git remote add {remote_name} <url>'."
        )

    # Is remote tag missing in local?
    # If highest remote tag already in local, no need to sync
    remote_tags = get_remote_tags(remote_name)
    highest_remote_tag = parse_highest_version(remote_tags) if remote_tags else None
    if not highest_remote_tag:
        return

    local_tags = get_local_tags()
    tag_name = f"v{highest_remote_tag}"
    in_local = tag_name in local_tags

    commit_hash = (
        get_tag_commit_hash(tag_name) if in_local
        else get_remote_tag_commit_hash(tag_name, remote_name)
    )

    if not is_commit_in_current_branch(commit_hash):
        raise RuntimeError(
            f"Error: Commit '{commit_hash[:7]}' associated with tag '{tag_name}' "
            f"is not integrated into your current branch.\n"
            f"Hint: Please run 'git pull' or merge the target branch before syncing version."
        )

    if not in_local:
        fetch_remote_tags(remote_name)


def do_sync(request: SyncRequest) -> None:
    ## Auto fetch git tag If using remote argument
    if request.remote_name is not None:
        sync_remote(request.remote_name)

    config_list = get_config_version(request.config_name)
    local_tags = get_local_tags()

    highest_local_tag = parse_highest_version(local_tags)

    unique_version = {}
    for config_path, ver in config_list.items():
        unique_version[get_config_tag(config_path)] = ver

    config_tag = parse_highest_version(set(unique_version.values()))
    if not config_tag:
        raise ConfigFileVersionError(
            f"No config tag found."
        )

    if not local_tags:
        bump_git_tag(config_tag)
        print("No local git tag found.")
        print(f"Synced version from config file. Created tag: v{config_tag}")
        return

    elif config_tag == highest_local_tag and len(unique_version) == 1:
        print(f"Already in sync at (v{config_tag})")
        return

    else:
        sync_version(request, highest_local_tag, config_tag, config_list)