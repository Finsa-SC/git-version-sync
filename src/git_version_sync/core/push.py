from packaging.version import Version

from .changelog import generate_changelog
from .check import get_remote_tags, parse_highest_version
from .git import push_to_remote, fetch_remote_tags, get_commit_since_tag, create_github_release, get_local_tags
from ..models import PushRequest


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

def do_push(request: PushRequest):
    fetch_remote_tags()

    local_tags = get_local_tags()
    remote_tags = get_remote_tags()
    unpush_tags = local_tags - remote_tags
    latest_tags = parse_highest_version(local_tags)

    tags_to_push: list[Version] = []

    if latest_tags is None:
        raise RuntimeError("Failed to push to remote, No local tag found.")

    if request.push_all:
        tags_to_push.extend(Version(ver) for ver in unpush_tags)

    elif request.tags:
        tags_to_push.extend(Version(ver) for ver in request.tags if ver in unpush_tags)

    elif f"v{latest_tags}" in unpush_tags:
        tags_to_push.append(latest_tags)

    # Check missing tags
    if not tags_to_push:
        print(f"Everything up-to-date at tag v{latest_tags}")
        return

    tags_to_push.sort()

    print(f"Pushing tag(s) to remote: {', '.join(f'v{ver}' for ver in tags_to_push)}")
    push_to_remote(tags_to_push)

    number_of_tag = len(tags_to_push)
    if number_of_tag > 1:
        print(f"Pushed: {number_of_tag} tags to origin.")
    else:
        print(f"Pushed: {tags_to_push[0]} -> origin.")

    if request.release is not None:
        for target_version in tags_to_push:
            if request.release.strip():
                change_log = request.release
            else:
                prev_tag = get_previous_tag(target_version, local_tags)
                commits = get_commit_since_tag(prev_tag, target_version)
                change_log = generate_changelog(commits)

            print(f"Created GitHub Release for v{target_version}")
            create_github_release(target_version, change_log)