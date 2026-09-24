def undo_subparse(subparsers):
    undo_parser = subparsers.add_parser(
        "undo",
        help="Undo/rollback the last version bump and delete its corresponding Git tag"
    )
    undo_parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Specific tag/version to undo (e.g. v1.6.0). Default: latest tag."
    )
    undo_parser.add_argument(
        "-r",
        "--remote",
        action="store_true",
        help="Also delete the target tag from remote repository if pushed"
    )
    undo_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Bypass confirmation prompts"
    )