import re
from pathlib import Path

from packaging.version import Version

from .undo import do_undo
from .changelog import generate_changelog
from .git import commit_config_change, push_to_remote, create_github_release, get_commit_since_tag, clean_git_error, \
    bump_git_tag
from .check import parse_highest_version, get_local_tags, get_config_tag, get_remote_tags, get_missing_local_tags, \
    is_all_config_match, get_config_mismatch_str
from ..config_handlers import get_config_parser
from ..exception import GitCommandError, ConfigVersionMismatch
from ..models import BumpRequest, BumpType
from ..networks import check_network
from ..utils import get_config_version

def bump_config_version(new_version: Version, config_path: Path) -> None:
    config_parser = get_config_parser(config_path)
    config_parser.update_version(new_version)

def bump_version(
        request: BumpRequest,
        base_version: Version,
        new_version: Version,
        config_version: dict[Path,Version]
) -> bool:
    mutated_local = False

    try:
        for config_path in config_version.keys():
            bump_config_version(new_version, config_path)
            print(f"Updated {config_path.name} to v{new_version}")

        commit_config_change(new_version, config_version)
        print(f"Committed changes: 'bump version to v{new_version}'")

        bump_git_tag(new_version, request.tag_message)
        print(f"Created Git tag v{new_version}")

        mutated_local = True

        if request.push:
            push_to_remote(new_version)
            print("Pushed commit and tag to remote")

        if request.release is not None:
            if request.release.strip():
                change_log = request.release
            else:
                commits = get_commit_since_tag(base_version)
                change_log = generate_changelog(commits)

            create_github_release(new_version, change_log, request.draft)
            draft_str = " (Draft)" if request.draft else ""
            print(f"Created GitHub Release v{new_version}{draft_str}")

    except Exception as e:
        print(f"\n[!] Error during bump execution: {e}")
        if mutated_local:
            handle_push_error(f"v{new_version}", config_path)
        return False
    else:
        return True

def handle_push_error(tag_name: str, config_path):
    print(f"[!] Local repository was modified with tag '{tag_name}'.")
    do_undo(tag_name, remote=True, config_name=config_path)

def format_dry_run_output(request: BumpRequest, new_version: Version, config_version: dict[Path,Version]) -> str:
    config_out = []
    for config_path in config_version.keys():
        config_out.append(f"Would update {config_path.name} to v{new_version} (DRY RUN)",)
    config_out_str = '\n'.join(config_out)

    output: list[str] = [
        f"Would commit changes: 'bump version to v{new_version}' (DRY RUN)",
        f"{config_out_str}"
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

def detect_bump_type(base_version: Version) -> tuple[BumpType, str]:
    # Regex String Patterns
    pat_major = r"(BREAKING[ -]CHANGE:|^\w+(\([\w\.-]+\))?!:)"
    pat_minor = r"^feat(\([\w\.-]+\))?:"
    pat_patch = r"^fix(\([\w\.-]+\))?:"

    major_count = 0
    minor_count = 0
    patch_count = 0

    for commit in get_commit_since_tag(base_version):
        commit_str = commit['message'].strip()
        if not commit_str:
            continue

        if re.search(pat_major, commit_str, re.MULTILINE):
            major_count += 1

        elif re.search(pat_minor, commit_str, re.MULTILINE):
            minor_count += 1

        elif re.search(pat_patch, commit_str, re.MULTILINE):
            patch_count += 1

    if major_count > 0:
        reason = f"Detected {major_count} BREAKING CHANGE commit(s) since v{base_version}"
        return "major", reason

    if minor_count > 0:
        reason = f"Detected {minor_count} 'feat' commit(s) since v{base_version}"
        return "minor", reason

    if patch_count > 0:
        reason = f"Detected {patch_count} 'fix' commit(s) since v{base_version}"
        return "patch", reason

    raise RuntimeError(
        "No Conventional Commits pattern matched (feat/fix/BREAKING CHANGE). "
        "Please specify bump type manually."
    )

def do_bump(request: BumpRequest):
    if request.push:
        check_network()

    config_version = get_config_version(request.config_path)

    local_tags = get_local_tags()
    remote_tags = get_remote_tags()

    config_tag = parse_highest_version(set(config_version.values()))
    highest_local_tag = parse_highest_version(local_tags)
    highest_overall_tag = parse_highest_version(local_tags | remote_tags)

    all_match = is_all_config_match(config_version)
    if not all_match and not request.force:
        raise ConfigVersionMismatch(
            f"{get_config_mismatch_str(config_version, highest_local_tag)}"
            f"Run `git-version-sync sync` first or use `--force` to bypass."
        )

    missing_in_local = get_missing_local_tags(remote_tags, local_tags)
    if missing_in_local and not request.force:
        missing_str = ", ".join(f"{ver}" for ver in missing_in_local)
        raise GitCommandError(
            f"Remote repository has newer tag(s) missing locally: {missing_str}\n"
            f"Run `git-version-sync sync` first or use `--force` to bump from the highest remote tag."
        )

    base_version = max(
        v
        for v in [config_tag, highest_local_tag, highest_overall_tag]
        if v is not None
    )

    # if run without bump type, will be interactive
    if request.bump_type is None:
        bump_type, reason = detect_bump_type(base_version)
        next_version = calculate_next_version(base_version, bump_type)

        print(reason)
        print(f"Suggested bump: {bump_type} (v{base_version} -> v{next_version})")

        if not request.dry_run:
            confirm = input("Apply this version bump? [Y/n]: ").lower()
            print("")

            if confirm not in ["y", 'yes']:
                return "Bump version has been canceled."

    # Immediately detect version without interactive confirmation
    elif request.bump_type == "auto":
        bump_type, _ = detect_bump_type(base_version)

    # Manual type bump
    else:
        bump_type = request.bump_type

    new_version = Version(calculate_next_version(base_version, bump_type))

    # Dry run
    if request.dry_run:
        return format_dry_run_output(
            request,
            new_version,
            config_version
        )

    bump_status = bump_version(
        request,
        base_version,
        new_version,
        config_version
    )

    return f"\nSuccess bump version to v{new_version}" if bump_status else "\nFailed to bump version"