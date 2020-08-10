import os
from stream2hop import Utils as ut
import json
import sys

region = "us-west-2"
cred_secret_name = "dev-gcn2hop-hopcreds"
tns_api_key_secret_name = "tns_api_key"
config_dir = "/root/share"
location = "%s/config.toml" % config_dir


os.system(f"mkdir -p {config_dir}")
creds = ut.get_secret(cred_secret_name)

if creds is None:
    print("Error: Credentials cannot be empty")
    sys.exit(1)

creds_json = json.loads(creds)
values = creds_json["creds"].split(":")
creds = {"user": values[0], "pass": values[1]}
ut.writeConfig(location, creds)

tns_api_key = json.loads(ut.get_secret(tns_api_key_secret_name))["key"]
run = os.system(f"stream2hop tns -F {location} --api_key={tns_api_key}")
