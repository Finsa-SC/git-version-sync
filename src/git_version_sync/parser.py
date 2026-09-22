import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        prog="git-version-sync",
        description="Sync Git tags and pyproject.toml versions.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("sync")

    bump_parser = subparsers.add_parser("bump")
    bump_parser.add_argument(
        "part",
        choices=["major", "minor", "patch"],
    )

    return parser