from typing import Literal

import httpx
import orjson

from ._api import HomesAPI
from ._http import send_request
from ._util import readjson
from .paths import QUERY_DIR
from .paths import JSON_DIR
from .geo import get_commutes


class Homes:
    def __init__(
            self, 
            favorite_locations: list[str] | None = None,
            commute_destinations: list[tuple[float, float]] | None = None
        ):
        """
        Domus

        Parameters
        ----------
        favorite_locations: list[str]

        commute_destinations: list[tuple[float, float]]
            Coordinates used when calculating the commutes to/from a specific property
        """

        if favorite_locations != None:
            self.favorite_locations = favorite_locations if isinstance(favorite_locations, list) else [favorite_locations]
            self.favorite_locations = [str(x) for x in self.favorite_locations]
        else:
            self.favorite_locations = []

        if commute_destinations != None:
            self.commute_destinations = commute_destinations if isinstance(commute_destinations, list) else [commute_destinations]
            self.commute_destinations = [x for x in self.commute_destinations]
        else:
            self.commute_destinations = []

        self.api = HomesAPI()


    def find_location(self, query:str, _type:Literal["city", "zipcode"]|None=None, **kwargs) -> dict:
        """
        Get the details & geography for a specific location
        """
        query = str(query).strip()

        req = self.api.request.autocomplete(query)

        r = send_request(req)

        data = orjson.loads(r.content)

        if _type == "city":
            _type = "City"
        elif _type == "zipcode":
            _type = "Zip Code"

        location_data = None

        if _type == None:
            location_data = data.get("suggestions", {}).get("places", [None])[0]
        
        else:
            for p in data.get("suggestions", {}).get("places", []):
                if _type == p["s"]:
                    location_data = p
                    break
        
        return location_data
    

    def find_location_results(self, query:str, **kwargs):
        """
        Get query results for requested location. 
        
        Similar to 'query_location()' method, but returns all
        results instead of just the first one 
        """
        query = str(query).strip()

        data = self.api.autocomplete(query)

        return data


    def query_search(self, query:str, **kwargs):
        """
        Standard property search tool
        """
        client = httpx.Client()

        query = str(query).strip()

        req_query_search = self.api.request.autocomplete(query)
        r = client.send(req_query_search)
        results_query_search = orjson.loads(r.content)

        loc = results_query_search.get("suggestions", {}).get("places", [None])[0]
        g = loc["g"]

        req_pindata = self.api.request.getpins(g, **kwargs)
        r = client.send(req_pindata)
        results_pindata = orjson.loads(r.content)

        listing_keys = [x["lk"]["key"] for x in results_pindata["pins"]]
        req_properties = self.api.request.getplacards(listing_keys)
        r = client.send(req_properties)
        results_properties = orjson.loads(r.content)

        client.close()

        return results_properties["placards"]


    def geography_search(self, geography, **kwargs):
        """
        Search with geography data for a given location
        """
        return self.api.getpins(geography, **kwargs)


    def coordinate_search(self, **kwargs):
        ...
    

    def polygon_search(self, polygon:str, **kwargs):
        ...


    def property_details(self, property_key:str, **kwargs):
        req = self.api.request.property_details(property_key)

        client = httpx.Client()

        r = client.send(req)
        data = orjson.loads(r.content)

        client.close()

        # normalized_data = readjson(JSON_DIR.joinpath("property_details.json"))

        return data

    
    def add_commute(self, lat:float, lon:float):
        """
        Add a destination to commute tracker
        """
        self.commute_destinations.append((lat, lon))

    def _property_amentities(self, property_details:dict):
        amentity_data = []
        for a_category in property_details["amenityCategories"]:
            for a_sub in a_category["subCategories"]:
                individual_amentities_str = a_sub.get("value")
                individual_amentities = a_sub.get("value", "").split(",")
                individual_amentities = [x.strip() for x in individual_amentities]
                amentity_data.append({
                    "category": a_category["name"],
                    "sub_category": a_sub["name"],
                    # "amenity_list": individual_amentities,
                    "amentiy_string": individual_amentities_str,
                })
        return amentity_data
