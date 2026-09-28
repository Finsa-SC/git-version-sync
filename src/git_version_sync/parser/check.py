def check_subparse(subparsers, parent_parser):
    check_parser = subparsers.add_parser(
        "check",
        help="Check and compare current version status between Git tags and project configuration version",
        parents=[parent_parser] if parent_parser else []
    )
    check_parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip fetching tags from remote repository"
    )