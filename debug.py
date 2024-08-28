import httpx
import orjson
from flask import request
from flask.app import Flask
from flask.json import jsonify
from flask.templating import render_template
from flask.helpers import url_for
from flask_assets import Environment, Bundle

from src.api import Redfin

app = Flask(__name__)
# app.config["JSON_SORT_KEYS"] = False


assets = Environment(app)
scss = Bundle('style.scss',filters='pyscss',output='style.css')
assets.register('style',scss)

@app.context_processor
def inject_dict_for_all_templates():
    return {}

@app.route("/")
def index():
    url = ""
    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.5",
        "accept-encoding": "gzip, deflate, br, zstd",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "host": "www.redfin.com",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }

    
    redfin = Redfin()

    # data = redfin.search()
    # data = redfin.map_search((42.221805, -88.23305500000001))
    # data = redfin.region_search(18063, "zipcode")
    data = redfin.query_region("Crystal Lake, IL")

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
    
    

if __name__ == "__main__":
    app.run("127.0.0.1", port=5000, debug=True)