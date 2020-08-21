import argparse
import functools
import os
import sys

import gcn.voeventclient
from hop import auth
from hop import io

from . import constant
from . import utils


def _add_parser_args(parser):
    """
        adding parser arguments
    """
    utils.add_common_arguments(parser)

    parser.add_argument(
        "--hosts", default=constant.DHL, help="Comma separated list of GCN hosts."
    )
    parser.add_argument(
        "-p", "--port", default=constant.PORT, type=int, help="GCN port"
    )


def _main(args):
    """Stream GCN alerts to Hopskotch.
    """
    #  Line buffer stdout and stderr
    sys.stdout = os.fdopen(sys.stdout.fileno(), "w", buffering=1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), "w", buffering=1)

    hopUrl = args.hop_url + "gcn"
    hopConfFile = os.path.expanduser(args.config)
    host = tuple(args.hosts.split(","))
    port = args.port

    print("gcn2hop starting")
    print("GCN host list:      %s" % repr(host))
    print("GCN port:           %d" % port)
    print("Hop server URL:  %s" % hopUrl)
    print("Hop config file: %s\n" % hopConfFile)

    """
    What is the best way to clean up if gcn.voeventclient.listen returns
    or if we lose our connection to hop?

    For now, assume that it does something sensible and exit.
    """
    stream = io.Stream(auth=auth.load_auth(hopConfFile))
    sink = stream.open(hopUrl, "w")
    try:
        gcn.voeventclient.listen(
            host=host, port=port, handler=functools.partial(utils.writeTohop, sc=sink)
        )
    except KeyboardInterrupt:
        sink.close()
    except Exception:
        sink.close()
        raise
