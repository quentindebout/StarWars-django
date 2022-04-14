import requests
import json
from .settings import SWAPI_URL
from .models import DownloadedDataset


def fetch_all_data(type):
    """
    fetch all pages of one type on SWAPI

    :param type: string indicating the type of star wars object ('people', 'planets', ...)
    :return: list of dict. Each dict containing data about one instance of the object
    """
    url = SWAPI_URL + type
    next_page = True
    data = []
    # we need multiple requests to swapi to get all the data
    # it's not possible to get all data in one request with current API
    while next_page:

        # This may trigger all kind of exception. They are caught in the view.
        response = requests.get(url)

        # This will trigger an exception if status code 4xx or 5xx.
        response.raise_for_status()

        content = json.loads(response.text)

        data = data + content["results"]

        if bool(content["next"]):
            url = content["next"]
        else:
            next_page = False

    return data


def merge_and_transform(people, planets):
    """

    :param people: list of dict of people as from SWAPI
    :param planets: list of dict of planets as from SWAPI
    :return: list of dict of people transformed
    """
    for person in people:
        person.pop('films')
        person.pop('species')
        person.pop('vehicles')
        person.pop('starships')
        person.pop('url')
        person.pop('created')
        person['date'] = person.pop('edited')[:10]

        for planet in planets:
            if planet["url"] == person["homeworld"]:
                person["homeworld"] = planet["name"]

                break

    return people


def store_data(content):
    """
    :param content: string in csv format
    :return:
    """

    d = DownloadedDataset(csv=content)
    d.save()

