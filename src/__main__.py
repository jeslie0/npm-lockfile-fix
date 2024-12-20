from .npmfix import get_lockfile_json, loop_through_packages, save_json, make_parser
import json


def main_impl(args):
    lockfile_path = args.filename

    lockfile_json = get_lockfile_json(lockfile_path, args.cout)

    loop_through_packages(lockfile_json['packages'], args.r, args.cout)

    if args.cout:
        print(json.dumps(lockfile_json))
        return 0

    outpath = lockfile_path if args.output is None else args.output

    save_json(lockfile_json, outpath, args.indent)

    return 0


def main():
    args = make_parser().parse_args()
    return main_impl(args)


if __name__ == "__main__":
    main()

# Local Variables:
# mode: python-ts
# End:
