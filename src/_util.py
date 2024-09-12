import json
from pathlib import Path
from collections import UserDict

import orjson
from pyperclip import copy as pyperclip_copy

from .paths import JSON_DIR
from .paths import QUERY_DIR



def copy_data(data:list|dict):
    pyperclip_copy(json.dumps(data))


def savejson(obj, filepath):
    if isinstance(filepath, str):
        filepath = filepath.removesuffix(".json") + ".json"

    filepath = Path(filepath).resolve()

    with filepath.open("w+") as fp:
        return json.dump(obj, fp)


def savetxt(string: str, filepath):
    filepath = Path(filepath).resolve()

    with filepath.open("w+") as fp:
        return fp.write(string)


def readjson(jsonfile):
    if isinstance(jsonfile, str):
        jsonfile = jsonfile.removesuffix(".json") + ".json"

    jsonfile = Path(jsonfile).resolve()

    # with jsonfile.open("r") as fp:
    #     return json.load(fp)

    with jsonfile.open("rb") as fp:
        return orjson.loads(fp.read())
    


def readfile(filepath):
    filepath = Path(filepath).resolve()

    with filepath.open("r") as fp:
        return fp.read()
    

def read_graphql(s):
    return readfile(QUERY_DIR.joinpath(s))


def read_payload(s):
    return readjson(QUERY_DIR.joinpath(s))


def generate_uncommented_json():
    import commentjson
    for jsonfile_c in JSON_DIR.iterdir():
        if jsonfile_c.suffix.lower() == ".jsonc":
            with jsonfile_c.open("r") as fp_c:
                data = commentjson.load(fp_c)
            
            jsonfile = jsonfile_c.with_suffix(".json")
            with jsonfile.open("w+") as fp:
                json.dump(data, fp, indent=4)

def always_get(key, data: dict, default=None):
    """
    Always retrieve a value (event)
    """
    value = data.get(key, default)
    # If the value is not a dict or is None, return the default
    if value is None or not isinstance(value, dict):
        return default
    return value
