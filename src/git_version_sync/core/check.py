import subprocess, tomllib
from pathlib import Path

from packaging.version import Version

from git_version_sync.config_handlers import get_config_parser
from git_version_sync.core.git import get_remote_tags, fetch_remote_tags
from git_version_sync.networks import check_network
from git_version_sync.utils import get_config_path

def get_local_tags() -> set[str]:
    command = ["git", "tag", "--list"]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    tags = {tag for tag in result.stdout.strip().splitlines()}

    return tags

def parse_highest_verion(tags: set[str]) -> Version|None:
    valid_version = []
    for tag in tags:
        try:
            clean_tag = tag.removeprefix("v")
            valid_version.append(Version(clean_tag))
        except Exception:
            continue

    return max(valid_version) if valid_version else None

def get_config_tag(config_name: Path|None=None) -> Version:
    config_path = get_config_path(config_name)

    config_parser = get_config_parser(config_path)
    config_tag = config_parser.get_version()

    return config_tag

def get_missing_local_tags(remote_tags: set[str], local_tags: set[str]) -> set[str]:
    missing_in_local = remote_tags - local_tags

    return missing_in_local

def get_missing_remote_tags(remote_tags: set[str], local_tags: set[str]) -> set[str]:
    missing_in_remote = local_tags - remote_tags

    return missing_in_remote

def do_check(config_name: Path|None, no_fetch: bool=False) -> str:
    config_tag = get_config_tag(config_name)
    local_tags = get_local_tags()

    highest_local_version = parse_highest_verion(local_tags)
    if highest_local_version is None:
        return "No local tags found."

    if no_fetch:
        if config_tag == highest_local_version:
            return f"Version is synchronized with highest local tag (v{config_tag})"
        else:
            return (
                f"Version mismatch\n"
                f"Git Local: {highest_local_version or 'unknown'}\n"
                f"Config:    {config_tag}\n"
            )

    check_network()
    fetch_remote_tags()

    remote_tags = get_remote_tags()

    output = []

    highest_remote = parse_highest_verion(remote_tags)

    missing_in_local = get_missing_local_tags(remote_tags, local_tags)
    missing_in_remote = get_missing_remote_tags(remote_tags, local_tags)

    # Check if local version match but missing from remote
    if highest_local_version == config_tag and (missing_in_remote or missing_in_local):
        status = "behind" if highest_remote > highest_local_version else "ahead of"
        output.append(f"Config matches local tag (v{config_tag}), but local is {status} remote!")

    elif highest_local_version == config_tag:
        output.append(f"Version is synchronized with highest local tag (v{config_tag})")

    else:
        output.append(
            f"Version mismatch\n"
            f"Git Local: {highest_local_version or 'unknown'}\n"
            f"Config:    {config_tag}\n"
            f"Remote:    {highest_remote or 'unknown'}"
        )

    if missing_in_remote:
        output.append("Tag(s) available locally but missing in remote:")
        for tag in sorted(missing_in_remote):
            output.append(f"  - {tag}")
        output.append("  (Run 'git-version-sync push' to sync)")
        output.append("")

    if missing_in_local:
        output.append(f"New tag(s) found from remote: ")
        for tag in sorted(missing_in_local):
            output.append(f"  - {tag}")
        output.append("")

    return "\n".join(output)

if __name__ == "__main__":
    print(do_check())