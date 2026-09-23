import subprocess, shutil

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

def push_to_remote(new_version: Version) -> None:
    try:
        command = [
            'git', 'push',
            'origin', 'HEAD',
            f'v{new_version}'
        ]

        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to push to remote: \n{e.stderr.strip()}") from e

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