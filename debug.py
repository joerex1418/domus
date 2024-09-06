import json

import rich
import httpx
import orjson
import polyline
from flask import request
from flask.app import Flask
from flask.json import jsonify
from flask.templating import render_template
from flask.helpers import url_for
from flask_assets import Environment, Bundle

from src import geo
from src import paths
from src._api import Realtor
from src._api import Zillow
from src._api import Redfin
from src._api import Homes
from src._http import send_request
from src._http import fetch_bulk
from src._api import readjson
from src._api import readfile
from src._domus import Domus
from src._util import copy_data


app = Flask(__name__)
# app.config["JSON_SORT_KEYS"] = False


assets = Environment(app)
scss = Bundle('style.scss',filters='pyscss',output='style.css')
assets.register('style',scss)

mapbox = geo.Mapbox(readfile("geoauth.txt"))

@app.context_processor
def inject_dict_for_all_templates():
    return {}


@app.route("/")
def index():
    zillow = Zillow()
    redfin = Redfin()
    realtor = Realtor()
    homes = Homes()

    domus = Domus()

    q = request.args.get("q")
    _type = request.args.get("type")

    # loc = domus.query_location(q)
    # data = domus.search_geography(loc["g"])
    # req = domus.api.request.getpins(loc["g"])
    # r = _send_request(req)

    # data = orjson.loads(r.content)
    # return domus.find_location(q, _type)
    data = domus.query_search(q, price_max=500000)
    data = domus.property_details(data[0]["propertyKey"]["key"])

    start = [41.69579266, -88.1128678]  # Commonwealth Dr
    dest1 = [41.77386435, -88.1595485]  # Stevens St
    dest2 = [42.205556, -88.26480364]   # Pearson Rd

    coords = data["propertyInfo"]["coordinate"]
    coords = (coords["lt"], coords["ln"])
    addr = data["propertyInfo"]["address"]["street"]
    
    commute = geo.get_commutes(start=coords, start_name=addr, destinations=[{"coords": dest1, "name": "640 Stevens St"}])
    
    data["commute"] = commute
    
    return data




@app.route("/homes/search")
def homessearch():
    query = request.args.get("q", request.args.get("query"))
    homes = Homes()

    r = send_request(homes.request.autocomplete(query))
    
    data = orjson.loads(r.content)

    gdata = data.get("suggestions", {}).get("places", [{}])[0].get("g")
    copy_data(gdata)

    return data

@app.route("/rfapi/<path:anything>")
def redfin(anything):
    url = f"https://www.redfin.com/{request.path.replace('/rfapi/', '')}"
    print(url)

    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.5",
        "accept-encoding": "gzip, deflate, br, zstd",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "host": "www.redfin.com",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }

    params = dict(request.args)

    r = httpx.get(url, params=params, headers=headers)
    data = orjson.loads(r.content.replace(b"{}&&", b""))

    return data

@app.route("/geosearch")
def geosearch():
    # data = geo.search(query=request.args.get("query"))

    start = [41.69579266, -88.1128678]  # Commonwealth Dr
    dest1 = [41.77386435, -88.1595485]  # Stevens St
    dest2 = [42.205556, -88.26480364]   # Pearson Rd

    data = geo.get_commutes(
        start=start, start_name="131 S Commonwealth Dr",
        destinations=[
            {"coords": dest1, "name": "640 Stevens St"},
            {"coords": dest2, "name": "940 Pearson Rd"},
        ]
    )

    return data
    
    

if __name__ == "__main__":
    app.run("127.0.0.1", port=5000, debug=True)