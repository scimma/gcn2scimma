import os
from stream2hop import Utils as ut
import json

region = "us-west-2"
cred_secret_name = "dev-gcn2hop-hopcreds"
tns_api_key_secret_name = "tns_api_key"
configDir = "/root/share"
Location = "%s/kafkacat.conf" % configDir


os.system("mkdir -p %s" % configDir)
creds = ut.get_secret(cred_secret_name)
if creds is not None:
    creds_json = json.loads(creds)
    values = creds_json["creds"].split(":")
    creds = {"user": values[0], "pass": values[1]}
    ut.writeConfig(Location, creds)
tns_api_key = json.loads(ut.get_secret(tns_api_key_secret_name))["key"]
run = os.system("stream2hop tns -F %s --api_key=%s" % (Location, tns_api_key))
