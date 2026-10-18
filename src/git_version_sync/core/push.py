from packaging.version import Version, InvalidVersion

from .changelog import generate_changelog
from .check import get_remote_tags, parse_highest_version, get_missing_in_remote_tags
from .git import (
    push_to_remote,
    fetch_remote_tags,
    get_commit_since_tag,
    create_github_release,
    get_local_tags,
    get_current_remote,
    set_latest_tag,
    is_gh_accessible
)
from .latest import is_highest_up_to_date_with_remote, is_latest_up_to_date_with_local
from ..exception import GitPushError, GitCommandError
from ..models import PushRequest
from ..utils import Color


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

# Return semver and non-semver
def separate_non_semver(tag_list: set[str]) -> tuple[set[str], set[str]]:
    semver = set()
    non_semver = set()
    for tag in tag_list:
        try:
            Version(tag)
            semver.add(tag)
        except InvalidVersion:
            non_semver.add(tag)

    return semver, non_semver

def do_push(request: PushRequest):
    # Check gh-cli if using release flag
    if request.release is not None and not is_gh_accessible():
        raise GitCommandError(
            f"GitHub CLI ('gh') is unavailable or not authenticated.\n"
            f"{Color.BLUE}Hint: Ensure GitHub CLI is installed and run 'gh auth login'."
        )

    remote_name = request.remote_name if request.remote_name else get_current_remote()
    fetch_remote_tags(remote_name)

    local_tags = get_local_tags()
    remote_tags = get_remote_tags(remote_name)
    unpush_tags = get_missing_in_remote_tags(remote_tags, local_tags)
    latest_local_tag = parse_highest_version(local_tags)


    if latest_local_tag is None:
        raise GitPushError("Failed to push to remote, No local tag found.")

    pending_tags: list[str] = []
    release_tags: list[str] = []

    # If using --all flag
    if request.push_all:
        semver_tags, non_semver_tags = separate_non_semver(unpush_tags)
        pending_tags.extend(semver_tags)
        pending_tags.extend(non_semver_tags)

        release_tags += unpush_tags

    # If user input tag(s) manually
    elif request.tags:
        requested = list(dict.fromkeys(request.tags))

        missing_tags = [tag for tag in requested if tag not in local_tags]
        if missing_tags:
            raise GitPushError(
                f"Error: Tag(s) not found locally: {', '.join(missing_tags)}\n"
                f"Nothing was pushed."
            )

        pending_tags.extend(tag for tag in request.tags if tag in unpush_tags)
        release_tags.extend(requested)

    # If user doesn't input any tag, auto use latest lag
    elif latest_local_tag in unpush_tags:
        pending_tags.append(latest_local_tag)
        release_tags.append(latest_local_tag)

    if not pending_tags and not request.push_latest:
        if request.tags:
            print(f"Already on {remote_name}: {', '.join(request.tags)}")
        else:
            print(f"Nothing to push: {latest_local_tag} (highest tag) already exists on {remote_name}.")
            if unpush_tags:
                print(f"{len(unpush_tags)} other local tag(s) are not in {remote_name} yet: {', '.join(unpush_tags)}")
                print(f"{Color.BLUE}Hint: Use 'git-version-sync push --all' to send them, or 'push <tag> ...' to choose.")
        return

    # Latest tag logic
    force_tags = []
    if request.push_latest:
        if is_latest_up_to_date_with_local(latest_local_tag) and is_highest_up_to_date_with_remote(latest_local_tag, remote_name):
            print(f"'latest' is already up to date ({latest_local_tag}) with {remote_name}.")
        else:
            set_latest_tag(latest_local_tag)
            print("Update the 'latest' local tag.")
            force_tags.append('latest')

    pending_tags = [tag for tag in pending_tags if tag not in force_tags]

    # Return if nothing to push
    if not pending_tags and not force_tags:
        return

    print(f"Pushing tag(s) to remote: {', '.join(f'{ver}' for ver in pending_tags)}")
    push_to_remote(pending_tags, remote_name, force_tags=force_tags)

    pushed = [*pending_tags, *force_tags]
    if len(pushed) > 1:
        print(f"Pushed: {len(pushed)} tags to {remote_name}.")
    else:
        print(f"Pushed: {pushed[0]} -> {remote_name}.")

    if request.release is not None:
        for target_version in release_tags:
            # Skip non semver
            try:
                Version(target_version)
            except InvalidVersion:
                continue

            if request.release.strip():
                change_log = request.release
            else:
                prev_tag = get_previous_tag(Version(target_version), local_tags)
                commits = get_commit_since_tag(prev_tag, target_version)
                change_log = generate_changelog(commits)

            create_github_release(target_version, change_log)
            print(f"Created GitHub Release for {target_version}")