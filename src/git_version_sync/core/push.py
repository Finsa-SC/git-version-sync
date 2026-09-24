from packaging.version import Version

from .check import get_local_tags, get_remote_tags, parse_highest_verion
from .git import push_to_remote, fetch_remote_tags


def do_push(tags: list[str], push_all: bool=False):
    fetch_remote_tags()

    local_tags = get_local_tags()

    tags_to_push: list[str] = []

    if push_all:
        remote_tags = get_remote_tags()
        unpush_tags = local_tags - remote_tags

        if unpush_tags:
            tags_to_push.extend(unpush_tags)
        else:
            print("Everything up-to-date.")
            return

    elif tags:
        tags_to_push.extend(tags)

    else:
        latest_tags = parse_highest_verion(local_tags)
        if latest_tags:
            tags_to_push.append(f"v{latest_tags}")
        else:
            raise RuntimeError("Failed to push to remote, No local tag found.")

    for tag in tags_to_push:
        print(f"Pushing (v{tag}) to remote...")
        push_to_remote(Version(tag))