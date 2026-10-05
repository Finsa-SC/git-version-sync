from pathlib import Path
from packaging.version import Version

from .bump import bump_config_version, bump_git_tag
from .check import get_config_tag, parse_highest_version, is_all_config_match
from .git import fetch_remote_tags, is_branch_behind_remote, get_local_tags, check_remote_connection, has_remote
from ..exception import GitRemoteError
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

def do_sync(request: SyncRequest) -> None:
    ## Auto fetch git tag If using remote argument
    if request.remote_name is not None:
        if not has_remote(request.remote_name):
            raise GitRemoteError(
                f"Git remote '{request.remote_name}' was not found.\n"
                f"Hint: Run 'git remote -v' to view existing remotes, or add it using 'git remote add {request.remote_name} <url>'."
            )

        check_remote_connection(request.remote_name)
        fetch_remote_tags(request.remote_name)

        if is_branch_behind_remote():
            raise RuntimeError(
                "Your branch is behind remote commits. "
                "Please run `git pull` first before syncing version"
            )

    config_list = get_config_version(request.config_name)
    local_tags = get_local_tags()

    highest_local_tag = parse_highest_version(local_tags)

    unique_version = {}
    for config_path, ver in config_list.items():
        unique_version[get_config_tag(config_path)] = ver

    config_tag = max(unique_version.values())
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