def bump_subparse(subparsers):
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