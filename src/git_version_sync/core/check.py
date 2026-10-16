from collections.abc import Iterable
from pathlib import Path

from packaging.version import Version

from git_version_sync.config_handlers import get_config_parser
from git_version_sync.core.git import get_remote_tags, get_local_tags, check_remote_connection, has_remote
from git_version_sync.utils import get_config_version, Color


def parse_highest_version(*items: Iterable[str]) -> str|None:
    tags = set().union(*items)
    version_map = {}
    for tag in tags:
        try:
            has_prefix = tag.startswith("v")
            version_map[Version(tag)] = {"version": tag, "has_prefix": has_prefix}
        except Exception:
            continue

    if not version_map:
        return None

    highest = max(version_map.keys())

    return version_map[highest]['version']

def get_config_tag(config_path: Path) -> Version:
    config_parser = get_config_parser(config_path)
    config_tag = config_parser.get_version()

    return config_tag

def get_missing_in_local_tags(remote_tags: set[str], local_tags: set[str]) -> set[str]:
    missing_in_local = remote_tags - local_tags

    return missing_in_local

def get_missing_in_remote_tags(remote_tags: set[str], local_tags: set[str]) -> set[str]:
    missing_in_remote = local_tags - remote_tags

    return missing_in_remote

def is_all_config_match(configs: dict[Path, Version]) -> bool:
    prev_ver = None
    for path, ver in configs.items():
        if prev_ver is None:
            prev_ver = ver

        else:
            if prev_ver != ver:
                return False
            prev_ver = ver

    return True

def get_config_mismatch_str(config_items: dict[Path,Version], local_highest: Version) -> str:
    config_out = []
    for config, ver in config_items.items():
        config_out.append(f"{str(config.name):<24}: {ver}")
    config_str = "\n".join(config_out)
    local_highest_str = f"{local_highest}" if local_highest else 'unknown'
    return (
        f"Version mismatch\n"
        f"Git Local\t\t: {local_highest_str}\n"
        f"{config_str}"
    )

# Return status code and description
def do_check(config_name: Path|None, no_fetch: bool=False, remote_name: str = "origin") -> tuple[int, str]:
    local_tags = get_local_tags()

    remote_tags = set()
    skip_remote = False
    # Check if remote is enable and skip remote if remote cannot be reach
    if not no_fetch:
        if not has_remote(remote_name):
            print(f"{Color.YELLOW}Warning: Remote '{remote_name}' not found. Skipping remote check.{Color.RESET}")
            skip_remote = True

        else:
            check_remote_connection(remote_name)
            remote_tags = get_remote_tags(remote_name)

    # Validate local tags
    highest_local_version = parse_highest_version(local_tags)
    if highest_local_version is None:
        return 1, "No local tags found."

    config_version = get_config_version(config_name)
    all_match = is_all_config_match(config_version)
    config_tag = None
    if all_match:
        config_tag = next(iter(config_version.values()))

    # Offline check
    if no_fetch or skip_remote:
        if Version(highest_local_version) == config_tag and all_match:
            return 0, (
                f"Version is synchronized with highest local tag ({config_tag})\n"
                f"(Skipped remote fetch. Remote status may be out of date.)"
            )

        else:
            return 1, get_config_mismatch_str(config_version, Version(highest_local_version))

    output = []

    highest_remote = f"{parse_highest_version(remote_tags)}" if remote_tags else "None (no remote configured)"

    missing_in_local = get_missing_in_local_tags(remote_tags, local_tags)
    missing_in_remote = get_missing_in_remote_tags(remote_tags, local_tags)

    # If highest local tag match with config version
    if Version(highest_local_version) == config_tag and not (missing_in_local or missing_in_remote):
        status_code = 0
        output.append(f"Version ({config_tag}) is synchronized with local tag '{highest_local_version}'.")

    else:
        status_code = 1
        config_msg = get_config_mismatch_str(config_version, Version(highest_local_version))
        output.append("")
        output.append(config_msg)

        if not skip_remote:
            highest_remote_str = highest_remote if highest_remote else 'unknown'
            output.append(f"Remote\t\t\t: {highest_remote_str}")

            if missing_in_remote:
                output.append(f"\nPending Remote Sync ({remote_name}):")
                for tag in sorted(missing_in_remote):
                    output.append(f"  - {tag}")

            if missing_in_local:
                output.append(f"\nNew tag(s) found on remote ({remote_name}): ")
                for tag in sorted(missing_in_local):
                    clean_tag = tag.removeprefix('v')
                    output.append(f"  - {clean_tag}")

            ## Warning and hint if local and remote tag is not valid
            if missing_in_local:
                output.append(
                    f"{Color.YELLOW}Warning: Local version is behind remote.{Color.RESET}"
                    f"{Color.BLUE}Hint: Remote has newer tags/commits. Run 'git pull' (or 'git fetch --tags') before pushing local changes.{Color.RESET}"
                )

            elif missing_in_remote:
                output.append(f"{Color.BLUE}\nHint: Run 'git-version-sync push' to sync local tags to remote.{Color.RESET}")

    return status_code, "\n".join(output)