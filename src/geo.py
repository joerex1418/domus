import asyncio
from typing import Literal
from typing import overload as typ_overload

import httpx
import orjson


OSM_BASE = "https://nominatim.openstreetmap.org/search"
OSM_REVERSE_BASE = "https://nominatim.openstreetmap.org/reverse?lat=<value>&lon=<value>&<params>"
TIGER_WEB = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/1/query"

# ---------------------------- #
# Logging
# ---------------------------- #
def log_response(r:httpx.Response):
    if r.status_code in (401, 403):
        colorize = color.red
    elif r.status_code in (400, 404):
        colorize = color.yellow
    elif r.status_code == 429:
        colorize = color.magenta
    else:
        colorize = color.bold
    
    print("{status_code} {urlhost}{urlpath}".format(
        status_code = colorize(f"[{r.status_code}]"),
        urlhost = color.dim(r.url.scheme + r.url.host),
        urlpath = color.magenta(r.url.path)
    ))


class _color:
    __slots__ = tuple()
    def __init__(self) -> None:
        pass
    def bold(self,s: str):
        return f"\033[1m{s}\033[0m"
    
    def dim(self,s: str):
        return f"\033[2m{s}\033[0m"
    
    def underline(self,s: str):
        return f"\033[4m{s}\033[0m"
    
    def italic(self,s: str):
        return f"\033[3m{s}\033[0m"
    
    def yellow(self,s: str):
        return f"\033[93m{s}\033[0m"
    
    def cyan(self,s: str):
        return f"\033[96m{s}\033[0m"
    
    def magenta(self,s: str):
        return f"\033[35m{s}\033[0m"
    
    def bright_magenta(self,s: str):
        return f"\033[95m{s}\033[0m"
    
    def red(self,s: str):
        return f"\033[31m{s}\033[0m"
    
    def bright_red(self,s: str):
        return f"\033[91m{s}\033[0m"
    
    def green(self,s: str):
        return f"\033[92m{s}\033[0m"
    
    def blue(self,s: str):
        return f"\033[34m{s}\033[0m"
    
    def bright_yellow(self,s: str):
        return f"\033[93m{s}\033[0m"

color = _color()




# ---------------------------- #
# Async Functions
# ---------------------------- #
async def _fetch_request(client:httpx.AsyncClient, req:httpx.Request, **kwargs):
    if kwargs.get("rebuild_with_client") == True:
        req = client.build_request(req.method, req.url, headers=req.headers)
    
    r = await client.send(req)
    
    if r.status_code != 200:
        log_response(r)

        return r
    
    return r

async def _fetch_bulk(request_list:list[httpx.Request], **kwargs):
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=500)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = (asyncio.create_task(_fetch_request(client, req, **kwargs)) for req in request_list)
        responses = await asyncio.gather(*tasks)
        return responses

def fetch_bulk(request_list:list[httpx.Request], **kwargs) -> list[httpx.Response]:
    if isinstance(request_list, httpx.Request):
        request_list = [request_list]
    return asyncio.run(_fetch_bulk(request_list, **kwargs))



def search(*,
        query:str|None=None,
        street_address:str|None=None,
        city:str|None=None,
        county:str|None=None,
        state:str|None=None,
        country:str|None=None,
        postalcode:str|None=None,
        fmt:Literal["jsonv2", "xml", "json", "geojson", "geocodejson"]="jsonv2",
        limit:int=10,
        **kwargs
    ):
    
    if query != None:
        params = {
            "q": query,
            "format": fmt,
            "limit": limit,
        }
    else:
        params = {
            "street": street_address,
            "city": city,
            "county": county,
            "state": state,
            "country": country,
            "postalcode": postalcode,
            "format": fmt,
            "limit": limit,
        }

    headers = {
        "user-agent": "My-Simple-RealEstate-App"
    }

    req = httpx.Request("GET", OSM_BASE, params=params, headers=headers)
    if kwargs.get("req_only") == True:
        return req
    
    with httpx.Client() as client:
        r = client.send(req)

    data = orjson.loads(r.content)

    return data


def polygon_city(city, state=None, county=None, **kwargs):
    """
    Get the boundary coordinates for a city
    """
    params = {
        "city": city,
        "county": county,
        "state": state,
        "country": "usa",
        "format": "jsonv2",
        "email": "joe.rechenmacher@gmail.com",
        "polygon_geojson": "1",
    }

    headers = {
        "user-agent": "My-Simple-RealEstate-App"
    }

    req = httpx.Request("GET", OSM_BASE, params=params, headers=headers)
    
    if kwargs.get("req_only") == True:
        return req

    with httpx.Client() as client:
        r = client.send(req)

    data = orjson.loads(r.content)

    geometry = None

    if len(data) > 0:
        geometry = data[0].get("geojson", {})

    return geometry


def polygon_zipcode(zcta, **kwargs):
    """
    Get the boundary coordinates for a zip/postal code
    """
    payload = {
        "where": "",
        "text": str(zcta),
        "objectIds": "",
        "timeRelation": "esriTimeRelationOverlaps",
        "geometry": "",
        "geometryType": "esriGeometryPolygon",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": "",
        "units": "esriSRUnit_Foot",
        "outFields": "",
        "returnGeometry": True,
        "returnTrueCurves": False,
        "geometryPrecision": "",
        "returnIdsOnly": False,
        "returnCountOnly": False,
        "outStatistics": "",
        "returnZ": False,
        "returnM": False,
        "gdbVersion": "",
        "historicMoment": "",
        "returnDistinctValues": False,
        "returnExtentOnly": False,
        "sqlFormat": None,
        "featureEncoding": "esriDefault",
        "f": "geojson"
    }

    headers = {
        "user-agent": "My-Simple-RealEstate-App",
        "content-type": "application/x-www-form-urlencoded"
    }

    req = httpx.Request("POST", TIGER_WEB, data=payload, headers=headers)
    
    if kwargs.get("req_only") == True:
        return req

    with httpx.Client() as client:
        r = client.send(req, follow_redirects=True)

    data = orjson.loads(r.content)

    geometry = None

    if len(data["features"]) > 0:
        geometry = data["features"][0].get("geometry")

    return geometry


def directions(start_coords:tuple[float, float], end_coords:tuple[float, float], steps=False, **kwargs):
    url = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}".format(
        start_coords[1],
        start_coords[0],
        end_coords[1],
        end_coords[0],
    )

    params = {
        "language": "en",
        "overview": False,
        "steps": steps,
    }

    req = httpx.Request("GET", url, params=params)
    
    if kwargs.get("req_only") == True:
        return req
    
    with httpx.Client() as client:
        r = client.send(req)
    
    data = orjson.loads(r.content)

    return data


def distance_comparison(start: tuple[float, float], start_name: str, destinations: list[dict], **kwargs):
    """
    Compares the driving distance and duration from a starting location to multiple destinations using the OSRM API.

    ## Parameters
    
    start : tuple[float, float]
        A tuple containing the latitude and longitude of the starting location.
        
    start_name: str
        A name or label for the starting location, used in the output data.
        
    destinations: list[dict]
        A list of dictionaries where each dictionary represents a destination.
        Each dictionary should have the following keys:
            - 'coords': A tuple[float, float] containing the latitude and longitude of the destination.
            - 'name': A string representing the name or label of the destination.
        
    **kwargs: dict
        Optional keyword arguments:
            - 'req_only': bool
                If True, the function will return a list of prepared requests instead of making the API calls.

    """
    url_template = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}.json"
    
    reqlist = []
    
    for i, dest in enumerate(destinations):
        dest_coords = dest['coords']
        dest_name = dest['name']
        
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "dest-name": dest_name,
            "dest-num": str(i + 1),
        }
        
        req = httpx.Request("GET", url_template.format(start[1], start[0], dest_coords[1], dest_coords[0]), headers=headers)
        reqlist.append(req)
    
    if kwargs.get("req_only") == True:
        return reqlist
    
    responses = fetch_bulk(reqlist)
    
    data = []
    for r in sorted(responses, key=lambda x: int(x.request.headers.get("dest-num", 0))):
        routes = orjson.loads(r.content)
        if len(routes.get("routes", [])) > 0:
            distance_mi = routes["routes"][0]["distance"] * 0.000621371
            duration_min = routes["routes"][0]["duration"] / 60
            
            route_data = routes["routes"][0]
            route_data["distance_mi"] = round(distance_mi, 1)
            route_data["duration_min"] = round(duration_min, 1)
            route_data["dest_name"] = r.request.headers.get("dest-name")
            route_data["route_name"] = "{} to {}".format(start_name, r.request.headers.get("dest-name"))
            
            data.append(route_data)

    return data


class Mapbox:
    def __init__(self, token:str):
        """
        DON'T USE THIS. I think I'm going to remove it
        """
        self.token = token.strip()

    def directions(self, start_lat:float, start_lon:float, end_lat:float, end_lon:float, steps=False, **kwargs):
        url = "https://api.mapbox.com/directions/v5/mapbox/driving/{},{};{},{}".format(
            start_lon,
            start_lat,
            end_lon,
            end_lat,
        )

        params = {
            "access_token": self.token,
            "alternatives": False,
            "geometries": "geojson",
            "language": "en",
            "overview": "full",
            "steps": steps,
        }

        req = httpx.Request("GET", url, params=params)
        
        if kwargs.get("req_only") == True:
            return req
        
        with httpx.Client() as client:
            r = client.send(req)
        
        print(r.url)

        data = orjson.loads(r.content)

        return data

