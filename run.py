import json

import rich
import httpx
import orjson

from src import _geo
from src._api import RealtorAPI
from src._api import ZillowAPI
from src._api import RedfinAPI
from src._api import HomesAPI
from src._util import readjson
from src._util import readfile
from src._util import savejson


realtor = RealtorAPI()
zillow = ZillowAPI()
redfin = RedfinAPI()
homes = HomesAPI()


with httpx.Client() as client:
    req = homes.request.autocomplete("Cary, IL")
    r = client.send(req)
    data = r.json()
    
    req = homes.request.getpins(data["suggestions"]["places"][0]["g"])
    r = client.send(req)
    data = r.json()

    listing_keys = [x["lk"]["key"] for x in data["pins"]]
    req = homes.request.getplacards(listing_keys)
    r = client.send(req)
    data = r.json()
    

# properties: list[dict] = data["properties"]

with open("temp2.json", "wb+") as fp:
    fp.write(orjson.dumps(data))

# with open("temp3.json", "wb+") as fp:
#     property_id = properties[0]["property_id"]
#     # property_id = properties[0]["listing_id"]
#     property_data = realtor.property_details(property_id)
#     fp.write(orjson.dumps(property_data))