import argparse
from . import Utils as ut
from twisted.internet import task, reactor
from datetime import datetime, timedelta
import requests
import json
import csv
from io import StringIO
from urllib.parse import urljoin
import os


def _add_parser_args(parser):
    """
        adding parser arguments
    """
    ut.add_common_arguments(parser)
    parser.add_argument("--api_key", help="TNS Bot's api key")


def search(url, json_list, api_key):
    """
      Search for objects in TNS

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
    """
      Get TNS object details

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


def fix_photometry(object, parameters_list):
    """
      Add additional information for abbreviated data

      Args:
        object: the TNS object
        parameters_list: the additional information about the abbreviations

      Returns:
        the modified object
    """

    for photometry in object["photometry"]:
        photometry["instrument"]["description"] = parameters_list["instruments"][
            str(photometry["instrument"]["id"])
        ]
        photometry["telescope"]["description"] = parameters_list["telescopes"][
            str(photometry["telescope"]["id"])
        ]
        photometry["filters"]["description"] = parameters_list["filters"][
            str(photometry["filters"]["id"])
        ]

    return object


def fix_spectra(object, parameters_list):
    """
      Add additional information for abbreviated data

      Args:
        object: the TNS object
        parameters_list: the additional information about the abbreviations

      Returns:
        the modified object
    """

    for spectra in object["spectra"]:

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

    return object


def get_new_data(hop_url, config, api_key):
    """
      Retrieve new TNS objects

      Args:
        hop_url: hop URL that will be used to publish data to it
        config: configurations to access hop URL

      Returns:
        None
    """

    url_tns_api = "https://wis-tns.weizmann.ac.il/api/get/"

    #  every 3 hours
    days_ago = 0.125
    date = str(datetime.utcnow() - timedelta(days=days_ago))
    print("Running on: " + date)
    #  Set search parameter
    search_obj = {"public_timestamp": date}
    response = search(url_tns_api, search_obj, api_key)

    if None not in response:
        print("hop_url = " , hop_url)
        #  New data is retrieved, open a stream with hop
        sC = ut.HopConnection(hop_url, config)
        sC.open()

        #  Read parameters file
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../parameters.json")
        parameters_list = json.load(open(filename, "r"))["data"]
        objects_list = json.loads(response.text)["data"]["reply"]
        print("Objects: \n", json.dumps(objects_list, indent=4))
        for object in objects_list:
            get_obj = {
                "objname": object["objname"],
                "photometry": "1",
                "spectra": "1",
                "classification": "1",
                "discovery": "1",
                "AT": "1",
            }
            response = get_object(url_tns_api, get_obj, api_key)

            if response:
                object_data = json.loads(response.text)["data"]["reply"]
                object_data = fix_photometry(object_data, parameters_list)
                object_data = fix_spectra(object_data, parameters_list)
                object_data = {"format": "BLOB", "content": object_data}
                sC.write(json.dumps(object_data, indent=4))
        sC.close()
    else:
        print("Nothing to do\n")

    pass


def get_astronotes(hop_url, config, api_key):
    """
        Get the latest astronotes in the previous day

        Args:
            hop_url: hop URL that will be used to publish data to it
            config: configurations to access hop URL

        Returns:
            None
    """
    date = datetime.today().strftime("%Y-%m-%d")
    print("Astronotes on: ", date)
    astronotes_url = "https://wis-tns.weizmann.ac.il/astronotes"
    params = {"date_start[date]": date, "format": "csv"}
    response = requests.get(astronotes_url, params=params, stream=True)
    csv_reader = csv.reader(StringIO(response.content.decode("utf-8")), delimiter=",")
    
    print("Astronotes: ", csv_reader)

    line_count = 0
    headlines = []

    for row in csv_reader:
        if line_count == 0:
            for headline in row:
                headlines.append(headline)
            line_count += 1
        else:
            content = {headline: col for headline, col in zip(headlines, row)}
            json_object = {"format": "BLOB", "content": content}
            #  New data is retrieved, open a stream with hop
            sC = ut.HopConnection(hop_url, config)
            sC.open()
            sC.write(json.dumps(json_object, indent=4))
            sC.close()
    pass


def _main(args=None):
    """
      Stream TNS objects to hop kafka server
    """
    if not args:
        parser = argparse.ArgumentParser()
        _add_parser_args(parser)
        args = parser.parse_args()

    #  3 hours
    obj_timeout = 3 * 60.0 * 60.0
    #  everyday
    astro_timeout = 24 * 60.0 * 60.0

    hop_url = args.hop_url + "tns"
    task.LoopingCall(get_new_data, hop_url, args.config, args.api_key).start(
        obj_timeout
    )
    task.LoopingCall(get_astronotes, hop_url, args.config, args.api_key).start(
        astro_timeout
    )
    reactor.run()
