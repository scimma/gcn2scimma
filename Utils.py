from scimma.client import models
from scimma.client import publish
from scimma.client import io

messageCount   = 1
scimmaConfFile = ""
scimmaUrl      = ""

##
## There is no way to pass the GCN handler arguments, so using global variables.
## For now, one connection per event. Eventually, keep the connection to the
## SCiMMA server open.
##
def writeToScimma(payload, root):
    global messageCount
    global scimmaUrl
    global scimmaConfFile
    voevent = models.VOEvent.from_xml(payload)
    s = io.Stream(config=scimmaConfFile, format="json")
    sh = s.open(scimmaUrl, mode="w", format="json")
    sh.write(voevent.asdict())
    sh.close()
    print("Sent message %d" % messageCount)
    messageCount = messageCount + 1
