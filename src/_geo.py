from typing import Literal

import httpx
import orjson
from haversine import Unit
from haversine import Direction
from haversine import inverse_haversine

from ._http import fetch_bulk


# OSM_REVERSE_BASE = "https://nominatim.openstreetmap.org/reverse?lat=<value>&lon=<value>&<params>"
# TIGER_WEB = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/1/query"

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

    url = "https://nominatim.openstreetmap.org/search"

    headers = {"user-agent": "Domus Python API"}

    req = httpx.Request("GET", url, params=params, headers=headers)
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

    url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "user-agent": "My-Simple-RealEstate-App"
    }

    req = httpx.Request("GET", url, params=params, headers=headers)
    
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

    url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/1/query"

    headers = {
        "user-agent": "My-Simple-RealEstate-App",
        "content-type": "application/x-www-form-urlencoded"
    }

    req = httpx.Request("POST", url, data=payload, headers=headers)
    
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


def get_commutes(start: tuple[float, float], start_name: str, destinations: list[dict], **kwargs):
    """
    Compares the driving distance and duration from a starting location to multiple destinations using the OSRM API.

    Parameters
    -----------
    
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


def get_bounding_box(latitude, longitude, radius, unit:Unit=Unit.MILES):
    north_point = inverse_haversine((latitude, longitude), radius, Direction.NORTH, unit=unit)
    south_point = inverse_haversine((latitude, longitude), radius, Direction.SOUTH, unit=unit)
    east_point = inverse_haversine((latitude, longitude), radius, Direction.EAST, unit=unit)
    west_point = inverse_haversine((latitude, longitude), radius, Direction.WEST, unit=unit)

    return {
        "north": north_point[0],
        "south": south_point[0],
        "east": east_point[1],
        "west": west_point[1],
    }


def string_to_polygon_tuples(polygon_str):
    if polygon_str.startswith("clipPolygon="):
        polygon_str = polygon_str.replace("clipPolygon=", "")
    
    polygon_groups = polygon_str.split(':')
    
    polygons = []
    
    for group in polygon_groups:
        if group:
            points = group.split('|')
            
            points = [point for point in points if point]
            
            try:
                polygon = [tuple(map(float, point.split(','))) for point in points]
            except ValueError as e:
                raise e
            
            polygons.append(polygon)
    
    return polygons


def polygon_tuples_to_string(polygons):
    polygon_strings = []
    
    for polygon in polygons:
        point_strings = [','.join(map(str, point)) for point in polygon]
        
        polygon_string = '|'.join(point_strings)
        
        polygon_strings.append(polygon_string + '|:')
    
    final_string = ''.join(polygon_strings)
    
    return f"clipPolygon={final_string}"





class Mapbox:
    def __init__(self, token:str):
        """
        DON'T USE THIS. I think I'm going to remove it
        """
        self.token = token.strip()

    def directions(self, start_lat:float, start_lon:float, end_lat:float, end_lon:float, steps=False, **kwargs):
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_lon},{start_lat};{end_lon},{end_lat}"

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

