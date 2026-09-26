def check_subparse(subparsers):
    check_parser = subparsers.add_parser(
        "check",
        help="Check and compare current version status between Git tags and project configuration version"
    )
    check_parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip fetching tags from remote repository"
    )