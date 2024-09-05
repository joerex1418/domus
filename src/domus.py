from typing import Literal

import httpx

from .api import Homes


class Domus:
    def __init__(self, favorite_locations:list[str]|None=None):
        if favorite_locations != None:
            self.favorite_locations = favorite_locations if isinstance(favorite_locations, list) else [favorite_locations]
            self.favorite_locations = [str(x) for x in self.favorite_locations]
        else:
            self.favorite_locations = []

        self.api = Homes()

    def query_location(self, query:str, _type:Literal["city", "zipcode"]|None=None, **kwargs) -> dict:
        """
        Get the details/geography for a specific location
        """
        query = str(query).strip()

        data = self.api.autocomplete(query)

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
    
    def search_by_location(self, geography, **kwargs):
        return self.api.getpins(geography, **kwargs)
    
    def query_locations(self, query:str, **kwargs):
        """
        Get query results for requested location. 
        
        Similar to 'query_location()' method, but returns all
        results instead of just the first one 
        """
        query = str(query).strip()

        data = self.api.autocomplete(query)

        return data

    def track_commute(self, lat:float, lon:float):
        """
        TODO:
        Add a destination to commute tracker
        """
    