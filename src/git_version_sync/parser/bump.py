from pathlib import Path

def bump_subparse(subparsers):
    bump_parser = subparsers.add_parser(
        "bump",
        help="Increment project version in configuration file and create a corresponding Git tag"
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
    bump_parser.add_argument(
        "-r",
        "--release",
        nargs="?",
        const="",
        default=None,
        metavar="NOTES",
        help="Create a GitHub release for the bumped version (requires 'gh' CLI)"
    )
    bump_parser.add_argument(
        "-d",
        "--draft",
        action="store_true",
        help="Save the GitHub release as a draft (requires --release)",
    )
    bump_parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making any actual changes"
    )
    bump_parser.add_argument(
        "-c",
        "--config",
        type=Path,
        metavar="PATH",
        help="Path to a custom configuration file (e.g. pyproject.toml, Cargo.toml, package.json)"
    )