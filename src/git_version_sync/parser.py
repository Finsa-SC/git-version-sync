import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        prog="git-version-sync",
        description="Sync Git tags and pyproject.toml versions.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: check
    check_parser = subparsers.add_parser(
        "check",
        help="Check and compare current version status between Git tags and pyproject.toml"
    )
    check_parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch remote tags before checking"
    )

    # Subcommand: sync
    sync_parser = subparsers.add_parser(
        "sync",
        help="Sync version discrepancies between pyproject.toml and Git tags"
    )
    sync_group = sync_parser.add_mutually_exclusive_group()
    sync_group.add_argument(
        "--to-git",
        action="store_true",
        help="Force config version (pyproject.toml) to match the highest Git tag"
    )
    sync_group.add_argument(
        "--to-config",
        action="store_true",
        help="Force Git tag to match the version in pyproject.toml"
    )

    # Subcommand: bump
    bump_parser = subparsers.add_parser(
        "bump",
        help="Increment version in pyproject.toml and create a corresponding Git tag"
    )
    bump_parser.add_argument(
        "part",
        choices=["major", "minor", "patch"],
        help="Version part to increment (major, minor, or patch)"
    )
    bump_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force bump even if version mismatch occurs"
    )
    bump_parser.add_argument(
        "-p",
        "--push",
        action="store_true",
        help="Automatically push commit and the new tag to remote"
    )
    bump_parser.add_argument(
        "-m",
        "--message",
        type=str,
        help="Custom annotation message for the created Git tag"
    )

    return parser