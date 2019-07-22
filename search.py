import requests
import csv
import collections
import time
import json
import os


CountryCityCoords = collections.namedtuple(
    "CountryCityCoords", ["country_name", "capital_name", "capital_lat", "capital_lng"]
)


G_KEY = os.getenv("G_KEY")
G_PLACE_API = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&keyword=starbucks&key={key}"
G_PLACE_NEXT_PAGE_TOKEN = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={page_token}&key={key}"


def get_near_coords(lat: float, lng: float, offset=0.1):
    for r in [offset, -offset]:
        yield (lat + r, lng)
    for r in [offset, -offset]:
        yield (lat, lng + r)


def get_starbucks(lat, lng, radius=15000):
    results = []
    response = requests.get(
        G_PLACE_API.format(lat=lat, lng=lng, radius=radius, key=G_KEY)
    )
    results.extend(response.json()["results"])
    next_page_token = response.json().get("next_page_token")
    while True:
        if next_page_token is None:
            break
        # Sleeping for 3 seconds to wait for the results be prepared by Google.
        time.sleep(3)
        response = requests.get(
            G_PLACE_NEXT_PAGE_TOKEN.format(key=G_KEY, page_token=next_page_token)
        )
        next_page_token = response.json().get("next_page_token")
        results.extend(response.json()["results"])
    return results


def get_cities_coords():
    result = []
    with open("geo_capitals.json", "r") as f:
        data = json.loads(f.read())
        for row in data:
            result.append(
                CountryCityCoords._make(
                    [
                        row["CountryName"],
                        row["CapitalName"],
                        row["CapitalLatitude"],
                        row["CapitalLongitude"],
                    ]
                )
            )
    return result


class StarbucksCitySearcher(object):
    def __init__(self, e: CountryCityCoords):
        self.lat = float(e.capital_lat)
        self.lng = float(e.capital_lng)
        self.places_ids = set()

    def _search(self, lat: float, lng: float):
        results = get_starbucks(lat, lng)
        for r in results:
            self.places_ids.add(r["id"])

    def search(self):
        for (lat, lng) in get_near_coords(self.lat, self.lng):
            self._search(lat, lng)
        return len(self.places_ids)


def main():
    cities_coords = get_cities_coords()
    with open("data.csv", mode="w") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for e in cities_coords:
            n_starbucks = StarbucksCitySearcher(e).search()
            print(f"Got {n_starbucks} for {e.capital_name}")
            writer.writerow([e.country_name, e.capital_name, n_starbucks])


if __name__ == "__main__":
    main()
