## stream2hop

This program connects to several data sources (GCN/TNS) to relay them to the [SCiMMA](https://scimma.org/) HOPSKOTCH network
using the [HOP Client Library](https://github.com/scimma/hop-client).

### GCN

Uses [pygcn](https://github.com/lpsinger/pygcn) to read [VOEvent](http://www.ivoa.net/documents/VOEventTransport/) messages from
the [GCN/TAN servers](https://gcn.gsfc.nasa.gov/voevent.html).

### TNS

Uses the TNS REST API to fetch TNS objects and store them into HOPSKOTCH.
