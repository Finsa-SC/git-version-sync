from packaging.version import Version

from .check import get_local_tags, get_remote_tags, parse_highest_verion
from .git import push_to_remote, fetch_remote_tags


def do_push(tags: list[str], push_all: bool=False):
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

    elif latest_tags in unpush_tags:
        tags_to_push.append(latest_tags)

    # Check missing tags
    if not tags_to_push:
        print(f"Everything up-to-date at tag v{latest_tags}")
        return

    print(f"Pushing tag(s) to remote: {', '.join(f'v{ver}' for ver in tags_to_push)}")

    push_to_remote(tags_to_push)