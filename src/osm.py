from typing import Literal

import httpx
import orjson


OSM_BASE = "https://nominatim.openstreetmap.org/search"
OSM_REVERSE_BASE = "https://nominatim.openstreetmap.org/reverse?lat=<value>&lon=<value>&<params>"
# polygon_geojson

def search(
        query:str=None,
        street_address:str=None,
        city:str=None,
        county:str=None,
        state:str=None,
        country:str=None,
        postalcode:str=None,
        format:Literal["jsonv2", "xml", "json", "geojson", "geocodejson"]="jsonv2",
        limit:int=10,
    ):
    params = {
        "query": query,
        "street": street_address,
        "city": city,
        "county": county,
        "state": state,
        "country": country,
        "postalcode": postalcode,
        "format": format,
        "limit": limit,
    }

    r = httpx.get(OSM_BASE, params=params)

    data = orjson.loads(r.content)

    return data