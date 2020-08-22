import csv
from datetime import datetime
from io import StringIO
import json
import os
import time
from urllib.parse import urljoin

from hop import auth
from hop import io
import requests
import schedule

from . import utils


def _add_parser_args(parser):
    """adding parser arguments.
    """
    utils.add_common_arguments(parser)
    parser.add_argument("--api-key", help="TNS Bot's api key")
    parser.add_argument(
        "--params-file",
        default=os.path.join(os.path.dirname(__file__), "../parameters.json"),
        help="Path to parameters file."
    )


def search(url, json_list, api_key):
    """Search for objects in TNS.

    Args:
      url: TNS url
      json_list: parameters in the search query
      api_key: TNS bot's api key

    Return:
      search result

    """
    try:
        # url for search obj
        search_url = urljoin(url, "search")
        # construct the list of (key,value) pairs
        search_data = [
            ("api_key", (None, api_key)),
            ("data", (None, json.dumps(json_list))),
        ]
        # search obj using request module
        response = requests.post(search_url, files=search_data)
        return response
    except Exception as e:
        return [None, "Error message : \n" + str(e)]


def get_object(url, json_list, api_key):
    """Get TNS object details.

    Args:
      url: TNS URL
      json_list: parameters passed to TNS get API specifing the information needed
      api_key: TNS bot's api key

    Returns:
      Object's data

    """
    try:
        get_url = urljoin(url, "object")
        get_data = [
            ("api_key", (None, api_key)),
            ("data", (None, json.dumps(json_list))),
        ]
        response = requests.post(get_url, files=get_data)
        return response
    except Exception as e:
        return [None, "Error message : \n" + str(e)]


def fix_photometry(object_, parameters_list):
    """Add additional information for abbreviated data.

    Args:
      object_: the TNS object
      parameters_list: the additional information about the abbreviations

    Returns:
      the modified object

    """

    for photometry in object_["photometry"]:
        photometry["instrument"]["description"] = parameters_list["instruments"][
            str(photometry["instrument"]["id"])
        ]
        photometry["telescope"]["description"] = parameters_list["telescopes"][
            str(photometry["telescope"]["id"])
        ]
        photometry["filters"]["description"] = parameters_list["filters"][
            str(photometry["filters"]["id"])
        ]

    return object_


def fix_spectra(object_, parameters_list):
    """Add additional information for abbreviated data.

    Args:
      object_: the TNS object
      parameters_list: the additional information about the abbreviations

    Returns:
      the modified object

    """

    for spectra in object_["spectra"]:

        if "source_group" in spectra:
            spectra["source_group"]["description"] = parameters_list["groups"][
                str(spectra["source_group"]["id"])
            ]

        if "instrument" in spectra:
            spectra["instrument"]["description"] = parameters_list["instruments"][
                str(spectra["instrument"]["id"])
            ]

        if "telescope" in spectra:
            spectra["telescope"]["description"] = parameters_list["telescopes"][
                str(spectra["telescope"]["id"])
            ]

        if "assoc_groups" in spectra:
            for assoc_group in spectra["assoc_groups"]:
                assoc_group["description"] = parameters_list["groups"][
                    str(assoc_group["id"])
                ]

    return object_


def get_object_ID(object_name):
    url = "https://wis-tns.weizmann.ac.il/search"
    params = {"name": object_name, "format": "csv"}
    response = requests.get(url, params=params, stream=True)
    csv_reader = csv.reader(StringIO(response.content.decode("utf-8")), delimiter=",")
    next(csv_reader)  # remove header
    if csv_reader:
        return next(csv_reader)[0]
    else:
        return 0


def get_tns_objects(sink, api_key, parameters_list):
    """Retrieve new TNS objects.

    Args:
      sink: an open hop stream in write mode
      api_key: to connect to TNS

    """

    url_tns_api = "https://wis-tns.weizmann.ac.il/api/get/"

    date = datetime.today().strftime("%Y-%m-%d")
    print("Running on: " + date)
    #  Set search parameter
    search_obj = {"public_timestamp": date}
    response = search(url_tns_api, search_obj, api_key)

    if None not in response:
        #  Read parameters file
        objects_list = json.loads(response.text)["data"]["reply"]
        print("Objects: \n", json.dumps(objects_list, indent=4))
        for object_ in objects_list:
            get_obj = {
                "objname": object_["objname"],
                "photometry": "1",
                "spectra": "1",
                "classification": "1",
                "discovery": "1",
                "AT": "1",
            }
            response = get_object(url_tns_api, get_obj, api_key)

            #  New data is retrieved, write to hop
            if response:
                object_data = json.loads(response.text)["data"]["reply"]
                object_data = fix_photometry(object_data, parameters_list)
                object_data = fix_spectra(object_data, parameters_list)
                object_data["ID"] = get_object_ID(object_["objname"])
                object_data[
                    "full_object_name"
                ] = f"{object_['prefix']} {object_['objname']}"
                sink.write(object_data)
    else:
        print("Nothing to do\n")


def get_astronotes(sink, api_key):
    """Get the latest astronotes in the previous day.

    Args:
      sink: an open hop stream in write mode
      api_key: to connect to TNS

    """
    date = datetime.today().strftime("%Y-%m-%d")
    print("Astronotes on: ", date)
    astronotes_url = "https://wis-tns.weizmann.ac.il/astronotes"
    params = {"date_start[date]": date, "format": "json"}
    response = requests.get(astronotes_url, params=params, stream=True)
    astronotes_list = json.loads(response.content.decode("utf-8"))

    if not astronotes_list:
        return

    for astronote in astronotes_list.items():
        if astronote[1]:
            #  New data is retrieved, send to hop
            sink.write(astronote[1])


def job(sink, api_key, parameters_list):
    get_tns_objects(sink, api_key, parameters_list)
    get_astronotes(sink, api_key)


def _main(args):
    """Stream TNS objects to Hopskotch.
    """
    # load parameters file
    with open(args.params_file, "r") as f:
        parameters_list = json.load(f)["data"]

    # set up stream
    stream = io.Stream(auth=auth.load_auth(args.config))
    sink = stream.open(args.hop_url + "tns", "w")

    # schedule everyday
    exact_time = "23:00"
    #schedule.every().day.at(exact_time).do(job, sink, args.api_key, parameters_list)
    schedule.every().minute.do(job, sink, args.api_key, parameters_list)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception:
        raise
    finally:
        sink.close()
