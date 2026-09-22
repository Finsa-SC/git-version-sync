import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        prog="git-version-sync",
        description="Sync Git tags and pyproject.toml versions.",
    )

    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch remote tags before checking"
    )

    subparsers.add_parser("sync")

    bump_parser = subparsers.add_parser("bump")
    bump_parser.add_argument(
        "part",
        choices=["major", "minor", "patch"],
    )
    bump_parser.add_argument(
        "--force",
        action="store_true",
        help="Force bump even if version mismatch occurs"
    )
    bump_parser.add_argument(
        "-m",
        "--message",
        type=str,
        help="Give message for the tag"
    )

    return parser