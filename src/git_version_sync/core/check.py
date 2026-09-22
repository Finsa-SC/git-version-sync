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

def get_config_tag() -> Version:
    config_path = get_git_path() / "pyproject.toml"

    if not config_path.exists():
        raise RuntimeError(f"Config file not found: {config_path}")

    with config_path.open('rb') as f:
        config = tomllib.load(f)
        project_config = config.get('project', {})
        config_tag = project_config.get("version", None)

    if config_tag is None:
        raise ValueError("No version found in project config.")

    return Version(config_tag)

def get_remote_tags() -> set[str]:
    command = ['git', 'ls-remote', '--tags', 'origin']
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    if result.returncode != 0:
        return set()

    remote_tags = set()
    for line in result.stdout.strip().splitlines():
        if not line:
            continue

        parts = line.split()
        if len(parts) == 2:
            ref = parts[1]
            if ref.endswith("^{}"):
                continue
            tag_name = ref.removeprefix("refs/tags/")
            remote_tags.add(tag_name)

    return remote_tags

def do_check(fetch_true: bool = False) -> str:
    config_tag = get_config_tag()
    local_tags = get_local_tags()
    remote_tags = get_remote_tags()

    output = []

    highest_local_version = parse_highest_verion(local_tags)
    if highest_local_version is None:
        return "No local tags found."

    if highest_local_version == config_tag:
        output.append(f"Version is synchronized with highest local tag (v{config_tag})")
    else:
        output.append(
            f"Version mismatch\n"
            f"Git Local: {highest_local_version}\n"
            f"Config:    {config_tag}"
        )

    if fetch_true:
        missing_in_local = remote_tags - local_tags
        if missing_in_local:
            output.append(f"New tag(s) found from remote: ")
            for tag in sorted(missing_in_local):
                output.append(f"  - {tag}")
            output.append("")

    return "\n".join(output)

if __name__ == "__main__":
    print(do_check())