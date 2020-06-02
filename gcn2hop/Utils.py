from hop import models
from hop import io


class ScimmaConnection:
    def __init__(self, scimmaUrl, scimmaConfFile):
        self.scimmaUrl = scimmaUrl
        self.scimmaConfFile = scimmaConfFile
        self.msgCount = 0

    def open(self):
        self.stream = io.Stream(config=self.scimmaConfFile, format="json")
        self.streamHandle = self.stream.open(self.scimmaUrl, mode="w", format="json")

    def write(self, msg):
        self.streamHandle.write(msg)
        self.msgCount = self.msgCount + 1
        print("Sent message %d" % self.msgCount)

    def close(self):
        self.streamHandle.close()


def writeToScimma(payload, root, sc):
    """
        writeToScimma is used by the handler passed to gcn.voevent.listen.
        It takes the two arguments that are specified for a handler as well as
        a ScimmaConnection.
    """
    global messageCount
    global scimmaUrl
    global scimmaConfFile
    voevent = models.VOEvent.from_xml(payload)
    sc.write(voevent.asdict())
