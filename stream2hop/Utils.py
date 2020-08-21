from hop import auth
from hop import models
from hop import io
from . import constant
import boto3
import base64
from botocore.exceptions import ClientError
import toml


class HopConnection:
    def __init__(self, hopUrl, hopConfFile):
        self.hopUrl = hopUrl
        self.hopConfFile = hopConfFile
        self.msgCount = 0

    def open(self):
        self.stream = io.Stream(auth=auth.load_auth(self.hopConfFile))
        self.streamHandle = self.stream.open(self.hopUrl, mode="w")

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
    voevent = models.VOEvent.load(payload)
    sc.write(voevent)


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


def get_secret(secret_name):
    """
        Get secret value from AWS
        Args:
            secret_name: secret name to fetch
        returns:
            secret value

    """
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    except ClientError as e:
        raise e

    if "SecretString" in get_secret_value_response:
        return get_secret_value_response["SecretString"]
    else:
        return base64.b64decode(get_secret_value_response["SecretBinary"])


def writeConfig(location, creds):
    """
        Writes configurations file
        Args:
            location: location for config file to be written at
            creds: dictionary of "user" for username and "pass" for password
    """
    with open(location, "w") as cfh:
        config = {
            "auth": {
                "username": creds["user"],
                "password": creds["pass"],
                "mechanism": "PLAIN",
                "ssl_ca_location": "/etc/pki/tls/certs/ca-bundle.trust.crt",
            }
        }
        toml.dump(config, cfh)
