import json
import datetime as dt
from typing import Literal
from typing import Optional
from pathlib import Path

import httpx
from dateutil.relativedelta import relativedelta

from . import paths
from .util import readjson
from .util import readfile
from .util import get_bounding_box


class RealtorAPI:
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

        # rawdata = self._search(
        #     coordinates=coordinates, 
        #     radius_mi=radius_mi, 
            # primary=primary, 
            # pending=pending, 
            # contingent=contingent,
            # limit=limit,
            # sort_type=sort_type,
        #     )

        data = self._compact_search_data(rawdata)

        return data


    def zipcode_search(
            self,
            zipcode,
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            offset=None,
            sort_type:Literal["relevant"]=None
        ):

        req = self.request.zipcode_search(
            zipcode, 
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

        data = self._compact_search_data(rawdata)

        return data


    def city_search(
            self,
            city, 
            state,
            primary=True, 
            pending=False, 
            contingent=False,
            limit=None,
            offset=None,
            sort_type:Literal["relevant"]=None
        ):

        city = f"{city}, {state}"

        req = self.request.zipcode_search(
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

        data = self._compact_search_data(rawdata)

        return data


    def property_link(self, permalink:str):
        base_url = "https://www.realtor.com/realestateandhomes-detail"
        return f"{base_url}/{permalink}"
    

    def custom_photo_link(self, og_url, width:Optional[int]=None):
        if width != None:
            url_obj = httpx.URL(og_url)

            start_idx = url_obj.path.rfind("/") + 1
            
            urlpath = Path(url_obj.path[start_idx:])

            edited_url = f"{url_obj.scheme}://{url_obj.host}/" + urlpath.with_stem(urlpath.stem + f"-w{width}").name
            
            return edited_url
        
        else:
            return og_url


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
        def map_search(
                coordinates:tuple[float]=None,
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

            payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.json"))
            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.gql"))

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
        def zipcode_search(
                zipcode, 
                primary:bool=True,
                pending:bool=False,
                contingent:bool=False,
                limit:int=None,
                offset:int=None,
                sort_type=None,
            ):
            url = "https://www.realtor.com/api/v1/rdc_search_srp"
            
            params = {"client_id": "rdc-search-for-sale-search", "schema": "vesta"}

            payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-ConsumerSearchQuery.json"))
            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-ConsumerSearchQuery.gql"))

            zipcode = str(zipcode).strip()
            payload["variables"]["query"]["search_location"] = {"location": zipcode}
            payload["variables"]["geoSupportedSlug"] = zipcode
            
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

            payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-ConsumerSearchQuery.json"))
            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-ConsumerSearchQuery.gql"))
            
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
            
            payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-PropertyAndTaxHistory.json"))
            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-PropertyAndTaxHistory.gql"))
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
                    # "sha256Hash": "e3e2fd0bf9ac9f82a05a4bd8c859c60ffdf701e3ff994c6da01d1d02d2d0da9e"
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

    def query_understanding(self,query:str):
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

    def _headers(self):
        return {
            "accept": "*/*",
            "host": "zm.zillow.com",
            "user-agent": "Zillow/16.95.0.1 CFNetwork/1568.100.1 Darwin/24.0.0",
            "content-type": "application/json",
            "x-client": "com.zillow.ZillowMap",
        }


