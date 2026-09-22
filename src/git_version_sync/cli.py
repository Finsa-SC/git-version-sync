from .parser import create_parser

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
            ...