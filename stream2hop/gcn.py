import os
import sys
import logging

import gcn.voeventclient
from hop import auth
from hop import io
from hop import models

from . import constant
from . import utils


logger = logging.getLogger("stream2hop")


def write_to_hop(sink):
    """A gcn.vovent.listen handler to write gcn packets to hop.

    It takes an open connection to a hop stream, and returns a
    handler for use within gcn.voevent.listen to handle incoming GCNs.

    """
    def hop_handler(payload, root):
        voevent = models.VOEvent.load(payload)
        sink.write(voevent)

    return hop_handler


def _add_parser_args(parser):
    """Adding parser arguments.
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
    # set up logging
    logging.basicConfig(
        level=utils.get_log_level(args.verbose),
        format="%(asctime)s | gcn2hop : %(levelname)s : %(message)s",
    )

    # Line buffer stdout and stderr
    sys.stdout = os.fdopen(sys.stdout.fileno(), "w", buffering=1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), "w", buffering=1)

    hop_url = args.hop_url + "gcn"
    hop_conf_file = os.path.expanduser(args.config)
    host = tuple(args.hosts.split(","))
    port = args.port

    logger.info("starting up...")
    logger.info("GCN host list: %s" % repr(host))
    logger.info("GCN port:      %d" % port)
    logger.info("Hop server URL:  %s" % hop_url)
    logger.info("Hop config file: %s" % hop_conf_file)

    # open stream to hop
    stream = io.Stream(auth=auth.load_auth(hop_conf_file))
    sink = stream.open(hop_url, "w")
    try:
        gcn.voeventclient.listen(host=host, port=port, handler=write_to_hop(sink))
    except KeyboardInterrupt:
        pass
    except Exception:
        raise
    finally:
       sink.close()
