def sync_subparse(subparsers):
    sync_parser = subparsers.add_parser(
        "sync",
        help="Sync version discrepancies between pyproject.toml and Git tags"
    )
    sync_group = sync_parser.add_mutually_exclusive_group()
    sync_group.add_argument(
        "--to-git",
        action="store_true",
        help="Force config version (pyproject.toml) to match the highest Git tag"
    )
    sync_group.add_argument(
        "--to-config",
        action="store_true",
        help="Force Git tag to match the version in pyproject.toml"
    )
