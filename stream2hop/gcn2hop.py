#!/usr/bin/python3
import gcn.voeventclient
from . import Utils as ut
import sys
import os
from . import constant
import argparse


def _add_parser_args(parser):
    """
        adding parser arguments
    """
    ut.add_common_arguments(parser)

    parser.add_argument(
        "--hosts", default=constant.DHL, help="Comma separated list of GCN hosts."
    )
    parser.add_argument(
        "-p", "--port", default=constant.PORT, type=int, help="GCN port"
    )


def _main(args=None):
    """
    Stream GCNs to Hop kafka server

    """
    if not args:
        parser = argparse.ArgumentParser()
        _add_parser_args(parser)
        args = parser.parse_args()

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
    sC = ut.HopConnection(hopUrl, hopConfFile)
    sC.open()
    try:
        gcn.voeventclient.listen(
            host=host, port=port, handler=lambda x, y: ut.writeTohop(x, y, sC)
        )
    except KeyboardInterrupt:
        print("Recieved Keyboard Interrupt. It's a python thing.")
    except:
        print("Received an unexpected exception.")

    exit(0)
