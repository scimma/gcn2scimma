import argparse
from . import __version__
from . import gcn2hop
from . import tns2hop


def append_subparser(subparser, cmd, func):
    """
        Add subparsers
    """
    assert func.__doc__, "empty docstring: {}".format(func)
    help_ = func.__doc__.split("\n")[0].lower().strip(".")
    desc = func.__doc__.strip()

    parser = subparser.add_parser(
        cmd,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help=help_,
        description=desc,
    )

    parser.set_defaults(func=func)
    return parser


def add_commands():
    """
        Add commands
    """
    parser = argparse.ArgumentParser(prog="stream2hop")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s version {__version__}",
    )
    #  set up subparser
    subparser = parser.add_subparsers(title="Commands", metavar="<command>", dest="cmd")
    subparser.required = True

    #  register commands
    p = append_subparser(subparser, "gcn", gcn2hop._main)
    gcn2hop._add_parser_args(p)

    p = append_subparser(subparser, "tns", tns2hop._main)
    tns2hop._add_parser_args(p)

    return parser


def main(args=None):
    """
        Stream GCNs or TNS objects to hop
    """
    parser = add_commands()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
