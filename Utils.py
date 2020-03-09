from scimma.client import models
from scimma.client import publish
from scimma.client import io

messageCount = 1

def writeToScimma(payload, root):
    voevent = models.VOEvent.from_xml(payload)
    broker = "kafka://scimma-server:9092/gcn"
    mode   = "w"
    config = "/root/shared/kafkacat.conf"
    s = io.Stream(config=config, format="json")
    sh = s.open(broker, mode=mode, format="json")
    sh.write(voevent.asdict())
    sh.close()
    print("Sent message %d" % messageCount)
    messageCount = messageCount + 1
