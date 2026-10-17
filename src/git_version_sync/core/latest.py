from git_version_sync.core.git import get_tag_commit_hash, get_remote_tag_commit_hash
from git_version_sync.exception import GitVersionSyncError


def is_highest_up_to_date_with_remote(highest_tag: str, remote: str = "origin") -> bool:
    target_hash = get_tag_commit_hash(highest_tag)
    try:
        remote_hash = get_remote_tag_commit_hash("latest", remote)
    except GitVersionSyncError:
        return False
    return target_hash == remote_hash

def is_latest_up_to_date_with_local(highest_tag: str) -> bool:
    highest_hash = get_tag_commit_hash(highest_tag)
    latest_hash = get_tag_commit_hash('latest')

    return highest_hash == latest_hash