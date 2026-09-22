import subprocess, re
import tomllib
from pathlib import Path
from packaging.version import Version
from typing import Literal

from .check import parse_highest_verion, get_local_tags, get_config_tag, get_git_path

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

def bump_config_version(new_version: Version, config_path: Path) -> None:
    content = config_path.read_text(encoding="utf-8")

    pattern = r'^(version\s*=\s*["\']).*?(["\'])'
    replacement = rf'\g<1>{new_version}\g<2>'

    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count == 0:
        raise RuntimeError(f"Version field not found in {config_path.stem}")

    config_path.write_text(new_content, encoding="utf-8")

def bump_version(new_version: Version, config_path: Path, message: str|None=None) -> None:
    bump_git_tag(new_version, message)
    bump_config_version(new_version, config_path)

def get_new_major(version: Version) -> str:
    return f"{version.major + 1}.0.0"

def get_new_minor(version: Version) -> str:
    return f"{version.major}.{version.minor + 1}.0"

def get_new_patch(version: Version):
    return f"{version.major}.{version.minor}.{version.micro + 1}"

BumpType = Literal["major", "minor", "patch"]

def do_bump(bump_type: BumpType, message: str|None = None, force: bool = False):
    config_tag = get_config_tag()
    local_tags = get_local_tags()
    highest_local_tag = parse_highest_verion(local_tags)

    if config_tag != highest_local_tag and not force:
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

    config_path = get_git_path() / "pyproject.toml"

    if not config_path.exists():
        raise RuntimeError(f"Config file not found: {config_path}")

    match bump_type:
        case "major":
            new_version = get_new_major(old_version)
        case "minor":
            new_version = get_new_minor(old_version)
        case "patch":
            new_version = get_new_patch(old_version)

    new_version = Version(new_version)

    bump_version(new_version, config_path, message)

    return f"Success bump version to v{new_version}"