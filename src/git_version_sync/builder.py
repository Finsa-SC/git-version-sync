import argparse
from importlib.metadata import version, PackageNotFoundError

from git_version_sync.parser import check_subparse, sync_subparse, bump_subparse, push_subparse


def create_parser():
    parser = argparse.ArgumentParser(
        prog="git-version-sync",
        description="Sync Git tags and pyproject.toml versions.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    try:
        pkg_version = version('git-version-sync')
    except PackageNotFoundError:
        pkg_version = "unknown"

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {pkg_version}"
    )

    check_subparse(subparsers)
    sync_subparse(subparsers)
    bump_subparse(subparsers)
    push_subparse(subparsers)

    return parser