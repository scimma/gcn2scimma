#!/usr/bin/python3
from optparse import OptionParser
import gcn.voeventclient
from . import Utils as ut
import sys
import os


def  main():
    ## Line buffer stdout and stderr
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

    ##
    ## Parse options.
    ##
    dhl="209.208.78.170,45.58.43.186,50.116.49.68,68.169.57.253"
    hlHelp = "Comma separated list of GCN hosts."
    cHelp  = "SCiMMA client configuration file"
    sHelp  = "SCiMMA server URL"
    sUrl   = "kafka://scimma-server:9092/gcn"
    p = OptionParser(usage="Usage: %prog [options]")
    p.add_option("",   "--scimma", dest="scimmaUrl", default=sUrl, help=sHelp)
    p.add_option("-F", "--config", dest="scimmaConfFile", default="~/shared/kafkacat.conf", help=cHelp)
    p.add_option("",   "--hosts",  dest="hostList", default=dhl, help=hlHelp)
    p.add_option("",   "--port",   dest="portString", default="8099", help="GCN port")
    (o, a) = p.parse_args()

    scimmaUrl      = o.scimmaUrl
    scimmaConfFile = os.path.expanduser(o.scimmaConfFile)
    host           = tuple(o.hostList.split(','))
    port           = int(o.portString)

    print("gcn2scimma starting")
    print("GCN host list:      %s"   % repr(host))
    print("GCN port:           %d"   % port)
    print("SCiMMA server URL:  %s"   % scimmaUrl)
    print("SCiMMA config file: %s\n" % scimmaConfFile)

    ##
    ## What is the best way to clean up if gcn.voeventclient.listen returns
    ## or if we lose our connection to SCiMMA?
    ##
    ## For now, assume that it does something sensible and exit.
    ##
    sC = ut.ScimmaConnection(scimmaUrl, scimmaConfFile)
    sC.open()
    try:
        gcn.voeventclient.listen(host=host, port=port, handler=lambda x,y : ut.writeToScimma(x, y, sC))
    except KeyboardInterrupt:
        print("Recieved Keyboard Interrupt. It's a python thing.")
    except:
        print("Received an unexpected exception.")

    exit(0)

if __name__ == "__main__":
    main()
