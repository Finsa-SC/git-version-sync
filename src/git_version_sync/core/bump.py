import subprocess, re
from packaging.version import Version

from .git import commit_config_change, push_to_remote, create_github_release
from .check import parse_highest_verion, get_local_tags, get_config_tag, get_remote_tags, get_missing_local_tags
from ..config_handlers import get_config_parser
from ..models import BumpRequest, BumpType
from ..networks import check_network
from ..utils import get_config_path

def bump_git_tag(new_version: Version, message: str|None = None) -> None:
    msg = message if message and message.strip() else f"bump version to v{new_version}"
    command = [
        'git',
        'tag',
        '-a', f'v{new_version}',
        '-m', msg
    ]

    subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

def bump_config_version(new_version: Version) -> None:
    config_path = get_config_path()

    config_parser = get_config_parser(config_path)
    config_parser.update_version(new_version)

def bump_version(
        request: BumpRequest,
        new_version: Version,
) -> None:
    bump_config_version(new_version)
    print(f"Updated {get_config_path().name} to v{new_version}")

    commit_config_change(new_version)
    print(f"Committed changes: 'bump version to v{new_version}'")

    bump_git_tag(new_version, request.tag_message)
    print(f"Created Git tag v{new_version}")

    if request.push:
        push_to_remote(new_version)
        print("Pushed commit and tag to remote")

    if request.release is not None:
        create_github_release(new_version, request.release, request.draft)
        draft_str = " (Draft)" if request.draft else ""
        print(f"Created GitHub Release v{new_version}{draft_str}")

def format_dry_run_output(request: BumpRequest, new_version: Version) -> str:
    output: list[str] = [
        f"Would update {get_config_path(request.config_path)} to v{new_version} (DRY RUN)",
        f"Would commit changes: 'bump version to v{new_version}' (DRY RUN)",
        f"Would create Git tag v{new_version} (DRY RUN)",
    ]

    if request.push:
        output.append(f"Would push commit and tag to remote (DRY RUN)")

    if request.release:
        output.append(f"Would create GitHub Release v{new_version} (DRY RUN)")

    output.append(f"\nDry run complete for v{new_version} (no changes made)")

    return "\n".join(output)

def get_new_major(version: Version) -> str:
    return f"{version.major + 1}.0.0"

def get_new_minor(version: Version) -> str:
    return f"{version.major}.{version.minor + 1}.0"

def get_new_patch(version: Version):
    return f"{version.major}.{version.minor}.{version.micro + 1}"

def calculate_next_version(base_version: Version, bump_type: BumpType) -> str:
    match bump_type:
        case "major":
            return get_new_major(base_version)
        case "minor":
            return get_new_minor(base_version)
        case "patch":
            return get_new_patch(base_version)

def do_bump(request: BumpRequest):
    if request.push:
        check_network()

    local_tags = get_local_tags()
    remote_tags = get_remote_tags()

    config_tag = get_config_tag()
    highest_local_tag = parse_highest_verion(local_tags)
    highest_overall_tag = parse_highest_verion(local_tags | remote_tags)

    if config_tag != highest_local_tag and not request.force:
        raise RuntimeError(
            f"Version mismatch detected!\n"
            f"  Config: v{config_tag}\n"
            f"  Git   : v{highest_local_tag}\n"
            f"Run `git-version-sync sync` first or use `--force` to bypass."
        )

    missing_in_local = get_missing_local_tags(remote_tags, local_tags)
    if missing_in_local and not request.force:
        missing_str = ", ".join(f"{ver}" for ver in missing_in_local)
        raise RuntimeError(
            f"Remote repository has newer tag(s) missing locally: {missing_str}\n"
            f"Run `git-version-sync sync` first or use `--force` to bump from the highest remote tag."
        )

    base_version = max(
        v
        for v in [config_tag, highest_local_tag, highest_overall_tag]
        if v is not None
    )

    new_version = Version(calculate_next_version(base_version, request.bump_type))

    # Dry run
    if request.dry_run:
        return format_dry_run_output(request, new_version)

    bump_version(
        request,
        new_version
    )

    return f"\nSuccess bump version to v{new_version}"