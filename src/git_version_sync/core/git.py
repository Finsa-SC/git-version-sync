import subprocess, shutil
from pathlib import Path
from packaging.version import Version
from git_version_sync.utils import get_config_path

def commit_config_change(new_version: Version) -> None:
    subprocess.run([
        'git', 'add', str(get_config_path())],
        capture_output=True,
        text=True,
        check=True
    )

    try:
        commit_msg = f"chore({get_config_path().name}): bump version to v{new_version}"
        subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        output = (e.stdout or "") + (e.stderr or "")
        if "nothing to commit" in output:
            return
        raise RuntimeError(f"Git commit failed: \n{e.stderr.strip()}") from e

def push_to_remote(new_version: list[Version]|Version) -> None:
    try:
        command = [
            'git', 'push',
            'origin', 'HEAD',
        ]

        if isinstance(new_version, Version):
            command.append(f"v{new_version}")
        else:
            str_version = [f"v{version}" for version in new_version]
            command.extend(str_version)

        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to push to remote: \n{e.stderr.strip()}") from e

def fetch_remote_tags():
    command = ['git', 'fetch', '--tags', 'origin']

    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to fetch tags from remote: {e.stderr.strip()}") from e

def create_github_release(version: Version, message: str|None=None, draft: bool=False):
    tag_name = f"v{version}"
    command = ['gh', 'release', 'create', tag_name, '--generate-notes']

    if not shutil.which('gh'):
        raise RuntimeError("Github CLI ('gh') not installed yet, please install 'gh' first.")

    if message and message.strip():
        command.extend(['--notes', message])
    if draft:
        command.extend(['--draft'])

    push_to_remote(version)
    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create release tag: \n{e.stderr.strip()}") from e

def get_git_path() -> Path:
    command = ["git", "rev-parse", "--show-toplevel"]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        err_msg = (e.stderr or "").strip()

        if "not a git" in err_msg:
            raise RuntimeError(f"Not a Git repository (or any of the parent directories).") from e
        else:
            raise RuntimeError(f"Failed to get git path: {err_msg}") from e

    return Path(result.stdout.strip())

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

def is_branch_behind_remote() -> bool:
    command = ['git', 'rev-list', '--count', 'HEAD..@{u}']

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return int(result.stdout.strip() or 0) > 0

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to check branch status: {e.stderr.strip()}") from e