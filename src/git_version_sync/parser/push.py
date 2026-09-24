def push_subparse(subparsers):
    push_parser = subparsers.add_parser(
        "push",
        help="Push active branch and Git tags to remote repository"
    )
    push_parser.add_argument(
        "tags",
        nargs="*",
        default=[],
        help="Specific tag(s) to push (e.g. v1.0.0 v1.0.1). If empty, pushes active version tag."
    )
    push_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="push_all",
        help="Push all local tags to remote"
    )