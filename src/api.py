import json
import datetime as dt
from typing import Literal
from typing import Optional
from pathlib import Path

import rich
import httpx
import orjson
from dateutil.relativedelta import relativedelta

from . import paths
from .util import readjson
from .util import readfile
from .util import get_bounding_box
from .constants import RF_UIPT_MAP
from .constants import RF_POOL_TYPE_MAP
from .constants import RF_REGION_TYPE_MAP
from .constants import RF_FINANCING_TYPE_MAP
from .constants import RF_REGION_TYPE_REVERSE_MAP
from .constants import ZI_REGION_TYPE_MAP

_Polygon = list[tuple[float, float]]
_MultiPolygon = list[list[tuple[float, float]]]


def _send_request(req:httpx.Request) -> httpx.Response:
    with httpx.Client() as client:
        r = client.send(req)
    return r

def _read_gql(s):
    return readfile(paths.GRAPHQL_DIR.joinpath(s))

def _read_payload(s):
    return readjson(paths.GRAPHQL_DIR.joinpath(s))



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


    def generate_property_link(self, permalink:str):
        base_url = "https://www.realtor.com/realestateandhomes-detail"
        return f"{base_url}/{permalink}"
    

    def generate_custom_photo_link(self, og_url, width:Optional[int]=None):
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

            payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-ConsumerSearchQuery.json"))
            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-ConsumerSearchQuery.gql"))

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

            payload = readjson(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.json"))
            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath(f"realtor-{operation_name}.gql"))

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
        


class Zillow:
    def __init__(self):
        pass


    def map_search(
            self, 
            coordinates:tuple[float, float], 
            radius_mi:int=None, 
            price_range_min:Optional[int]=None,
            price_range_max:Optional[int]=None,
            num_beds_min:Optional[int]=None,
            num_beds_max:Optional[int]=None,
            num_baths_min:Optional[int|float]=None,
            limit:Optional[int]=None,
            page:Optional[int]=None,
            ):
        # TODO: add all the same parameters as region_search
        # TODO: also involves re-configuring the request.map_search() method
        
        req = Zillow.request.map_search(
            coordinates=coordinates,
            radius_mi=radius_mi,
            price_min=price_range_min,
            price_max=price_range_max,
            num_beds_min=num_beds_min,
            num_beds_max=num_beds_max,
            num_baths_min=num_baths_min,
            limit=limit,
            page=page,
        )
        
        with httpx.Client() as client:
            r = client.send(req)

        rawdata = orjson.loads(r.content)

        return rawdata
    

    def polygon_search(
        self,
        polygon:Optional[_Polygon]=None, 
        multi_polygon:Optional[_MultiPolygon]=None,
        price_range_min:Optional[int]=None,
        price_range_max:Optional[int]=None,
        num_beds_min:Optional[int]=None,
        num_beds_max:Optional[int]=None,
        num_baths_min:Optional[int|float]=None,
        limit:Optional[int]=None,
        page:Optional[int]=None,
        ):
        
        req = self.request.polygon_search(
            polygon=polygon, 
            multi_polygon=multi_polygon,
            price_range_min=price_range_min,
            price_range_max=price_range_max,
            num_beds_min=num_beds_min,
            num_beds_max=num_beds_max,
            num_baths_min=num_baths_min,
            limit=limit,
            page=page,
        )

        r = _send_request(req)

        rawdata = orjson.loads(r.content)

        return rawdata


    def region_search(
            self, 
            query, 
            region_type:Literal["city", "zipcode", "neighborhood", "address"]=None,
            coordinates:list[tuple[float, float]]=None,
            price_min:int|None=None,
            price_max:int|None=None,
            num_beds_min:int|None=None,
            num_beds_max:int|None=None,
            num_baths_min:int|float|None=None,
            num_baths_max:int|float|None=None,
            include_pending_listings:bool|None=None,
            include_accepting_offers:bool|None=None,
            open_houses_only:bool|None=None,
            has_3d_tour_only:bool|None=None,
            year_built_min:int|None=None,
            year_built_max:int|None=None,
            has_finished_basement:bool|None=None,
            has_unfinished_basement:bool|None=None,
            has_garage:bool|None=None,
            age_55plus_only:bool|None=None,
            single_story_only:bool|None=None,
            has_ac:bool|None=None,
            has_pool:bool|None=None,
            doz:Literal["1","7","14","30","90","6m","12m","24m","36m"]|None=None,
            limit:int|None=None,
            page:int|None=None,
            sort_order:Literal["globalrelevanceex", "days", "beds", "baths", "lot", "paymentd", "paymenta", "featured", "size", "zest", "zesta", "pricea", "priced", "mostrecentchange", "listingstatus"]|None=None,
        
        ):
        req = self.request.query_understanding(query)

        with httpx.Client() as client:
            r = client.send(req)

            query_data = self._compact_query_understanding(orjson.loads(r.content))
            
            for result in query_data:
                if str(result["sub_type"]).lower() == region_type.strip().lower():
                    region_id = result["region_id"]
                    region_type = result["sub_type"]
                    coordinates = result["polygon"]
                    break

            req = self.request.region_lookup2(
                region_id,
                region_type, 
                coordinates=coordinates,
                price_min=price_min,
                price_max=price_max,
                num_beds_min=num_beds_min,
                num_beds_max=num_beds_max,
                num_baths_min=num_baths_min,
                num_baths_max=num_baths_max,
                include_pending_listings=include_pending_listings,
                include_accepting_offers=include_accepting_offers,
                open_houses_only=open_houses_only,
                has_3d_tour_only=has_3d_tour_only,
                year_built_min=year_built_min,
                year_built_max=year_built_max,
                has_finished_basement=has_finished_basement,
                has_unfinished_basement=has_unfinished_basement,
                has_garage=has_garage,
                hide_55plus=age_55plus_only,
                single_story_only=single_story_only,
                has_ac=has_ac,
                has_pool=has_pool,
                doz=doz,
                limit=limit,
                page=page,
                sort_order=sort_order,
                )
            
            r = client.send(req)

            rawdata = orjson.loads(r.content)
        
        # return query_data
        return rawdata
        
            


    def region_lookup(self, region_id, region_type:Literal["city", "zipcode", "neighborhood", "address"], coordinates:list[tuple[float, float]]):
        req = self.request.region_lookup(
            region_id=region_id,
            region_type=region_type,
            coordinates=coordinates
        )

        r = _send_request(req)

        rawdata = orjson.loads(r.content)

        return rawdata


    def property_details(self, zpid):
        req = self.request.property_details(zpid)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content)

        return rawdata


    def query_understanding(self, query:str):
        req = Zillow.request.query_understanding(query)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content)

        data = self._compact_query_understanding(rawdata)

        return data


    def query_understanding2(self, query, page:int=1):
        req = Zillow.request.query_understanding2(
            query=query,
            page=page
        )

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content)

        return rawdata
    

    def autocomplete(self, query_string:str):
        req = Zillow.request.autocomplete_results(query_string)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content)

        data = self._compact_autocomplete(rawdata)

        return data


    def _compact_query_understanding(self, rawdata):
        data = []
        
        for result in rawdata["data"]["zgsQueryUnderstandingRequest"]["results"]:
            sub_type_name = result.get("subType")
            region_type_id = ZI_REGION_TYPE_MAP.get(sub_type_name)

            polystr: str = result.get("region", {}).get("mbr", "")
            polystr = polystr.replace("POLYGON", "").replace("(", "").replace(")", "").strip()
            
            polygon = self._parse_polygon(polystr)
            # polygon = [[c[1], c[0]] for c in polygon]

            data.append({
                "id": result.get("id"),
                "type": result.get("type"),
                "sub_type": sub_type_name,
                "region_id": result.get("regionId"),
                "region_type_id": region_type_id,
                "geometry_type": result.get("region", {}).get("geometryType"),
                "polygon": polygon,
            })
        
        return data


    def _compact_autocomplete(self, rawdata):
        data = []

        for result in rawdata["data"]["searchAssistanceResult"]["results"]:
            new_result = {
                "id": None,
                "region_id": None,
                "type": None,
                "sub_type": None,
            }

            if result["__typename"] == "SearchAssistanceRegionResult":
                new_result["id"] = result.get("id")
                new_result["region_id"] = result.get("regionId")
                new_result["type"] = "Region"
                new_result["sub_type"] = result.get("subType")
            elif result["__typename"] == "SearchAssistanceAddressResult":
                new_result["id"] = result.get("id")
                new_result["region_id"] = result.get("regionId")
                new_result["type"] = "Address"
                new_result["sub_type"] = "ADDRESS"

            data.append(new_result)
        
        return data


    def _parse_polygon(self, polystr:str) -> list[tuple[float, float]]:
        coords_as_strings = polystr.split(", ")
        coords_as_strings = [x.split(" ") for x in coords_as_strings]

        final_coord_list = []
        for coord_tup in coords_as_strings:
            final_coord_list.append([float(coord_tup[0].strip()), float(coord_tup[1].strip())])
        
        return final_coord_list


    class request:
        @staticmethod
        def map_search(
            coordinates:tuple[float, float], 
            radius_mi:int=None, 
            price_min:Optional[int]=None,
            price_max:Optional[int]=None,
            num_beds_min:Optional[int]=None,
            num_beds_max:Optional[int]=None,
            num_baths_min:Optional[int|float]=None,
            limit:int|None=None,
            page:int|None=None,
            ) -> httpx.Request:

            url = "https://zm.zillow.com/api/public/v2/mobile-search/homes/search"

            radius_mi = int(radius_mi) if radius_mi != None else 5
            price_min = int(price_min) if price_min != None else None
            price_max = int(price_max) if price_max != None else None
            limit = int(limit) if limit != None else 100

            if (price_min, price_max) == (None, None):
                price_max = 500000000

            bbox = get_bounding_box(coordinates[0], coordinates[1], radius=radius_mi)
            
            payload = _read_payload("zillow-MapSearch.json")

            price_min = int(price_min) if price_min != None else 0
            price_max = int(price_max) if price_max != None else 500000000

            limit = int(limit) if limit != None else 100
            page = int(page) if page != None else 1

            num_beds_min = int(num_beds_min) if num_beds_min != None else 1
            num_beds_max = int(num_beds_max) if num_beds_max != None else 5

            num_baths_min = float(num_baths_min) if num_baths_min != None else 0

            if int(num_baths_min) == 0:
                payload.pop("bathroomsRange")
            else:
                if ".0" in str(num_baths_min):
                    num_baths_min = int(num_baths_min)
                payload["bathroomsRange"]["min"] = num_baths_min

            payload["paging"]["pageNumber"] = page
            payload["paging"]["pageSize"] = limit
            payload["bedroomsRange"]["min"] = num_beds_min
            payload["bedroomsRange"]["max"] = num_beds_max
            payload["priceRange"]["min"] = price_min
            payload["priceRange"]["max"] = price_max
            payload["regionParameters"]["boundaries"] = {
                "northLatitude": bbox["north"],
                "southLatitude": bbox["south"],
                "eastLongitude": bbox["east"],
                "westLongitude": bbox["west"],
            }

            headers = Zillow.request._mobile_headers()

            req = httpx.Request("POST", url, headers=headers, json=payload)

            return req
        

        @staticmethod
        def polygon_search(
            polygon:Optional[_Polygon]=None, 
            multi_polygon:Optional[_MultiPolygon]=None,
            price_range_min:Optional[int]=None,
            price_range_max:Optional[int]=None,
            num_beds_min:Optional[int]=None,
            num_beds_max:Optional[int]=None,
            num_baths_min:Optional[int|float]=None,
            limit:Optional[int]=None,
            page:Optional[int]=None,
        ):
            url = "https://zm.zillow.com/api/public/v2/mobile-search/homes/search"

            payload = _read_payload("zillow-clipPolygonSearch.json")

            price_range_min = int(price_range_min) if price_range_min != None else 0
            price_range_max = int(price_range_max) if price_range_max != None else 500000000

            limit = int(limit) if limit != None else 100
            page = int(page) if page != None else 1

            num_beds_min = int(num_beds_min) if num_beds_min != None else 1
            num_beds_max = int(num_beds_max) if num_beds_max != None else 5

            num_baths_min = float(num_baths_min) if num_baths_min != None else 0

            if int(num_baths_min) == 0:
                payload.pop("bathroomsRange")
            else:
                if ".0" in str(num_baths_min):
                    num_baths_min = int(num_baths_min)
                payload["bathroomsRange"]["min"] = num_baths_min


            if multi_polygon != None:
                all_lat = []
                all_lon = []
                for poly in multi_polygon:
                    for c in poly:
                        all_lat.append(c[0])
                        all_lon.append(c[1])
                clip_polygon_string = Zillow.request._polygon_tuples_to_string(multi_polygon)

            elif polygon != None:
                all_lat = [c[0] for c in polygon]
                all_lon = [c[1] for c in polygon]

                clip_polygon_string = Zillow.request._polygon_tuples_to_string(polygon)


            payload["paging"]["pageNumber"] = page
            payload["paging"]["pageSize"] = limit
            payload["bedroomsRange"]["min"] = num_beds_min
            payload["bedroomsRange"]["max"] = num_beds_max
            payload["priceRange"]["min"] = price_range_min
            payload["priceRange"]["max"] = price_range_max
            payload["regionParameters"]["regionType"] = "customPolygon"
            payload["regionParameters"]["clipPolygon"] = clip_polygon_string
            payload["regionParameters"]["boundaries"] = {
                "northLatitude": max(all_lat) + 0.1,
                "southLatitude": min(all_lat) - 0.1,
                "eastLongitude": max(all_lon) + 0.1,
                "westLongitude": min(all_lon) - 0.1,
            }

            headers = Zillow.request._mobile_headers()

            req = httpx.Request("POST", url, headers=headers, json=payload)

            return req


        @staticmethod
        def region_lookup(region_id, region_type:str, coordinates:list[tuple[float, float]]):
            url = "https://zm.zillow.com/api/public/v2/mobile-search/homes/search"
            
            headers = Zillow.request._mobile_headers()

            payload = readjson(paths.GRAPHQL_DIR.joinpath("zillow-regionQuery.json"))
            
            all_lat = [x[1] for x in coordinates]
            all_lon = [x[0] for x in coordinates]

            payload["regionParameters"]["regionIds"][0]["regionId"] = str(region_id)
            payload["regionParameters"]["regionIds"][0]["regionIdType"] = str(region_type).lower()
            payload["regionParameters"]["boundaries"]["northLatitude"] = max(all_lat) + 1
            payload["regionParameters"]["boundaries"]["southLatitude"] = min(all_lat) - 1
            payload["regionParameters"]["boundaries"]["eastLongitude"] = max(all_lon) + 1
            payload["regionParameters"]["boundaries"]["westLongitude"] = min(all_lon) - 1

            rich.print(payload["regionParameters"])

            req = httpx.Request("POST", url, headers=headers, json=payload)

            return req
        

        @staticmethod
        def region_lookup2(
            region_id, 
            region_type:str, 
            coordinates:list[tuple[float, float]],
            price_min:int|None=None,
            price_max:int|None=None,
            num_beds_min:int|None=None,
            num_beds_max:int|None=None,
            num_baths_min:int|float|None=None,
            num_baths_max:int|float|None=None,
            include_pending_listings:bool=False,
            include_accepting_offers:bool=False,
            open_houses_only:bool=False,
            has_3d_tour_only:bool|None=None,
            year_built_min:int|None=None,
            year_built_max:int|None=None,
            has_finished_basement:bool|None=None,
            has_unfinished_basement:bool|None=None,
            has_garage:bool|None=None,
            hide_55plus:bool=False,
            single_story_only:bool|None=None,
            has_ac:bool|None=None,
            has_pool:bool|None=None,
            doz:None|Literal["1","7","14","30","90","6m","12m","24m","36m"]=None,
            limit:None|int=None,
            page:None|int=None,
            sort_order:None|Literal["globalrelevanceex", "days", "beds", "baths", "lot", "paymentd", "paymenta", "featured", "size", "zest", "zesta", "pricea", "priced", "mostrecentchange", "listingstatus"]=None,

            ):
            url = "https://www.zillow.com/async-create-search-page-state"
            
            headers = Zillow.request._desktop_headers()

            payload = readjson(paths.GRAPHQL_DIR.joinpath("zillow-searchQueryState.json"))
            
            all_lat = [x[1] for x in coordinates]
            all_lon = [x[0] for x in coordinates]

            payload["searchQueryState"]["regionSelection"][0]["regionId"] = int(region_id)
            payload["searchQueryState"]["regionSelection"][0]["regionType"] = int(ZI_REGION_TYPE_MAP[region_type])
            payload["searchQueryState"]["mapZoom"] = 10
            payload["searchQueryState"]["mapBounds"] = {
                "north": max(all_lat) + 0.1,
                "south": min(all_lat) - 0.1,
                "east": max(all_lon) + 0.1,
                "west": min(all_lon) - 0.1,
                "zoom": 10,
            }

            if price_min != None or price_max != None:
                payload["searchQueryState"]["filterState"]["price"] = {}
                if price_min != None:
                    payload["searchQueryState"]["filterState"]["price"]["min"] = int(price_min)
                if price_max != None:
                    payload["searchQueryState"]["filterState"]["price"]["max"] = int(price_max)

            if num_beds_min != None or num_beds_max != None:
                payload["searchQueryState"]["filterState"]["beds"] = {}
                if num_beds_min != None:
                    payload["searchQueryState"]["filterState"]["beds"]["min"] = int(num_beds_min)
                if num_beds_max != None:
                    payload["searchQueryState"]["filterState"]["beds"]["max"] = int(num_beds_max)

            if num_baths_min != None or num_baths_max != None:
                payload["searchQueryState"]["filterState"]["baths"] = {}
                if num_baths_min != None:
                    num_baths_min = float(num_baths_min) if ".5" in str(num_baths_min) else int(num_baths_min)
                    payload["searchQueryState"]["filterState"]["baths"]["min"] = num_baths_min
                if num_baths_max != None:
                    num_baths_max = float(num_baths_max) if ".5" in str(num_baths_max) else int(num_baths_max)
                    payload["searchQueryState"]["filterState"]["baths"]["max"] = num_baths_max
            
            if year_built_min != None or year_built_max != None:
                payload["searchQueryState"]["filterState"]["built"] = {}
                if year_built_min != None:
                    payload["searchQueryState"]["filterState"]["built"]["min"] = int(year_built_min)
                if year_built_max != None:
                    payload["searchQueryState"]["filterState"]["built"]["max"] = int(year_built_max)
            
            if doz != None:
                payload["searchQueryState"]["filterState"]["doz"] = str(doz)

            if include_pending_listings == True:
                payload["searchQueryState"]["filterState"]["isPendingListingsSelected"] = {"value": True}
            if include_accepting_offers == True:
                payload["searchQueryState"]["filterState"]["isAcceptingBackupOffersSelected"] = {"value": True}
            if open_houses_only == True:
                payload["searchQueryState"]["filterState"]["isOpenHousesOnly"] = {"value": True}
            if has_3d_tour_only == True:
                payload["searchQueryState"]["filterState"]["is3dHome"] = {"value": True}
            if has_finished_basement == True:
                payload["searchQueryState"]["filterState"]["isBasementFinished"] = {"value": True}
            if has_unfinished_basement == True:
                payload["searchQueryState"]["filterState"]["isBasementUnfinished"] = {"value": True}
            if has_garage == True:
                payload["searchQueryState"]["filterState"]["hasGarage"] = {"value": True}
            if hide_55plus == True:
                payload["searchQueryState"]["filterState"]["ageRestricted55Plus"] = {"value": "e"}
            if single_story_only == True:
                payload["searchQueryState"]["filterState"]["singleStory"] = {"value": True}
            if has_ac == True:
                payload["searchQueryState"]["filterState"]["hasAirConditioning"] = {"value": True}
            if has_pool == True:
                payload["searchQueryState"]["filterState"]["hasPool"] = {"value": True}

            sort_order = sort_order if sort_order != None else "globalrelevanceex"
            payload["searchQueryState"]["filterState"]["sortSelection"] = {"value": sort_order}

            req = httpx.Request("PUT", url, headers=headers, json=payload)

            return req


        @staticmethod
        def autocomplete_results(query_string):
            query_string = str(query_string).strip()

            url = f"https://www.zillow.com/zg-graph"

            params = {
                "query": query_string,
                "queryOptions": "",
                "resultType": ["REGIONS", "FORSALE", "RENTALS", "SOLD", "BUILDER_COMMUNITIES"],
                "operationName": "getAutocompleteResults",
            }

            headers = Zillow.request._desktop_headers()

            payload = readjson(paths.GRAPHQL_DIR.joinpath("zillow-getAutocompleteResults.json"))

            payload["query"] = readfile(paths.GRAPHQL_DIR.joinpath("zillow-getAutocompleteResults.gql"))
            payload["variables"]["query"] = query_string

            req = httpx.Request("POST", url, params=params, headers=headers, json=payload)

            return req


        @staticmethod
        def property_details(zpid) -> httpx.Request:
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

            headers = Zillow.request._mobile_headers()

            req = httpx.Request("POST", url, headers=headers, json=payload)

            return req


        @staticmethod
        def property_details2(zpid, referer:str) -> httpx.Request:
            url = "https://www.zillow.com/graphql/"

            _variables = {
                "zpid": int(zpid),
                "platform":"DESKTOP_WEB",
                "formType":"OPAQUE",
                "contactFormRenderParameter":{
                    "zpid": int(zpid),
                    "platform":"desktop",
                    "isDoubleScroll":True
                },
                "skipCFRD": False, 
                "ompPlatform":"web"
            }

            _extensions = {
                "persistedQuery": {
                    "version":1, 
                    "sha256Hash":"20fecc52f18e651da861b92a8e065845fe90d2ca9164014cf5e67ab73de8563d"
                }
            }

            params = {
                "variables": json.dumps(_variables, separators=(',', ':')),
                "extensions": json.dumps(_extensions, separators=(',', ':')),
            }

            headers = Zillow.request._desktop_headers_alt()
            headers["referer"] = referer

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req


        @staticmethod
        def query_understanding(query:str) -> httpx.Request:
            url = "https://www.zillow.com/zg-graph"

            payload = readjson(paths.GRAPHQL_DIR.joinpath("zillow-QueryUnderstanding.json"))
            payload["variables"]["query"] = query

            headers = Zillow.request._mobile_headers_alt()

            req = httpx.Request("POST", url, headers=headers, json=payload)

            return req


        @staticmethod
        def query_understanding2(query, page:int=1):
            query = str(query).strip()

            url = f"https://www.zillow.com/async-create-search-page-state"

            headers = Zillow.request._desktop_headers()

            payload = readjson(paths.GRAPHQL_DIR.joinpath("zillow-searchQueryState.json"))
            payload["searchQueryState"]["usersSearchTerm"] = query
            payload["searchQueryState"]["pagination"]["currentPage"] = int(page)
            payload["searchQueryState"].pop("mapBounds")
            payload["searchQueryState"]["filterState"]["sortSelection"]["value"] = "globalrelevanceex"
            payload["searchQueryState"].pop("regionSelection")

            req = httpx.Request("PUT", url, headers=headers, json=payload)

            return req


        @staticmethod
        def property_affordability_estimate(zpid="61097782"):
            url = "https://www.zillow.com/zg-graph"
            
            params = {
                "zpid": str(zpid),
                "operationName": "getAffordabilityEstimateFromPersonalizedPaymentChipMVP",
            }

            query = _read_gql("zillow-AffordabilityEstimate.gql")

            payload = {
                "operationName": "getAffordabilityEstimateFromPersonalizedPaymentChipMVP",
                "query": query,
                "variables": {"zpid": int(zpid)}
            }

            headers = Zillow.request._desktop_headers()

            req = httpx.Request("POST", url, params=params, headers=headers, json=payload)

            return req


        @staticmethod
        def _mobile_headers():
            return {
                "host": "zm.zillow.com",
                "user-agent": "Zillow/16.95.0.1 CFNetwork/1568.100.1 Darwin/24.0.0",
                "accept": "*/*",
                "content-type": "application/json",
                "x-client": "com.zillow.ZillowMap",
            }


        @staticmethod
        def _mobile_headers_alt():
            return {
                "host": "www.zillow.com",
                "user-agent": "Zillow/16.95.0.1 CFNetwork/1568.100.1 Darwin/24.0.0",
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
                "x-client": "com.zillow.ZillowMap",
            }


        @staticmethod
        def _desktop_headers():
            return {
                "host": "www.zillow.com",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "content-type": "application/json",
                "x-client": "com.zillow.ZillowMap",
            }


        @staticmethod
        def _desktop_headers_alt():
            return {
                "host": "www.zillow.com",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "accept": "*/*",
                "accept-language": "en-GB,en;q=0.5",
                "accept-encoding": "gzip, deflate, br, zstd",
                "content-type": "application/json",
                "client-id": "for-sale-sub-app-browser-client",
            }


        @staticmethod
        def _string_to_polygon_tuples(polygon_str):
            if polygon_str.startswith("clipPolygon="):
                polygon_str = polygon_str.replace("clipPolygon=", "")
            
            polygon_groups = polygon_str.split(':')
            
            polygons = []
            
            for group in polygon_groups:
                if group:
                    points = group.split('|')
                    
                    points = [point for point in points if point]
                    
                    try:
                        polygon = [tuple(map(float, point.split(','))) for point in points]
                    except ValueError as e:
                        raise e
                    
                    polygons.append(polygon)
            
            return polygons


        @staticmethod
        def _polygon_tuples_to_string(polygons):
            polygon_strings = []
            
            for polygon in polygons:
                point_strings = [','.join(map(str, point)) for point in polygon]
                
                polygon_string = '|'.join(point_strings)
                
                polygon_strings.append(polygon_string + '|:')
            
            final_string = ''.join(polygon_strings)
            
            return f"clipPolygon={final_string}"



class Redfin:
    def __init__(self) -> None:
        pass
    
    def map_search(
            self,
            coordinates:tuple[float],
            radius_mi:int=None,
            home_types:list[Literal["home", "condo", "townhouse", "multi-family", "land", "other", "mobile", "co-op"]]=None,
            num_beds=None,
            max_num_beds=None,
            num_baths=None, 
            num_homes=350,
            excl_ar=False, 
            excl_ss=False,
            time_on_market_range:Literal["1-", "3-", "7-", "14-", "30-", "-7", "-14", "-30", "-45", "-60", "-90", "-180"]=None,
            redfin_listings_only=False,
            financing_type:Literal["FHA", "VA"]=None,
            pool_type:Literal["private", "community", "private_or_community", "no_private_pool"]=None,
            sort_by=None,
        ):
        req = self.request.map_search(coordinates=coordinates, radius_mi=radius_mi, home_types=home_types,
                                      num_beds=num_beds, max_num_beds=max_num_beds, num_baths=num_baths,
                                      num_homes=num_homes, excl_ar=excl_ar, excl_ss=excl_ss, 
                                      time_on_market_range=time_on_market_range, redfin_listings_only=redfin_listings_only,
                                      financing_type=financing_type, pool_type=pool_type, sort_by=sort_by)
        
        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))

        return rawdata


    def region_search(
            self,
            region_id,
            region_type:Literal["zipcode", "city", "county", "neighborhood"],
            home_types:list[Literal["home", "condo", "townhouse", "multi-family", "land", "other", "mobile", "co-op"]]=None,
            num_beds=None,
            max_num_beds=None,
            num_baths=None, 
            num_homes=350,
            excl_ar=False, 
            excl_ss=False,
            time_on_market_range:Literal["1-", "3-", "7-", "14-", "30-", "-7", "-14", "-30", "-45", "-60", "-90", "-180"]=None,
            redfin_listings_only=False,
            financing_type:Literal["FHA", "VA"]=None,
            pool_type:Literal["private", "community", "private_or_community", "no_private_pool"]=None,
            sort_by=None,
        ):
        req = self.request.region_search(region_id=region_id, region_type=region_type, home_types=home_types,
                                         num_beds=num_beds, max_num_beds=max_num_beds, num_baths=num_baths,
                                         num_homes=num_homes, excl_ar=excl_ar, excl_ss=excl_ss, 
                                         time_on_market_range=time_on_market_range, redfin_listings_only=redfin_listings_only,
                                         financing_type=financing_type, pool_type=pool_type, sort_by=sort_by)
        
        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))

        return rawdata


    def polygon_search(
            self,
            coordinates_list:list[tuple[float, float]],
            home_types:list[Literal["home", "condo", "townhouse", "multi-family", "land", "other", "mobile", "co-op"]]=None,
            num_beds=None,
            max_num_beds=None,
            num_baths=None, 
            num_homes=350,
            excl_ar=False, 
            excl_ss=False,
            time_on_market_range:Literal["1-", "3-", "7-", "14-", "30-", "-7", "-14", "-30", "-45", "-60", "-90", "-180"]=None,
            redfin_listings_only=False,
            financing_type:Literal["FHA", "VA"]=None,
            pool_type:Literal["private", "community", "private_or_community", "no_private_pool"]=None,
            sort_by=None,
        ):
        req = self.request.polygon_search(coordinates_list=coordinates_list, home_types=home_types,
                                         num_beds=num_beds, max_num_beds=max_num_beds, num_baths=num_baths,
                                         num_homes=num_homes, excl_ar=excl_ar, excl_ss=excl_ss, 
                                         time_on_market_range=time_on_market_range, redfin_listings_only=redfin_listings_only,
                                         financing_type=financing_type, pool_type=pool_type, sort_by=sort_by)
        
        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))

        return rawdata


    def query_region(self, location:str):
        req = self.request.query_region(location)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))

        data = self._compact_region_data(rawdata)

        return data
    

    def _compact_region_data(self, rawdata):
        data = []

        for region in rawdata["regions"]:
            name = region.get("name")
            cleaned_name = region.get("cleanedName")
            region_id = region.get("id", {}).get("tableId")
            region_type = region.get("id", {}).get("type")
            region_type_name = RF_REGION_TYPE_REVERSE_MAP.get(str(region_type))
            market = region.get("market")
            market_display = region.get("market_display_name")
            
            url: str = region.get("url")

            url_fragments = {
                "type": None,
                "id": None,
                "state_abbrv": None,
                # "city": None,
                # "neighborhood": None,
                # "slug_name": None,
            }
            
            url_split = url.removeprefix("/").split("/")
            if url_split[0] == "city":
                url_fragments["type"] = url_split[0]
                url_fragments["id"] = url_split[1]
                url_fragments["state_abbrv"] = url_split[2]
                # url_fragments["slug_name"] = url_split[3]
            elif url_split[0] == "zipcode":
                pass
                # url_fragments["type"] = url_split[0]
                # url_fragments["id"] = url_split[1]
                # url_fragments["state_abbrv"] = url_split[2]
            elif url_split[0] == "neighborhood":
                url_fragments["type"] = url_split[0]
                url_fragments["id"] = url_split[1]
                url_fragments["state_abbrv"] = url_split[2]
                # url_fragments["city"] = url_split[2]
                # url_fragments["slug_name"] = url_split[3]
            elif url_split[0] == "school":
                url_fragments["type"] = url_split[0]
                url_fragments["id"] = url_split[1]
                url_fragments["state_abbrv"] = url_split[2]
                # url_fragments["city"] = url_split[2]
                # url_fragments["slug_name"] = url_split[3]

            polygon = region.get("polygon", "")


            data.append({
                "name": name,
                "cleaned_name": cleaned_name,
                "market": market,
                "market_display": market_display,
                "region_id": region_id,
                "region_type": region_type,
                "region_type_name": region_type_name,
                "url": url,
                "url_fragments": url_fragments,
                "polygon": polygon,
            })

        # return data
        return rawdata


    class request:
        @staticmethod
        def map_search(
            coordinates:tuple[float],
            radius_mi:int=None,
            home_types:list[Literal["home", "condo", "townhouse", "multi-family", "land", "other", "mobile", "co-op"]]=None,
            num_beds=None,
            max_num_beds=None,
            num_baths=None, 
            num_homes=350,
            excl_ar=False, 
            excl_ss=False,
            time_on_market_range:Literal["1-", "3-", "7-", "14-", "30-", "-7", "-14", "-30", "-45", "-60", "-90", "-180"]=None,
            redfin_listings_only=False,
            financing_type:Literal["FHA", "VA"]=None,
            pool_type:Literal["private", "community", "private_or_community", "no_private_pool"]=None,
            sort_by=None,
            ):
            url = "https://www.redfin.com/stingray/api/gis"

            radius_mi = radius_mi if radius_mi != None else 5
            bbox = get_bounding_box(float(coordinates[0]), float(coordinates[1]), radius=radius_mi)
            poly = f'{bbox["west"]} {bbox["north"]},{bbox["east"]} {bbox["north"]},{bbox["east"]} {bbox["south"]},{bbox["west"]} {bbox["south"]},{bbox["west"]} {bbox["north"]}'

            # listing types
            sf = "1,2,3,4,5,6,7"

            if financing_type != None:
                financing_type = RF_FINANCING_TYPE_MAP[str(financing_type).upper()]

            if pool_type != None:
                pool_type = RF_POOL_TYPE_MAP[str(pool_type)]

            rdfn_lst = redfin_listings_only            

            if home_types == None:
                home_types = ["1"]
            else:
                home_types = [str(RF_UIPT_MAP[x]) for x in home_types]

            sort_by = "redfin-recommended-asc" if sort_by != None else None

            params = {
                "al": "1",
                "include_nearby_homes": "true",
                "mpt": "99",
                "num_beds": num_beds,
                "max_num_beds": max_num_beds,
                "num_baths": num_baths,
                "num_homes": num_homes,
                "ord": sort_by,
                "page_number": "1",
                "poly": poly,
                # "region_id": "25756",
                # "region_type": "2",
                "pool_types": pool_type,
                "sf": sf,
                "start": "0",
                "status": "9",
                "uipt": ",".join(home_types),
                "v": "8",
                "excl_ar": excl_ar,
                "excl_ss": excl_ss,
                "time_on_market_range": time_on_market_range,
                "financing_type": financing_type,
                "rdfn_lst": rdfn_lst,
            }

            headers = Redfin.request._headers()

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req


        @staticmethod
        def region_search(
            region_id,
            region_type:Literal["zipcode", "city", "county", "neighborhood"],
            home_types:list[Literal["home", "condo", "townhouse", "multi-family", "land", "other", "mobile", "co-op"]]=None,
            num_beds=None,
            max_num_beds=None,
            num_baths=None, 
            num_homes=350,
            excl_ar=False, 
            excl_ss=False,
            time_on_market_range:Literal["1-", "3-", "7-", "14-", "30-", "-7", "-14", "-30", "-45", "-60", "-90", "-180"]=None,
            redfin_listings_only=False,
            financing_type:Literal["FHA", "VA"]=None,
            pool_type:Literal["private", "community", "private_or_community", "no_private_pool"]=None,
            sort_by=None,
            ):

            url = "https://www.redfin.com/stingray/api/gis"

            region_type = RF_REGION_TYPE_MAP.get(region_type, str(region_type))

            # listing types
            sf = "1,2,3,4,5,6,7"

            if financing_type != None:
                financing_type = RF_FINANCING_TYPE_MAP[str(financing_type).upper()]

            if pool_type != None:
                pool_type = RF_POOL_TYPE_MAP[str(pool_type)]

            rdfn_lst = redfin_listings_only            

            if home_types == None:
                home_types = ["1"]
            else:
                home_types = [str(RF_UIPT_MAP[x]) for x in home_types]

            sort_by = "redfin-recommended-asc" if sort_by != None else None

            params = {
                "region_id": region_id,
                "region_type": region_type,
                "al": "1",
                "include_nearby_homes": "true",
                "mpt": "99",
                "num_beds": num_beds,
                "max_num_beds": max_num_beds,
                "num_baths": num_baths,
                "num_homes": num_homes,
                "ord": sort_by,
                "page_number": "1",
                "pool_types": pool_type,
                "sf": sf,
                "start": "0",
                "status": "9",
                "uipt": ",".join(home_types),
                "v": "8",
                "excl_ar": excl_ar,
                "excl_ss": excl_ss,
                "time_on_market_range": time_on_market_range,
                "financing_type": financing_type,
                "rdfn_lst": rdfn_lst,
            }

            headers = Redfin.request._headers()

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req


        @staticmethod
        def polygon_search(
            coordinates_list:list[tuple[float, float]],
            home_types:list[Literal["home", "condo", "townhouse", "multi-family", "land", "other", "mobile", "co-op"]]=None,
            num_beds=None,
            max_num_beds=None,
            num_baths=None, 
            num_homes=350,
            excl_ar=False, 
            excl_ss=False,
            time_on_market_range:Literal["1-", "3-", "7-", "14-", "30-", "-7", "-14", "-30", "-45", "-60", "-90", "-180"]=None,
            redfin_listings_only=False,
            financing_type:Literal["FHA", "VA"]=None,
            pool_type:Literal["private", "community", "private_or_community", "no_private_pool"]=None,
            sort_by=None,
            ):

            url = "https://www.redfin.com/stingray/api/gis"

            user_poly_list = [f"{c[1]} {c[0]}" for c in coordinates_list]
            user_poly = ",".join(user_poly_list)

            # listing types
            sf = "1,2,3,4,5,6,7"

            if financing_type != None:
                financing_type = RF_FINANCING_TYPE_MAP[str(financing_type).upper()]

            if pool_type != None:
                pool_type = RF_POOL_TYPE_MAP[str(pool_type)]

            rdfn_lst = redfin_listings_only            

            if home_types == None:
                home_types = ["1"]
            else:
                home_types = [str(RF_UIPT_MAP[x]) for x in home_types]

            sort_by = "redfin-recommended-asc" if sort_by != None else None

            params = {
                "user_poly": user_poly,
                "al": "1",
                "include_nearby_homes": "true",
                "mpt": "99",
                "num_beds": num_beds,
                "max_num_beds": max_num_beds,
                "num_baths": num_baths,
                "num_homes": num_homes,
                "ord": sort_by,
                "page_number": "1",
                "pool_types": pool_type,
                "sf": sf,
                "start": "0",
                "status": "9",
                "uipt": ",".join(home_types),
                "v": "8",
                "excl_ar": excl_ar,
                "excl_ss": excl_ss,
                "time_on_market_range": time_on_market_range,
                "financing_type": financing_type,
                "rdfn_lst": rdfn_lst,
            }

            headers = Redfin.request._headers()

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req


        @staticmethod
        def query_region(location:str):
            url = "https://www.redfin.com/stingray/do/query-location"

            params = {
                "al": 1,
                "location": location,
                "v": "1",
            }

            headers = Redfin.request._headers()

            req = httpx.Request("GET", url, params=params, headers=headers)

            return req


        @staticmethod
        def _headers():
            return {
                "accept": "*/*",
                "accept-language": "en-GB,en;q=0.5",
                "accept-encoding": "gzip, deflate, br, zstd",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "host": "www.redfin.com",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            }

