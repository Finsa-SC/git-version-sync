from packaging.version import Version, InvalidVersion


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