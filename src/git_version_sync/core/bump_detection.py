import re

from packaging.version import Version

from git_version_sync.core.git import get_commit_since_tag
from git_version_sync.exception import GitVersionSyncError
from git_version_sync.models import BumpType


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

def detect_bump_type(base_version: str) -> tuple[BumpType, str]:
    # Regex String Patterns
    pat_major = r"(BREAKING[ -]CHANGE:|^\w+(\([\w\.-]+\))?!:)"
    pat_minor = r"^feat(\([\w\.-]+\))?:"
    pat_patch = r"^fix(\([\w\.-]+\))?:"

    major_count = 0
    minor_count = 0
    patch_count = 0

    for commit in get_commit_since_tag(Version(base_version)):
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
        reason = f"Detected {major_count} BREAKING CHANGE commit(s) since {base_version}"
        return "major", reason

    if minor_count > 0:
        reason = f"Detected {minor_count} 'feat' commit(s) since {base_version}"
        return "minor", reason

    if patch_count > 0:
        reason = f"Detected {patch_count} 'fix' commit(s) since {base_version}"
        return "patch", reason

    raise GitVersionSyncError(
        "No Conventional Commits pattern matched (feat/fix/BREAKING CHANGE). "
        "Please specify bump type manually."
    )