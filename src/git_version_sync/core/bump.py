import subprocess, re
from packaging.version import Version

from .git import commit_config_change, push_to_remote, create_github_release
from .check import parse_highest_verion, get_local_tags, get_config_tag, get_remote_tags, get_missing_local_tags
from ..models import BumpRequest, BumpType
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
    content = config_path.read_text(encoding="utf-8")

    pattern = r'^(version\s*=\s*["\']).*?(["\'])'
    replacement = rf'\g<1>{new_version}\g<2>'

    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count == 0:
        raise RuntimeError(f"Version field not found in {config_path.stem}")

    config_path.write_text(new_content, encoding="utf-8")

def bump_version(
        request: BumpRequest,
        new_version: Version,
) -> None:
    print("Updating pyproject.toml version...")
    bump_config_version(new_version)

    print("Committing new change...")
    commit_config_change(new_version)

    print(f"Creating git tag v{new_version}...")
    bump_git_tag(new_version, request.tag_message)

    if request.push:
        print("Pushing commit and tag to remote...")
        push_to_remote(new_version)

    if request.release is not None:
        print(f"Creating GitHub Release for v{new_version}...")
        create_github_release(new_version, request.release, request.draft)

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
        missing_str = ", ".join(f"v{ver}" for ver in missing_in_local)
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

    bump_version(
        request,
        new_version
    )

    return f"\nSuccess bump version to v{new_version}"