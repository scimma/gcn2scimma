from hop import models
from hop import io
from . import constant


class HopConnection:
    def __init__(self, hopUrl, hopConfFile):
        self.hopUrl = hopUrl
        self.hopConfFile = hopConfFile
        self.msgCount = 0

    def open(self):
        self.stream = io.Stream(config=self.hopConfFile, format="json")
        self.streamHandle = self.stream.open(self.hopUrl, mode="w", format="json")

    def write(self, msg):
        self.streamHandle.write(msg)
        self.msgCount = self.msgCount + 1
        print("Sent message %d" % self.msgCount)

    def close(self):
        self.streamHandle.close()


def writeTohop(payload, root, sc):
    """
        writeTohop is used by the handler passed to gcn.voevent.listen.
        It takes the two arguments that are specified for a handler as well as
        a hopConnection.
    """
    global messageCount
    global hopUrl
    global hopConfFile
    voevent = models.VOEvent.from_xml(payload)
    sc.write(voevent.asdict())


def add_common_arguments(parser):

    parser.add_argument(
        "-s", "--hop_url", default=constant.HOP_URL, help="hop server URL"
    )
    parser.add_argument(
        "-F",
        "--config",
        default=constant.CONFIG_FILE,
        help="hop client configuration file",
    )
