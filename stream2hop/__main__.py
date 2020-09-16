import argparse

from hop.utils import cli as cli_utils

from . import __version__
from . import gcn
from . import tns


def add_commands():
    """Add commands.
    """
    parser = argparse.ArgumentParser(
        prog="stream2hop", formatter_class=cli_utils.SubcommandHelpFormatter
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s version {__version__}",
    )
    #  set up subparser
    subparser = parser.add_subparsers(title="commands", metavar="<command>", dest="cmd")
    subparser.required = True

    #  register commands
    p = cli_utils.append_subparser(subparser, "gcn", gcn._main)
    gcn._add_parser_args(p)

    p = cli_utils.append_subparser(subparser, "tns", tns._main)
    tns._add_parser_args(p)

    return parser


def main(args=None):
    """Stream GCNs or TNS objects to hop.
    """
    parser = add_commands()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
