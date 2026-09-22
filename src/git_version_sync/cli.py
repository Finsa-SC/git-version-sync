from .parser import create_parser
from .core import do_check

def do_bump():
    ...

def main():
    parser = create_parser()
    args = parser.parse_args()

    match args.command:
        case 'bump':
            do_bump()
        case 'sync':
            ...
        case 'check':
            do_check(args.fetch)

if __name__ == "__main__":
    main()