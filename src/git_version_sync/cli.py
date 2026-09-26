from git_version_sync.models import BumpRequest
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
                )
                print(do_bump(
                    bump_request
                ))

            case 'sync':
                print(do_sync(
                    args.to_git,
                    args.to_config,
                    config_name=args.config,
                ))

            case 'check':
                print(do_check(
                    config_name=args.config,
                    no_fetch=args.no_fetch,
                ))

            case 'push':
                do_push(args.tags, args.all)

            case 'undo':
                do_undo(
                    args.target,
                    remote=args.remote,
                    force=args.force,
                    config_name=args.config,
                )

            case _:
                print(f"Invalid command {args.command}")

    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    main()