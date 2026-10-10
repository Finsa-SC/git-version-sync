from packaging.version import Version, InvalidVersion

from .changelog import generate_changelog
from .check import get_remote_tags, parse_highest_version, get_missing_in_remote_tags
from .git import (
    push_to_remote,
    fetch_remote_tags,
    get_commit_since_tag,
    create_github_release,
    get_local_tags
)
from ..exception import GitPushError
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

def seperate_non_semver(tag_list: set[str]) -> tuple[set[str], set[str]]:
    semver = set()
    non_semver = set()
    for tag in tag_list:
        try:
            semver.add(Version(tag))
        except InvalidVersion:
            non_semver.add(tag)

    return semver, non_semver

def do_push(request: PushRequest):
    remote_name = request.remote_name if request.remote_name else 'origin'
    fetch_remote_tags(remote_name)

    local_tags = get_local_tags()
    remote_tags = get_remote_tags()
    unpush_tags = get_missing_in_remote_tags(remote_tags, local_tags)
    latest_tags = parse_highest_version(local_tags)


    if latest_tags is None:
        raise GitPushError("Failed to push to remote, No local tag found.")

    pending_tags: list[Version|str] = []
    # If using --all flag
    if request.push_all:
        semver_tags, non_semver_tags = seperate_non_semver(unpush_tags)
        pending_tags.extend(semver_tags)
        pending_tags.extend(non_semver_tags)

    # If user input tag(s) manually
    elif request.tags:
        unknown_tags = set(request.tags) - unpush_tags

        tag_not_exists = False
        # Validate invalid tags
        for tag in unknown_tags:
            if tag not in local_tags:
                tag_not_exists = True
                break

        is_valid = len(unknown_tags) > 0
        if is_valid and tag_not_exists:
            raise GitPushError(
                f"Error: Tag(s) not found locally: {', '.join(unknown_tags)}\n"
                f"Nothing was pushed."
            )

        clean_unpush_tags = seperate_non_semver(unpush_tags)
        pending_tags.extend(Version(ver) for ver in request.tags if ver in clean_unpush_tags)

    # If user doesn't input any tag, auto use latest lag
    elif f"v{latest_tags}" in unpush_tags:
        pending_tags.append(latest_tags)

    if not pending_tags:
        if request.tags:
            print(f"Already on {remote_name}: {', '.join(request.tags)}")
        else:
            print(f"Nothing to push: all local tags already exist on {remote_name}.")
        return

    print(f"Pushing tag(s) to remote: {', '.join(f'v{ver}' for ver in pending_tags)}")
    push_to_remote(pending_tags, remote_name)

    number_of_tag = len(pending_tags)
    if number_of_tag > 1:
        print(f"Pushed: {number_of_tag} tags to origin.")
    else:
        print(f"Pushed: v{pending_tags[0]} -> {remote_name}.")

    if request.release is not None:
        for target_version in pending_tags:
            # Skip non semver
            if isinstance(target_version, str):
                continue

            if request.release.strip():
                change_log = request.release
            else:
                prev_tag = get_previous_tag(target_version, local_tags)
                commits = get_commit_since_tag(prev_tag, target_version)
                change_log = generate_changelog(commits)

            print(f"Created GitHub Release for v{target_version}")
            create_github_release(target_version, change_log)