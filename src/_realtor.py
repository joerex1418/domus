import re
import json
import datetime as dt
from pathlib import Path
from typing import Literal

import httpx
from dateutil import relativedelta

# from . import paths
from .paths import JSON_DIR
from .paths import QUERY_DIR
from ._geo import get_bounding_box
from ._util import readfile
from ._util import readjson
from ._util import read_graphql
from ._util import read_payload
from ._util import always_get



class Realtor:
    def __init__(self) -> None:
        pass

    def map_search(
            self,
            coordinates:tuple[float],
            radius_mi=None,
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            sort_type:Literal["relevant"]=None
        ):

        req = self.request.map_search(
            coordinates, 
            radius_mi=radius_mi,
            primary=primary, 
            pending=pending, 
            contingent=contingent,
            limit=limit,
            sort_type=sort_type,
            )
        
        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = r.json()

        return rawdata


    def query_search(
            self,
            query_string,
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            offset=None,
            sort_type:Literal["relevant"]=None
        ):

        req = self.request.query_search(
            query_string=query_string, 
            primary=primary, 
            pending=pending, 
            contingent=contingent,
            limit=limit,
            offset=offset,
            sort_type=sort_type,
            )
        
        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = r.json()
        
        # data = rawdata.get("data", {}).get("home_search", {}).get("properties")
        # data = self._compact_search_data(rawdata)
        data = self.normalize.property_search(rawdata)

        return data


    def city_search(
            self,
            city, 
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            offset=None,
            sort_type:Literal["relevant"]=None
        ):

        req = Realtor.request.query_search(
            city, 
            primary=primary, 
            pending=pending, 
            contingent=contingent,
            limit=limit,
            offset=offset,
            sort_type=sort_type,
            )
        
        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = r.json()

        # data = self._compact_search_data(rawdata)

        return rawdata


    def generate_property_url(self, permalink: str):
        base_url = "https://www.realtor.com/realestateandhomes-detail"
        return f"{base_url}/{permalink}"
    
    @staticmethod
    def generate_custom_photo_url(og_url, width: int | None=None):
        if width != None:
            url_obj = httpx.URL(og_url)

            start_idx = url_obj.path.rfind("/") + 1
            
            urlpath = Path(url_obj.path[start_idx:])

            edited_url = f"{url_obj.scheme}://{url_obj.host}/" + urlpath.with_stem(urlpath.stem + f"-w{width}").name
            
            return edited_url
        
        else:
            return og_url

    @staticmethod
    def generate_custom_photo_url2(og_url: str, width: int | None):
        width = 960 if width == None else width
        width = str(width).strip()

        url_obj = httpx.URL(og_url)
        
        start_idx = url_obj.path.rfind("/") + 1

        urlpath = Path(url_obj.path[start_idx:])
        
        old_ending = f"s{urlpath.suffix}"
        new_ending = f"rd-w{width}{urlpath.suffix}"

        new_name = urlpath.name.replace(old_ending, new_ending)

        edited_url = f"{url_obj.scheme}://{url_obj.host}/" + new_name

        return edited_url
        

    def property_details(self, property_id):
        req = self.request.property_details(property_id)

        with httpx.Client() as client:
            r = client.send(req)

        rawdata = r.json()

        return rawdata


    def property_and_tax_history(self, property_id):
        req = self.request.property_and_tax_history(property_id)

        with httpx.Client() as client:
            r = client.send(req)

            rawdata = r.json()
        
            return rawdata
    

    def property_school_data(self, property_id):
        req = self.request.property_school_data(property_id)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = r.json()

        return rawdata


    def property_estimates(self, property_id, historical_year_start=None, historical_year_end=None, month_forecast_count=None):
        today = dt.date.today()

        if historical_year_start == None:
            historical_year_start = today.year - 3
        if historical_year_end == None:
            historical_year_end = today.year

        hist_year_min = f"{historical_year_start}-{today.month:02d}-01"
        hist_year_max = f"{today.year}-{today.month:02d}-01"

        if month_forecast_count == None:
            month_forecast_count = 3

        fcast_date = (today + relativedelta(months=month_forecast_count))
        fcast_date_str = fcast_date.strftime(r"%Y-%m-01")
        
        req = self.request.property_estimates(property_id, hist_year_min, hist_year_max, fcast_date_str)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = r.json()

        return rawdata


    def property_saves(self, property_id):
        req = self.request.property_saves(property_id)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = r.json()

        return rawdata
    

    def property_gallery(self, property_id):
        req = self.request.property_gallery(property_id)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = r.json()

        return rawdata


    class request:
        @staticmethod
        def map_search(
                coordinates:tuple[float],
                radius_mi=None,
                primary:bool=True,
                pending:bool=False,
                contingent:bool=False,
                limit:int=None,
                offset:int=None,
                sort_type=None,
            ):
            url = "https://www.realtor.com/api/v1/rdc_search_srp"
            
            params = {"client_id": "rdc-search-for-sale-search", "schema": "vesta"}

            payload = readjson(QUERY_DIR.joinpath(f"realtor-ConsumerSearchQuery.json"))
            payload["query"] = readfile(QUERY_DIR.joinpath(f"realtor-ConsumerSearchQuery.gql"))

            bbox = get_bounding_box(float(coordinates[0]), float(coordinates[1]), radius=radius_mi)
            payload["variables"]["query"]["boundary"] = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [bbox["west"], bbox["north"]],
                        [bbox["east"], bbox["north"]],
                        [bbox["east"], bbox["south"]],
                        [bbox["west"], bbox["south"]],
                        [bbox["west"], bbox["north"]],
                    ]
                ]
            }

            
            payload["variables"]["query"]["primary"] = primary
            payload["variables"]["query"]["pending"] = pending
            payload["variables"]["query"]["contingent"] = contingent
            
            limit = int(limit) if str(limit).isdigit() else 50
            sort_type = str(sort_type).lower() if sort_type != None else "relevant"

            payload["variables"]["limit"] = int(limit)
            # payload["variables"]["offset"] = int(offset)
            payload["variables"]["sort_type"] = sort_type


            req = httpx.Request("POST", url, params=params, json=payload)
            
            return req


        @staticmethod
        def polygon_search(
                coordinate_list:list[tuple[float]],
                radius_mi=None,
                primary:bool=True,
                pending:bool=False,
                contingent:bool=False,
                limit:int=None,
                offset:int=None,
                sort_type=None,
            ):
            url = "https://www.realtor.com/api/v1/rdc_search_srp"
            
            params = {"client_id": "rdc-search-for-sale-search", "schema": "vesta"}

            operation_name = "ConsumerSearchQuery"

            payload = readjson(QUERY_DIR.joinpath(f"realtor-{operation_name}.json"))
            payload["query"] = readfile(QUERY_DIR.joinpath(f"realtor-{operation_name}.gql"))

            # bbox = get_bounding_box(float(coordinates[0]), float(coordinates[1]), radius=radius_mi)
            payload["variables"]["query"]["boundary"] = {
                "type": "MultiPolygon",
                "coordinates": [coordinate_list]
            }

            
            payload["variables"]["query"]["primary"] = primary
            payload["variables"]["query"]["pending"] = pending
            payload["variables"]["query"]["contingent"] = contingent
            
            limit = int(limit) if str(limit).isdigit() else 50
            sort_type = str(sort_type).lower() if sort_type != None else "relevant"

            payload["variables"]["limit"] = int(limit)
            # payload["variables"]["offset"] = int(offset)
            payload["variables"]["sort_type"] = sort_type


            req = httpx.Request("POST", url, params=params, json=payload)
            
            return req


        @staticmethod
        def query_search(
                query_string, 
                primary:bool=True,
                pending:bool=False,
                contingent:bool=False,
                limit:int=None,
                offset:int=None,
                sort_type=None,
            ):
            url = "https://www.realtor.com/api/v1/rdc_search_srp"
            
            params = {"client_id": "rdc-search-for-sale-search", "schema": "vesta"}

            payload = read_payload("realtor-ConsumerSearchQuery.json")
            payload["query"] = read_graphql("realtor-ConsumerSearchQuery.gql")

            query_string = str(query_string).strip()
            payload["variables"]["query"]["search_location"] = {"location": query_string}
            payload["variables"]["geoSupportedSlug"] = query_string
            
            payload["variables"]["query"]["primary"] = primary
            payload["variables"]["query"]["pending"] = pending
            payload["variables"]["query"]["contingent"] = contingent
            
            limit = int(limit) if str(limit).isdigit() else 50
            sort_type = str(sort_type).lower() if sort_type != None else "relevant"

            payload["variables"]["limit"] = int(limit)
            # payload["variables"]["offset"] = int(offset)
            payload["variables"]["sort_type"] = sort_type

            req = httpx.Request("POST", url, params=params, json=payload)
            
            return req


        @staticmethod
        def city_search(
                city=None,
                primary:bool=True,
                pending:bool=False,
                contingent:bool=False,
                limit:int=None,
                offset:int=None,
                sort_type=None,
            ):
            url = "https://www.realtor.com/api/v1/rdc_search_srp"
            
            params = {"client_id": "rdc-search-for-sale-search", "schema": "vesta"}

            payload = readjson(QUERY_DIR.joinpath(f"realtor-ConsumerSearchQuery.json"))
            payload["query"] = readfile(QUERY_DIR.joinpath(f"realtor-ConsumerSearchQuery.gql"))
            
            payload["variables"]["query"]["search_location"] = {"location": city}
            payload["variables"]["geoSupportedSlug"] = city
            
            payload["variables"]["query"]["primary"] = primary
            payload["variables"]["query"]["pending"] = pending
            payload["variables"]["query"]["contingent"] = contingent
            
            limit = int(limit) if str(limit).isdigit() else 50
            sort_type = str(sort_type).lower() if sort_type != None else "relevant"

            payload["variables"]["limit"] = int(limit)
            # payload["variables"]["offset"] = int(offset)
            payload["variables"]["sort_type"] = sort_type

            req = httpx.Request("POST", url, params=params, json=payload)
            
            return req


        @staticmethod
        def property_details(property_id):
            url = "https://www.realtor.com/frontdoor/graphql"

            _variables = {"propertyId": f"{property_id}"}
            _extensions = {"persistedQuery": {"version": 1, "sha256Hash": "f092e858153fb66a74362fd819a7587b0cb445975107fe13bcff8fcdb500caae"}}

            params = {
                "operationName": "FullPropertyDetails",
                "variables": json.dumps(_variables, separators=(',', ':')),
                "extensions": json.dumps(_extensions, separators=(',', ':')),
            }

            headers = {
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "host": "www.realtor.com",
                "content-type": "application/json",
                "accept": "*/*",
                "rdc-client-name": "RDC_WEB_DETAILS_PAGE",
                "rdc-client-version": "2.0.1241",
            }

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req


        @staticmethod
        def property_and_tax_history(property_id):
            url = "https://www.realtor.com/api/v1/rdc_search_srp"
            
            payload = readjson(QUERY_DIR.joinpath(f"realtor-PropertyAndTaxHistory.json"))
            payload["query"] = readfile(QUERY_DIR.joinpath(f"realtor-PropertyAndTaxHistory.gql"))
            payload["variables"]["propertyId"] = property_id

            
            params = {"client_id": "RDC_WEB_DETAILS_PAGE", "schema": "vesta"}

            req = httpx.Request("POST", url, params=params, json=payload)

            return req


        @staticmethod
        def property_school_data(property_id):
            url = "https://www.realtor.com/frontdoor/graphql"

            _variables = {"propertyId": f"{property_id}"}
            _extensions = {
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": "ee4267d9cd64801da16099587142fc163d2e04fc6525f2b67924440a90b5f638"
                }
            }

            params = {
                "operationName": "GetSchoolData",
                "variables": json.dumps(_variables, separators=(',', ':')),
                "extensions": json.dumps(_extensions, separators=(',', ':')),
            }

            headers = {
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "host": "www.realtor.com",
                "content-type": "application/json",
                "accept": "*/*",
                "rdc-client-name": "RDC_WEB_DETAILS_PAGE",
                "rdc-client-version": "2.0.1241",
            }

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req
        

        @staticmethod
        def property_estimates(property_id, historicalYearsMin, historicalYearsMax, forecastedMonthsMax):
            url = "https://www.realtor.com/frontdoor/graphql"

            _variables = {
                "propertyId": f"{property_id}", 
                "historicalYearsMin": historicalYearsMin, 
                "historicalYearsMax": historicalYearsMax, 
                "forecastedMonthsMax": forecastedMonthsMax
            }
            _extensions = {
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": "98965d7e46d5550c2caca6656326be533a548fde2b41d9e1a4dda47c7db9de38"
                }
            }

            params = {
                "operationName": "DPPropertyEstimates",
                "variables": json.dumps(_variables, separators=(',', ':')),
                "extensions": json.dumps(_extensions, separators=(',', ':')),
            }

            headers = {
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "host": "www.realtor.com",
                "content-type": "application/json",
                "accept": "*/*",
                "rdc-client-name": "RDC_WEB_DETAILS_PAGE",
                "rdc-client-version": "2.0.1241",
            }

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req


        @staticmethod
        def property_saves(property_id):
            url = "https://www.realtor.com/frontdoor/graphql"

            _variables = {
                "propertyId": f"{property_id}"
            }
            _extensions = {
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": "00e9ea1931736764388f7794703d0fb9da5aa1dbb9cff211cb809c4aae5728cf"
                }
            }

            params = {
                "operationName": "GetHomeSaves",
                "variables": json.dumps(_variables, separators=(',', ':')),
                "extensions": json.dumps(_extensions, separators=(',', ':')),
            }

            headers = {
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "host": "www.realtor.com",
                "content-type": "application/json",
                "accept": "*/*",
                "rdc-client-name": "RDC_WEB_DETAILS_PAGE",
                "rdc-client-version": "2.0.1241",
            }

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req
        

        @staticmethod
        def property_gallery(property_id):
            url = "https://www.realtor.com/frontdoor/graphql"

            _variables = {
                # "propertyId": f"{property_id}"
                "property_id": f"{property_id}"
            }
            _extensions = {
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": "f31fc9dfe469d31d25c4e893223c06e40f9c307e4411a0e4afd060b99ed1db20"
                }
            }

            params = {
                # "operationName": "get_augmented_gallery",
                "operationName": "GetAugmentedGallery",
                "variables": json.dumps(_variables, separators=(',', ':')),
                "extensions": json.dumps(_extensions, separators=(',', ':')),
            }

            headers = {
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "host": "www.realtor.com",
                "content-type": "application/json",
                "accept": "*/*",
                "rdc-client-name": "RDC_WEB_DETAILS_PAGE",
                "rdc-client-version": "2.0.1241",
            }

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req
        

        @staticmethod
        def _compact_search_data(rawdata):
            data = {
                "count": rawdata["data"]["home_search"]["count"],
                "total": rawdata["data"]["home_search"]["total"],
                "mortgage_params": rawdata["data"]["home_search"]["mortgage_params"],
                "properties": rawdata["data"]["home_search"]["properties"]
            }

            return data


    class normalize:
        @staticmethod
        def property_search(response_data):
            template = readjson(JSON_DIR.joinpath("listing_search.json"))
            # template = _StrictMap(template)
            
            property_list: list[dict] = response_data.get("data", {}).get("home_search", {}).get("properties", [])
            
            normalized_data = []

            for property in property_list:
                property_data = template.copy()
                
                # Fill agent and agency details
                # _source = always_get("source", property, {})
                # _agent = always_get("agents", _source, [{}])[0]
                # _advertiser = always_get("advertisers", property, [{}])[0]

                # property_data["agency_name"] = _agent.get("office_name")
                # property_data["agency_phone"] = maybe we could get the phone number for the agency?
                # property_data["agent_name"] = _advertiser.get("type", None)
                # property_data["agent_phone"] = None  # No explicit field for phone with Realtor API

                # Address information
                _location = always_get("location", property, {})
                property_data["address"]["city"] = _location.get("address", {}).get("city")
                property_data["address"]["country_code"] = "US"
                property_data["address"]["county"] = _location.get("county", {}).get("name")
                property_data["address"]["postal_code"] = _location.get("address", {}).get("postal_code")
                property_data["address"]["state"] = _location.get("address", {}).get("state")
                property_data["address"]["street"] = _location.get("address", {}).get("line")
                property_data["address"]["lat"] = _location.get("coordinate", {}).get("lat")
                property_data["address"]["lon"] = _location.get("coordinate", {}).get("lon")
                
                # Number of beds and baths
                _description = always_get("description", property, {})
                property_data["num_beds"] = _description.get("beds")
                property_data["num_baths"] = float(_description.get("baths_consolidated", "0").split('+')[0])
                
                # Images
                property_data["images"] = [
                    Realtor.generate_custom_photo_url2(photo.get("href"))
                    for photo in always_get("photos", property, [])
                    ]
                
                # Price and price history
                property_data["price"] = property.get("list_price")
                if _description.get("sold_price"):
                    property_data["price_history"] = [{
                        "price": _description.get("sold_price"),
                        "date": _description.get("sold_date")
                    }]
                
                # Database fields
                property_data["db_listing_id"] = property.get("listing_id")
                property_data["db_property_id"] = property.get("property_id")
                property_data["db_name"] = _description.get("name")

                normalized_data.append(property_data)
            
            return normalized_data



