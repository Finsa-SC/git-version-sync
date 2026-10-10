import sys

from git_version_sync.exception import GitVersionSyncError
from git_version_sync.models import BumpRequest, SyncRequest, PushRequest, UndoRequest
from .builder import create_parser
from .core import do_check, do_bump, do_sync, do_push, do_undo


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        match args.command:
            case 'bump':
                bump_request = BumpRequest(
                    args.part,
                    config_path=args.config,
                    tag_message=args.message,
                    force=args.force,
                    push=args.push,
                    release=args.release,
                    draft=args.draft,
                    dry_run=args.dry_run,
                    no_prefix=args.no_prefix,
                    remote_name=args.remote
                )
                print(do_bump(
                    bump_request
                ))

            case 'sync':
                sync_request = SyncRequest(
                    to_git      = args.to_git,
                    to_config   = args.to_config,
                    config_name = args.config,
                    remote_name = args.remote,
                )
                do_sync(
                    sync_request
                )

            case 'check':
                print(do_check(
                    config_name=args.config,
                    no_fetch=args.no_fetch,
                    remote_name=args.remote or "origin"
                ))

            case 'push':
                # User Input Validation
                if args.all and args.tags:
                    args._parser.error("--all cannot be combined with explicit tags.")

                push_request = PushRequest(
                    tags=args.tags,
                    push_all=args.all,
                    release=args.release,
                    remote_name=args.remote,
                )
                do_push(
                    push_request
                )

            case 'undo':
                undo_request = UndoRequest(
                    undo_tag=args.target,
                    force=args.force,
                    config_name=args.config,
                    remote_name=args.remote,
                )
                do_undo(
                    undo_request
                )

            case _:
                print(f"Invalid command {args.command}")

    except GitVersionSyncError as e:
        print(f"{e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        raise

if __name__ == "__main__":
    main()