import base64

import boto3
from botocore.exceptions import ClientError
import toml

from . import constant


def add_common_arguments(parser):
    parser.add_argument(
        "-s", "--hop-url", default=constant.HOP_URL, help="hop server URL"
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


def write_config(location, creds):
    """Writes configurations file.

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
