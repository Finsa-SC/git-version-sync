from pathlib import Path

from packaging.version import Version

from git_version_sync.config_handlers import get_config_parser
from git_version_sync.core.git import get_remote_tags, get_local_tags, check_remote_connection
from git_version_sync.utils import get_config_version

def parse_highest_version(tags: set[str|Version]) -> Version | None:
    valid_version = []
    for tag in tags:
        try:
            if isinstance(tag, str):
                clean_tag = tag.removeprefix("v")
                valid_version.append(Version(clean_tag))
            else:
                valid_version.append(tag)
        except Exception:
            continue

    return max(valid_version, key=lambda ver: Version(ver.lstrip("v"))) if valid_version else None

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
        config_out.append(f"{str(config.name):<24}: v{ver}")
    config_str = "\n".join(config_out)
    local_highest_str = f"v{local_highest}" if local_highest else 'unknown'
    return (
        f"Version mismatch\n"
        f"Git Local\t\t: {local_highest_str}\n"
        f"{config_str}"
    )

def do_check(config_name: Path|None, no_fetch: bool=False, remote_name: str = "origin") -> str:
    local_tags = get_local_tags()
    remote_tags = get_remote_tags(remote_name)

    # Validate local tags
    highest_local_version = parse_highest_version(local_tags)
    if highest_local_version is None:
        return "No local tags found."

    config_version = get_config_version(config_name)
    all_match = is_all_config_match(config_version)
    config_tag = None
    if all_match:
        config_tag = next(iter(config_version.values()))

    # Offline check
    if no_fetch:
        if all_match:
            return (
                f"Version is synchronized with highest local tag (v{config_tag})\n"
                f"(Skipped remote fetch. Remote status may be out of date.)"
            )

        else:
            return get_config_mismatch_str(config_version, highest_local_version)

    # Online check
    check_remote_connection(remote_name)

    output = []

    highest_remote = parse_highest_version(remote_tags)

    missing_in_local = get_missing_in_local_tags(remote_tags, local_tags)
    missing_in_remote = get_missing_in_remote_tags(remote_tags, local_tags)

    if highest_local_version == config_tag:
        output.append(f"Version ({config_tag}) is synchronized with local tag 'v{config_tag}'.")

    else:
        highest_remote_str = f"v{highest_remote}" if highest_remote else 'unknown'

        config_msg = get_config_mismatch_str(config_version, highest_local_version)
        output.append("")
        output.append(config_msg)
        output.append(f"Remote\t\t\t: {highest_remote_str}")

    if missing_in_remote:
        output.append(f"\nPending Remote Sync ({remote_name}):")
        for tag in sorted(missing_in_remote):
            output.append(f"  - {tag}")

    if missing_in_local:
        output.append(f"\nNew tag(s) found on remote ({remote_name}): ")
        for tag in sorted(missing_in_local):
            output.append(f"  - {tag}")

    ## Warning and hint if local and remote tag is not valid
    if missing_in_local:
        output.append(
            f"\nWarning: Local version is behind remote."
            f"\nHint: Remote has newer tags/commits. Run 'git pull' (or 'git fetch --tags') before pushing local changes."
        )
    elif missing_in_remote:
        output.append("\nHint: Run 'git-version-sync push' to sync local tags to remote.")

    return "\n".join(output)