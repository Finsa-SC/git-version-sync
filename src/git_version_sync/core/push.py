from packaging.version import Version

from .changelog import generate_changelog
from .check import get_local_tags, get_remote_tags, parse_highest_verion
from .git import push_to_remote, fetch_remote_tags, get_commit_since_tag, create_github_release


def get_previous_tag(target_version: Version, local_tags: set[str]) -> Version|None:
    previous_tag = []

    for tag_str in local_tags:
        try:
            ver = Version(tag_str.lstrip("v"))
            if ver < target_version:
                previous_tag.append(ver)
        except ValueError:
            continue

    if not previous_tag:
        return None

    return max(previous_tag)

def do_push(tags: list[str], push_all: bool=False, release: str|None=None):
    fetch_remote_tags()

    local_tags = get_local_tags()
    remote_tags = get_remote_tags()
    unpush_tags = local_tags - remote_tags
    latest_tags = parse_highest_verion(local_tags)

    tags_to_push: list[Version] = []

    if latest_tags is None:
        raise RuntimeError("Failed to push to remote, No local tag found.")

    if push_all:
        tags_to_push.extend(Version(ver) for ver in unpush_tags)

    elif tags:
        tags_to_push.extend(Version(ver) for ver in tags if ver in unpush_tags)

    elif f"v{latest_tags}" in unpush_tags:
        tags_to_push.append(latest_tags)

    # Check missing tags
    if not tags_to_push:
        print(f"Everything up-to-date at tag v{latest_tags}")
        return

    tags_to_push.sort()

    print(f"Pushing tag(s) to remote: {', '.join(f'v{ver}' for ver in tags_to_push)}")
    push_to_remote(tags_to_push)

    if release is not None:
        for target_version in tags_to_push:
            if release.strip():
                change_log = release
            else:
                prev_tag = get_previous_tag(target_version, local_tags)
                commits = get_commit_since_tag(prev_tag, target_version)
                change_log = generate_changelog(commits)

            print(f"Created GitHub Release for v{target_version}")
            create_github_release(target_version, change_log)