import rich
import httpx
import orjson
from flask import request
from flask.app import Flask
from flask.json import jsonify
from flask.templating import render_template
from flask.helpers import url_for
from flask_assets import Environment, Bundle

from src.api import Realtor
from src.api import Zillow
from src.api import Redfin
from src.api import _send_request
from src.api import readjson
from src import paths

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
    zillow = Zillow()
    redfin = Redfin()

    data = zillow.region_search("Cary, IL", "city", has_pool=True)

    # data = zillow.autocomplete_results("Cary, IL")

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