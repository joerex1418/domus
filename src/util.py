import json
from pathlib import Path

# import orjson

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