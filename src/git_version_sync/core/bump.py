import subprocess, re
from packaging.version import Version

from .git import commit_config_change, push_to_remote
from .check import parse_highest_verion, get_local_tags, get_config_tag
from ..models import BumpRequest
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
    bump_config_version(new_version)
    commit_config_change(new_version)
    bump_git_tag(new_version, request.tag_message)

    if request.push:
        push_to_remote(new_version)

def get_new_major(version: Version) -> str:
    return f"{version.major + 1}.0.0"

def get_new_minor(version: Version) -> str:
    return f"{version.major}.{version.minor + 1}.0"

def get_new_patch(version: Version):
    return f"{version.major}.{version.minor}.{version.micro + 1}"

def do_bump(request: BumpRequest):
    config_tag = get_config_tag()
    local_tags = get_local_tags()
    highest_local_tag = parse_highest_verion(local_tags)

    if config_tag != highest_local_tag and not request.force:
        raise RuntimeError(
            f"Version mismatch detected!\n"
            f"  Config: v{config_tag}\n"
            f"  Git   : v{highest_local_tag}\n"
            f"Please run `git-version-sync sync` first or fix the mismatch."
        )

    if highest_local_tag:
        old_version = max(config_tag, highest_local_tag)
    else:
        old_version = config_tag

    config_path = get_config_path()

    if not config_path.exists():
        raise RuntimeError(f"Config file not found: {config_path}")

    match request.bump_type:
        case "major":
            new_version = get_new_major(old_version)
        case "minor":
            new_version = get_new_minor(old_version)
        case "patch":
            new_version = get_new_patch(old_version)

    new_version = Version(new_version)

    bump_version(
        request,
        new_version
    )

    return f"Success bump version to v{new_version}"