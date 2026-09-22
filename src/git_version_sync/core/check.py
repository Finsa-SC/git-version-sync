from pathlib import Path
import subprocess, tomllib
from packaging.version import Version

def get_git_path() -> Path:
    command = ["git", "rev-parse", "--show-toplevel"]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return Path(result.stdout.strip())

def get_tag_list() -> list[str]:
    command = ["git", "tag", "--list"]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    tags = result.stdout.strip().splitlines()

    return tags

def get_last_tag() -> Version:
    tags = get_tag_list()

    versions = [
        Version(tag.removeprefix('v'))
        for tag in tags
    ]

    if not versions:
        raise RuntimeError("No git tag found.")

    latest = max(versions)

    return latest

def get_config_tag() -> Version:
    config_path = get_git_path() / "pyproject.toml"

    with config_path.open('rb') as f:
        config = tomllib.load(f)
        project_config = config.get('project', {})
        config_tag = project_config.get("version", None)

    if config_tag is None:
        raise ValueError("No version found in project config.")

    return Version(config_tag)

def do_check() -> str:
    git_tag = get_last_tag()
    config_tag = get_config_tag()

    if git_tag == config_tag:
        return "Version is synchronized"
    else:
        return (
            f"Version mismatch\n"
            f"Git:    {git_tag}\n"
            f"Config: {config_tag}"
        )

if __name__ == "__main__":
    print(do_check())