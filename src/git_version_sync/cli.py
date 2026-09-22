from .parser import create_parser
from .core import do_check, do_bump, do_sync


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        match args.command:
            case 'bump':
                print(do_bump(
                    args.part,
                    message=args.message,
                    force=args.force
                ))
            case 'sync':
                do_sync(args.to_git, args.to_config)
            case 'check':
                print(do_check(args.fetch))
            case _:
                print(f"Invalid command {args.command}")
        print("\n")
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    main()