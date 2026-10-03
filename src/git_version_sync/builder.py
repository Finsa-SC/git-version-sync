import argparse
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

from git_version_sync.parser import check_subparse, sync_subparse, bump_subparse, push_subparse, undo_subparse


def create_parser():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-c",
        "--config",
        type=Path,
        metavar="PATH",
        help="Path to a custom configuration file (e.g. pyproject.toml, Cargo.toml, package.json)"
    )
    parent_parser.add_argument(
        "-R",
        "--remote",
        nargs="?",
        type=str,
        const="origin",
        default=None,
        metavar="REMOTE",
        help="Target Git remote repository name (default if flag used: origin)"
    )

    parser = argparse.ArgumentParser(
        prog="git-version-sync",
        description="Sync Git tags and project config versions.",
        parents=[parent_parser]
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

    check_subparse(subparsers, parent_parser)
    sync_subparse(subparsers, parent_parser)
    bump_subparse(subparsers, parent_parser)
    push_subparse(subparsers, parent_parser)
    undo_subparse(subparsers, parent_parser)

    return parser