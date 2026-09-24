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
                    tag_message=args.message,
                    force=args.force,
                    push=args.push,
                    release=args.release,
                    draft=args.draft,
                )
                print(do_bump(bump_request))

            case 'sync':
                print(do_sync(args.to_git, args.to_config))

            case 'check':
                print(do_check())

            case 'push':
                do_push(args.tags, args.all)

            case 'undo':
                do_undo(
                    args.target,
                    remote=args.remote,
                    force=args.force,
                )

            case _:
                print(f"Invalid command {args.command}")

    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    main()