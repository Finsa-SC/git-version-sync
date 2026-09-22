from .parser import create_parser
from .core import do_check

def do_bump():
    ...

def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        match args.command:
            case 'bump':
                do_bump()
            case 'sync':
                ...
            case 'check':
                print(do_check(args.fetch))
            case _:
                print(f"Invalid command {args.command}")
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    main()