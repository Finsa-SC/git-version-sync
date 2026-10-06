import subprocess, shutil
from pathlib import Path
from packaging.version import Version

from git_version_sync.exception import GitCommandError, GitPushError, GitRemoteError


def commit_config_change(new_version: Version, config_version: dict[Path,Version]) -> None:
    if not config_version:
        return

    subprocess.run([
        'git', 'add', *config_version.keys()],
        capture_output=True,
        text=True,
        check=True
    )

    try:
        commit_msg = f"chore(version): bump version to v{new_version}"
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

        error_msg = clean_git_error(e)
        raise GitCommandError(f"Git commit failed: \n{error_msg}") from e

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
        error_msg = clean_git_error(e)
        raise GitPushError(f"Failed to push to remote: \n{error_msg}") from e

def fetch_remote_tags(remote_name: str = 'origin'):
    # Validate git structure
    get_git_path()
    if not has_remote(remote_name):
        raise GitRemoteError(
            f"Remote '{remote_name}' not found.\n"
            f"Hint: Add a remote using 'git remote add {remote_name} <url>'"
        )

    command = ['git', 'fetch', '--tags', remote_name]

    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to fetch tags from remote: {error_msg}") from e

def create_github_release(version: Version, message: str|None=None, draft: bool=False) -> None:
    tag_name = f"v{version}"
    command = ['gh', 'release', 'create', tag_name, '--generate-notes']

    if not shutil.which('gh'):
        raise GitCommandError("Github CLI ('gh') not installed yet, please install 'gh' first.")

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
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to create release tag: \n{error_msg}") from e

def delete_tag(version: Version) -> None:
    command = ['git', 'tag', '-d', f"v{version}"]

    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to check branch status: {error_msg}") from e

def delete_remote_tag(version: Version, remote_name: str) -> None:
    command = ['git', 'push', remote_name, '--delete', f"v{version}"]

    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to check branch status: {error_msg}") from e

def bump_git_tag(new_version: Version, message: str|None = None) -> None:
    msg = message if message and message.strip() else f"bump version to v{new_version}"
    command = [
        'git',
        'tag',
        '-a', f'v{new_version}',
        '-m', msg
    ]

    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        error_msg = clean_git_error(e)

        if "already exists" in error_msg:
            raise GitCommandError(f"Tag 'v{new_version}' already exists in this repository.") from e

        raise GitCommandError(f"Failed to create Git tag:\n{error_msg}") from e

def get_tag_commit(tag_name: str) -> str | None:
    command = ["git", "rev-parse", f"{tag_name}^{{commit}}"]

    try:
        res = subprocess.run(
            command,
            capture_output=True, text=True, check=True
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_head_commit() -> str | None:
    command = ["git", "rev-parse", "HEAD"]

    try:
        res = subprocess.run(
            command,
            capture_output=True, text=True, check=True
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def reset_soft_head() -> None:
    command = ["git", "reset", "--soft", "HEAD~1"]

    try:
        subprocess.run(
            command, check=True
        )
    except subprocess.CalledProcessError as e:
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to soft reset head: {error_msg}") from e

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
            raise GitCommandError(f"Not a Git repository (or any of the parent directories).") from e
        else:
            raise GitCommandError(f"Failed to get git path: {err_msg}") from e

    return Path(result.stdout.strip())

def get_remote_tags(remote_name: str = 'origin') -> set[str]:
    if not has_remote(remote_name):
        raise GitRemoteError(
            f"No remote repository found for {remote_name}.\n"
            f"Hint: Connect a remote repository first using 'git remote add {remote_name} <url>' or list existing remotes with 'git remote -v'."
        )

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
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to check branch status: {error_msg}") from e

def get_commit_since_tag(
        base_version: Version|None = None,
        target_reff: Version|str = "HEAD"
) -> list:
    if target_reff != "HEAD":
        target_reff = f"v{target_reff}" if isinstance(target_reff, Version) else target_reff

    if base_version:
        git_range = f"v{base_version}..{target_reff}"
    else:
        git_range = str(target_reff)

    command = [
        "git", "log",
        git_range,
        "--format=%h%x1f%B%n---END_COMMIT---"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        raw_logs = result.stdout.strip()

        if not raw_logs:
            raise GitCommandError(f"No new commit found, Action cancelled.")

        parsed_commits = []
        raw_commits = [commit.strip() for commit in raw_logs.split("---END_COMMIT---") if commit.strip()]

        for raw_commit in raw_commits:
            if "\x1f" in raw_commit:
                commit_hash, msg = raw_commit.split("\x1f", 1)
                parsed_commits.append({
                    "hash": commit_hash,
                    "message": msg
                })

        return parsed_commits

    except subprocess.CalledProcessError as e:
        if base_version:
            return get_commit_since_tag(None, target_reff)

        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to collect git log: {error_msg}") from e

def clean_git_error(e: subprocess.CalledProcessError) -> str:
    raw_error = e.stderr or e.stdout or str(e)
    lines = raw_error.splitlines()

    ingore_tupple = (
        "remote: error",
        "remote: -",
        "[remote rejected]",
    )

    cleand_lines = []
    for line in lines:
        line_str = line.strip()
        for ignore in ingore_tupple:
            if ignore in line_str:
                cleand_lines.append(line_str)

    if cleand_lines:
        return "\n".join(cleand_lines)

    return raw_error.strip()


def get_local_tags() -> set[str]:
    get_git_path()

    command = ["git", "tag", "--list"]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        tags = {tag for tag in result.stdout.strip().splitlines()}

        return tags
    except subprocess.CalledProcessError as e:
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to collect git log: {error_msg}") from e

def has_remote(remote_name: str = 'origin') -> bool:
    command = ['git', 'remote']

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        remotes = [rmt.strip() for rmt in result.stdout.splitlines()]
        if remote_name == 'origin':
            return len(remotes) >= 1
        else:
            return remote_name in remotes

    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_remote_connection(remote_name: str = 'origin', timeout: int = 5) -> None:
    command = ["git", "ls-remote", "--exit-code", "-h", remote_name]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=True
        )

    except subprocess.TimeoutExpired:
        raise GitRemoteError(f"Network error: Connection to remote '{remote_name}' timed out.")
    except subprocess.CalledProcessError as e:
        raise OSError(
            f"Network error: Unable to reach remote '{remote_name}'. "
            f"Please check your internet connection or repository access rights."
        ) from e

def get_tag_commit_hash(tag_name: str) -> str:
    try:
        command = ['git', 'rev-parse', f'{tag_name}^{{commit}}']

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        error_msg = clean_git_error(e)
        raise GitCommandError(f"Failed to resolve commit for tag '{tag_name}': {error_msg}") from e

def is_commit_in_current_branch(commit_hash: str) -> bool:
    command = ['git', 'merge-base', '--is-ancestor', commit_hash, 'HEAD']

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return True
    except subprocess.CalledProcessError:
        return False