import json
import datetime as dt
from typing import Literal

import httpx
from dateutil.relativedelta import relativedelta

from . import paths
from .util import readjson
from .util import readfile
from .util import get_bounding_box


class RealtorAPI:
    def __init__(self) -> None:
        pass

    def map_lookup(
            self,
            coordinates:tuple[float],
            radius_mi=None,
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            sort_type:Literal["relevant"]=None
        ):

        rawdata = self._search(
            coordinates=coordinates, 
            radius_mi=radius_mi, 
            primary=primary, 
            pending=pending, 
            contingent=contingent,
            limit=limit,
            sort_type=sort_type,
            )

        data = self._compact_search_data(rawdata)

        return data


    def zipcode_lookup(
            self,
            zipcode,
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            sort_type:Literal["relevant"]=None
        ):

        rawdata = self._search(
            zipcode=zipcode,
            primary=primary, 
            pending=pending, 
            contingent=contingent,
            limit=limit,
            sort_type=sort_type,
            )

        data = self._compact_search_data(rawdata)

        return data


    def city_lookup(
            self,
            city, 
            state,
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            sort_type:Literal["relevant"]=None
        ):

        city = f"{city}, {state}"

        rawdata = self._search(
            city=city,
            primary=primary, 
            pending=pending, 
            contingent=contingent,
            limit=limit,
            sort_type=sort_type,
            )

        data = self._compact_search_data(rawdata)

        return data


    def generate_link(self, permalink:str):
        # base_url = "https://www.realtor.com/realestateandhomes-detail/55-Codorus-Rd_Montgomery_IL_60538_M75204-56587?from=srp-map-list"
        base_url = "https://www.realtor.com/realestateandhomes-detail"
        return f"{base_url}/{permalink}"


    def _search(
            self, *, 
            zipcode=None, 
            city=None, 
            coordinates:tuple[float]=None,
            radius_mi=None,
            primary:bool=True,
            pending:bool=False,
            contingent:bool=False,
            limit:int=None,
            sort_type=None,
        ):
        url = "https://www.realtor.com/api/v1/rdc_search_srp"
        
        params = {"client_id": "rdc-search-for-sale-search", "schema": "vesta"}

        operation_name = "ConsumerSearchQuery"

        payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.json"))
        payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.gql"))

        if zipcode != None:
            zipcode = str(zipcode).strip()
            payload["variables"]["query"]["search_location"] = {"location": zipcode}
            payload["variables"]["geoSupportedSlug"] = zipcode
        
        elif city != None:
            payload["variables"]["query"]["search_location"] = {"location": city}
            payload["variables"]["geoSupportedSlug"] = city
        
        elif coordinates != None:
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

        # payload["variables"]["offset"] = 
        payload["variables"]["sort_type"] = "relevant"
        payload["variables"]["limit"] = int(limit)


        with httpx.Client() as client:
            r = client.post(url, params=params, json=payload)

            return r.json()


    def _get_graphql_request(
            self, operation_name:Literal["FullPropertyDetails", "DPPropertyEstimates", "GetSchoolData", "GetHomeSaves", "get_augmented_gallery"], 
            property_id,
            historical_year_start=None,
            historical_year_end=None,
            month_forecast_count=None,
        ):
        url = "https://www.realtor.com/frontdoor/graphql"

        if operation_name == "FullPropertyDetails":
            sha_hash = "f092e858153fb66a74362fd819a7587b0cb445975107fe13bcff8fcdb500caae"
            variables = {"propertyId": f"{property_id}"}

        elif operation_name == "DPPropertyEstimates":
            sha_hash = "98965d7e46d5550c2caca6656326be533a548fde2b41d9e1a4dda47c7db9de38"
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

            variables = {"propertyId": f"{property_id}", "historicalYearsMin": hist_year_min,"historicalYearsMax": hist_year_max,"forecastedMonthsMax": fcast_date_str}

        elif operation_name == "GetSchoolData":
            sha_hash = "ee4267d9cd64801da16099587142fc163d2e04fc6525f2b67924440a90b5f638"
            variables = {"propertyId": f"{property_id}"}
        
        elif operation_name == "GetHomeSaves":
            sha_hash = "00e9ea1931736764388f7794703d0fb9da5aa1dbb9cff211cb809c4aae5728cf"
            variables = {"propertyId": f"{property_id}"}

        elif operation_name == "get_augmented_gallery":
            sha_hash = "e3e2fd0bf9ac9f82a05a4bd8c859c60ffdf701e3ff994c6da01d1d02d2d0da9e"
            variables = {"propertyId": f"{property_id}"}


        extensions = {"persistedQuery": {"version": 1, "sha256Hash": f"{sha_hash}"}}

        params = {
            "operationName": operation_name,
            "variables": json.dumps(variables, separators=(',', ':')),
            "extensions": json.dumps(extensions, separators=(',', ':')),
        }

        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "host": "www.realtor.com",
            "content-type": "application/json",
            "accept": "*/*",
            "rdc-client-name": "RDC_WEB_DETAILS_PAGE",
            "rdc-client-version": "2.0.1241",
        }

        r = httpx.get(url, params=params, headers=headers)

        data = r.json()

        return data

    def _property_details(self, property_id):
        url = "https://www.realtor.com/frontdoor/graphql"

        params = {
            "operationName": "FullPropertyDetails",
            "variables": json.dumps({"propertyId": f"{property_id}"}, separators=(',', ':')),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "f092e858153fb66a74362fd819a7587b0cb445975107fe13bcff8fcdb500caae"}}, separators=(',', ':')),
        }

        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "host": "www.realtor.com",
            "content-type": "application/json",
            "accept": "*/*",
            "rdc-client-name": "RDC_WEB_DETAILS_PAGE",
            "rdc-client-version": "2.0.1241",
        }

        r = httpx.get(url, params=params, headers=headers)

        data = r.json()

        return data

    def _property_and_tax_history(self, property_id):
        
        operation_name = "PropertyAndTaxHistory"

        payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.json"))
        payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.gql"))
        payload["variables"]["propertyId"] = property_id

        url = "https://www.realtor.com/api/v1/rdc_search_srp"
        
        params = {"client_id": "RDC_WEB_DETAILS_PAGE", "schema": "vesta"}

        with httpx.Client() as client:
            r = client.post(url, params=params, json=payload)

            return r.json()
    
    def _compact_property_data(self, rawdata):
        ...

    def _compact_search_data(self, rawdata):
        data = {
            "count": rawdata["data"]["home_search"]["count"],
            "total": rawdata["data"]["home_search"]["total"],
            "mortgage_params": rawdata["data"]["home_search"]["mortgage_params"],
            "properties": rawdata["data"]["home_search"]["properties"]
        }

        return data

    class request:
        @staticmethod
        def search(
                zipcode=None, 
                city=None, 
                coordinates:tuple[float]=None,
                radius_mi=None,
                primary:bool=True,
                pending:bool=False,
                contingent:bool=False,
                limit:int=None,
                sort_type=None,
            ):
            url = "https://www.realtor.com/api/v1/rdc_search_srp"
            
            params = {"client_id": "rdc-search-for-sale-search", "schema": "vesta"}

            operation_name = "ConsumerSearchQuery"

            payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.json"))
            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.gql"))

            if zipcode != None:
                zipcode = str(zipcode).strip()
                payload["variables"]["query"]["search_location"] = {"location": zipcode}
                payload["variables"]["geoSupportedSlug"] = zipcode
            
            elif city != None:
                payload["variables"]["query"]["search_location"] = {"location": city}
                payload["variables"]["geoSupportedSlug"] = city
            
            elif coordinates != None:
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

            # payload["variables"]["offset"] = 
            payload["variables"]["sort_type"] = sort_type
            payload["variables"]["limit"] = int(limit)


            req = httpx.Request("POST", url, params=params, json=payload)
            
            return req




class ZillowAPI:
    def __init__(self):
        pass

    def coordinates_lookup(
            self, 
            coordinates:tuple[float, float], 
            radius_mi:int=None, 
            price_range_min:float=None, 
            price_range_max:float=None,
            limit=None
            ):
        url = "https://zm.zillow.com/api/public/v2/mobile-search/homes/search"

        radius_mi = int(radius_mi) if radius_mi != None else 10
        price_range_min = int(price_range_min) if price_range_min != None else None
        price_range_max = int(price_range_max) if price_range_max != None else None
        limit = int(limit) if limit != None else 75

        if (price_range_min, price_range_max) == (None, None):
            price_range_max = 500000000

        bbox = get_bounding_box(coordinates[0], coordinates[1], radius=radius_mi)
        

        payload = {
            "filterHiddenHomes": True,
            "sortOrder": "relevance",
            "supplementResultsWithOffMarket": False,
            "keywords": "Shed",
            "regionParameters": {
                "boundaries": {
                    "westLongitude": bbox["west"],
                    "eastLongitude": bbox["east"],
                    "northLatitude": bbox["north"],
                    "southLatitude": bbox["south"]
                }
            },
            "paging": {
                "pageNumber": 1,
                "pageSize": limit,
            },
            "homeStatuses": [
                "fsba",
                "fsbo",
                "foreclosure",
                "auction",
                "comingSoon",
                "newConstruction"
            ],
            "includeFlexField": True,
            "excludeFilter": [
                "pending",
                "acceptingBackupOffers"
            ],
            "returnFlags": [
                "navigationAds"
            ],
            "zoomLevel": 10,
            "priceRange": {
                "max": price_range_max
            },
            "homeDetailsUriParameters": {
                "platform": "iphone",
                "googleMaps": False,
                "streetView": False,
                "showFactsAndFeatures": True
            },
            "includeUngroupedCount": False,
            "bedroomsRange": {
                "min": 0
            },
            "sortAscending": False,
            "showAllFirstPartyPhotos": True,
            "photoTreatments": [
                "medium",
                "highResolution"
            ],
            "listingCategoryFilter": "category1"
        }

        headers = self._headers()

        r = httpx.post(url, headers=headers, json=payload)

        return r.json()
    
    def property_lookup(self, zpid):
        url = "https://zm.zillow.com/api/public/v3/mobile-search/homes/lookup"

        payload = {
            "homeDetailsUriParameters": {
                "googleMaps": False,
                "streetView": False,
                "platform": "iphone",
                "showFactsAndFeatures": True
            },
            "sortOrder": "recentlyChanged",
            "listingCategoryFilter": "all",
            "propertyIds": [int(zpid)],
            "showAllFirstPartyPhotos": False,
            "buildings": [],
            "sortAscending": True
        }

        headers = self._headers()

        r = httpx.post(url, headers=headers, json=payload)

        return r.json()

    def _query_understanding(self,query:str):
        url = "https://www.zillow.com/zg-graph"

        payload = readjson(paths.GRAPHQL_DIR.joinpath("zillow-QueryUnderstanding.json"))
        payload["variables"]["query"] = query

        headers = {
            "accept": "*/*",
            "host": "www.zillow.com",
            # "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "user-agent": "Zillow/16.95.0.1 CFNetwork/1568.100.1 Darwin/24.0.0",
            "referer": "https://www.zillow.com/",
            "content-type": "application/json",
            "client-id": "hops-homepage",
            "accept-encoding": "gzip, deflate, br",
        }

        r = httpx.post(url, headers=headers, json=payload)

        return r.json() 

    def _query_understanding2(self, query:str):
        url = "https://www.zillow.com/zg-graph"
        
        payload = readjson(paths.GRAPHQL_DIR.joinpath("zillow-getQueryUnderstandingResults.json"))
        payload["variables"]["query"] = query
        payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath("zillow-getQueryUnderstandingResults.gql"))

        headers = {
            "accept": "*/*",
            "host": "www.zillow.com",
            # "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "user-agent": "Zillow/16.95.0.1 CFNetwork/1568.100.1 Darwin/24.0.0",
            "referer": "https://www.zillow.com/",
            "content-type": "application/json",
            "client-id": "hops-homepage",
            "accept-encoding": "gzip, deflate, br",
        }

        r = httpx.post(url, headers=headers, json=payload)

        return r.json() 


    def _headers(self):
        return {
            "accept": "*/*",
            "host": "zm.zillow.com",
            "user-agent": "Zillow/16.95.0.1 CFNetwork/1568.100.1 Darwin/24.0.0",
            "content-type": "application/json",
            "x-client": "com.zillow.ZillowMap",
        }


