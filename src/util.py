import json
from pathlib import Path

from haversine import Unit
from haversine import Direction
from haversine import inverse_haversine

def savejson(obj, filepath):
    if isinstance(filepath, str):
        filepath = filepath.removesuffix(".json") + ".json"

    filepath = Path(filepath).resolve()

    with filepath.open("w+") as fp:
        return json.dump(obj, fp)

def readjson(jsonfile):
    if isinstance(jsonfile, str):
        jsonfile = jsonfile.removesuffix(".json") + ".json"

    jsonfile = Path(jsonfile).resolve()

    with jsonfile.open("r") as fp:
        return json.load(fp)
    
def readfile(filepath):
    filepath = Path(filepath).resolve()

    with filepath.open("r") as fp:
        return fp.read()
    

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
