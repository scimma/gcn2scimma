import os
import json
import sys

from stream2hop import utils


region = "us-west-2"
cred_secret_name = "dev-gcn2hop-hopcreds"
tns_api_key_secret_name = "tns_api_key"
config_dir = "/root/share"
location = "%s/config.toml" % config_dir

os.system(f"mkdir -p {config_dir}")
creds = utils.get_secret(cred_secret_name)

if creds is None:
    print("Error: Credentials cannot be empty")
    sys.exit(1)

creds_json = json.loads(creds)
values = creds_json["creds"].split(":")
creds = {"user": values[0], "pass": values[1]}
utils.writeConfig(location, creds)

tns_api_key = json.loads(utils.get_secret(tns_api_key_secret_name))["key"]
run = os.system(f"stream2hop tns -F {location} --api_key={tns_api_key}")
