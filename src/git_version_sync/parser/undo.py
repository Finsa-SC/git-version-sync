def undo_subparse(subparsers, parent_parser):
    undo_parser = subparsers.add_parser(
        "undo",
        help="Undo/rollback the last version bump and delete its corresponding Git tag",
        parents=[parent_parser] if parent_parser else []
    )
    undo_parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Specific tag/version to undo (e.g. v1.6.0). Default: latest tag."
    )
    undo_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Bypass confirmation prompts"
    )