from pathlib import Path
from packaging.version import Version

from .bump import bump_config_version, bump_git_tag
from .check import get_config_tag, parse_highest_version, is_all_config_match
from .git import fetch_remote_tags, is_branch_behind_remote, get_local_tags
from ..networks import check_network
from ..utils import get_config_version

def sync_version(
        to_git: bool,
        to_config: bool,
        highest_local_tag:Version|None,
        config_tag: Version,
        config_version: dict[Path,Version]
) -> None:

    if to_git:
        if highest_local_tag:
            for config_path in config_version.keys():
                bump_config_version(highest_local_tag, config_path)
                print(f"Synced {config_path.name} version to match Git tag v{highest_local_tag}")
        else:
            raise RuntimeError("No git tag found on local.")

    elif to_config and highest_local_tag:
        bump_git_tag(config_tag, message=f"Sync git tag to v{config_tag}")
        print(f"Synced Git tag to match config version v{config_tag}")

    else:
        if highest_local_tag:
            target_version = max(config_tag, highest_local_tag)
        else:
            target_version = config_tag

        all_match = is_all_config_match(config_version)
        if highest_local_tag and (not all_match or highest_local_tag > config_tag):
            for config_path in config_version.keys():
                bump_config_version(target_version, config_path)

        elif highest_local_tag and highest_local_tag < config_tag:
            bump_git_tag(target_version)

        else:
            return

        print(f"Synced workspace to highest version v{target_version}")

def do_sync(to_git: bool=False, to_config: bool=False, config_name: Path|None=None) -> None:
    check_network()
    fetch_remote_tags()

    if is_branch_behind_remote():
        raise RuntimeError(
            "Your branch is behind remote commits. "
            "Please run `git pull` first before syncing version"
        )

    config_list = get_config_version(config_name)
    local_tags = get_local_tags()

    highest_local_tag = parse_highest_version(local_tags)

    unique_version = {}
    for config_path, ver in config_list.items():
        unique_version[get_config_tag(config_path)] = ver

    config_tag = max(unique_version.values())
    if not local_tags:
        bump_git_tag(config_tag)
        print(f"Synced version from config file. Created tag: v{config_tag}")

    if config_tag == highest_local_tag and len(unique_version) == 1:
        print(f"Already in sync at (v{config_tag})")
        return

    sync_version(to_git, to_config, highest_local_tag, config_tag, config_list)