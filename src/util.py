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


