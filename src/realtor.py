import httpx

from . import paths
from .util import readjson
from .util import readfile

def search(postalcode=None, city=None):
    # POSTALCODE
    # CITY
    
    url = "https://www.realtor.com/api/v1/rdc_search_srp"
    
    params = {
        "client_id": "rdc-search-for-sale-search",
        "schema": "vesta",
    }

    payload = readjson(paths.GRAPHQL_DIR.joinpath("realtor-ConsumerSearchQuery.json"))
    payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath("realtor-ConsumerSearchQuery.gql"))

    if postalcode != None:
        payload["variables"]["geoSupportedSlug"] = str(postalcode).strip()
        payload["variables"]["search_promotion"]["name"] = ["POSTALCODE"]
    elif city != None:
        payload["variables"]["search_promotion"]["name"] = ["CITY"]



    with httpx.Client() as client:
        r = client.post(url, params=params, json=payload)

        return r