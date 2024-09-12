import json
from typing import Literal

import rich
import httpx
import orjson

from ._geo import get_bounding_box
from ._constants import ZI_REGION_TYPE_MAP
from ._http import send_request
from ._util import readjson
from ._util import readfile
from ._util import read_payload
from ._util import read_graphql
from .paths import QUERY_DIR

_Polygon = list[tuple[float, float]]
_MultiPolygon = list[list[tuple[float, float]]]

class Zillow:
    def __init__(self):
        pass

    def map_search(
            self, 
            coordinates:tuple[float, float], 
            radius_mi: int | None = None, 
            price_min: int | None = None,
            price_max: int | None = None,
            num_beds_min: int | None = None,
            num_beds_max: int | None = None,
            num_baths_min: int | float | None = None,
            num_baths_max: int | float | None = None,
            include_pending_listings: bool | None = None,
            include_accepting_offers: bool | None = None,
            open_houses_only: bool | None = None,
            has_3d_tour_only: bool | None = None,
            year_built_min: int | None = None,
            year_built_max: int | None = None,
            has_finished_basement: bool | None = None,
            has_unfinished_basement: bool | None = None,
            has_garage: bool | None = None,
            age_55plus_only: bool | None = None,
            single_story_only: bool | None = None,
            has_ac: bool | None = None,
            has_pool: bool | None = None,
            doz:Literal["1","7","14","30","90","6m","12m","24m","36m"]|None=None,
            limit: int | None = None,
            page: int | None = None,
            sort_order:Literal["globalrelevanceex", "days", "beds", "baths", "lot", "paymentd", "paymenta", "featured", "size", "zest", "zesta", "pricea", "priced", "mostrecentchange", "listingstatus"]|None=None,
            ):
        
        # TODO: add all the same parameters as region_search
        # TODO: also involves re-configuring the request.map_search() method
        
        req = Zillow.request.map_search(
            coordinates=coordinates,
            radius_mi=radius_mi,
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
        
        with httpx.Client() as client:
            r = client.send(req)

        rawdata = orjson.loads(r.content)

        return rawdata


    def map_search1(
            self, 
            coordinates: tuple[float, float], 
            radius_mi: int | None = None, 
            price_range_min: int | None=None,
            price_range_max: int | None=None,
            num_beds_min: int | None=None,
            num_beds_max: int | None=None,
            num_baths_min: int | float | None=None,
            limit: int | None=None,
            page: int | None=None,
            ):
        
        req = self.request.map_search1(
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
        polygon: _Polygon | None=None, 
        multi_polygon: _MultiPolygon | None=None,
        price_range_min: int | None=None,
        price_range_max: int | None=None,
        num_beds_min: int | None = None,
        num_beds_max: int | None = None,
        num_baths_min: int | float | None = None,
        limit:int | None=None,
        page:int | None=None,
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

        r = send_request(req)

        rawdata = orjson.loads(r.content)

        return rawdata


    def query_search(
            self, 
            query, 
            region_type:Literal["city", "zipcode", "neighborhood", "address"]=None,
            coordinates:list[tuple[float, float]]=None,
            price_min: int | None = None,
            price_max: int | None = None,
            num_beds_min: int | None = None,
            num_beds_max: int | None = None,
            num_baths_min: int | float | None = None,
            num_baths_max: int | float | None = None,
            include_pending_listings: bool | None = None,
            include_accepting_offers: bool | None = None,
            open_houses_only: bool | None = None,
            has_3d_tour_only: bool | None = None,
            year_built_min: int | None = None,
            year_built_max: int | None = None,
            has_finished_basement: bool | None = None,
            has_unfinished_basement: bool | None = None,
            has_garage: bool | None = None,
            age_55plus_only: bool | None = None,
            single_story_only: bool | None = None,
            has_ac: bool | None = None,
            has_pool: bool | None = None,
            doz:Literal["1","7","14","30","90","6m","12m","24m","36m"]|None=None,
            limit: int | None = None,
            page: int | None = None,
            sort_order:Literal["globalrelevanceex", "days", "beds", "baths", "lot", "paymentd", "paymenta", "featured", "size", "zest", "zesta", "pricea", "priced", "mostrecentchange", "listingstatus"]|None=None,
        ):
        """
        Standard query search
        """

        with httpx.Client() as client:
            req = self.request.query_understanding(query)
            r = client.send(req)
            query_data = self._compact_query_understanding(orjson.loads(r.content))

            if region_type != None:
                for result in query_data:
                    if str(result["sub_type"]).lower() == region_type.strip().lower():
                        region_id = result["region_id"]
                        region_type = result["sub_type"]
                        coordinates = result["polygon"] # list[tuple[lng, lat]]
                        break
            else:
                result = query_data[0]
                region_id = result["region_id"]
                region_type = result["sub_type"]
                coordinates = result["polygon"] # list[tuple[lng, lat]]

            req = self.request.region_lookup(
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
        
        data = rawdata.get("cat1", {}).get("searchResults", {}).get("listResults")
        
        return data
        

    def property_details(self, zpid):
        req = self.request.property_details(zpid)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content)

        return rawdata


    def region_lookup(self, query:str):
        req = Zillow.request.query_understanding(query)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content)

        data = self._compact_query_understanding(rawdata)
        # data = rawdata

        return data
    

    def autocomplete(self, query_string:str):
        req = self.request.autocomplete_results(query_string)

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
            radius_mi: int | None = None, 
            price_min: int | None = None,
            price_max: int | None = None,
            num_beds_min: int | None = None,
            num_beds_max: int | None = None,
            num_baths_min: int | float | None = None,
            num_baths_max: int | float | None = None,
            include_pending_listings: bool | None = None,
            include_accepting_offers: bool | None = None,
            open_houses_only: bool | None = None,
            has_3d_tour_only: bool | None = None,
            year_built_min: int | None = None,
            year_built_max: int | None = None,
            has_finished_basement: bool | None = None,
            has_unfinished_basement: bool | None = None,
            has_garage: bool | None = None,
            hide_55plus: bool | None = None,
            single_story_only: bool | None = None,
            has_ac: bool | None = None,
            has_pool: bool | None = None,
            doz:Literal["1","7","14","30","90","6m","12m","24m","36m"]|None=None,
            page: int | None = None,
            limit: int | None = None,
            sort_order:Literal["globalrelevanceex", "days", "beds", "baths", "lot", "paymentd", "paymenta", "featured", "size", "zest", "zesta", "pricea", "priced", "mostrecentchange", "listingstatus"]|None=None,
        
            ) -> httpx.Request:

            radius_mi = int(radius_mi) if radius_mi != None else 5
            bbox = get_bounding_box(coordinates[0], coordinates[1], radius=radius_mi)
            
            url = "https://www.zillow.com/async-create-search-page-state"
            
            headers = Zillow.request._desktop_headers()

            payload = read_payload("zillow-searchQueryState.json")

            payload["searchQueryState"].pop("regionSelection")

            payload["searchQueryState"]["mapBounds"] = {
                "northLatitude": bbox["north"],
                "southLatitude": bbox["south"],
                "eastLongitude": bbox["east"],
                "westLongitude": bbox["west"],
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
                payload["searchQueryState"]["filterState"]["doz"] = {"value": str(doz)}

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

            page = int(page) if page != None else 1
            payload["searchQueryState"]["pagination"]["currentPage"] = page

            req = httpx.Request("PUT", url, headers=headers, json=payload)

            return req
        

        @staticmethod
        def map_search1(
            coordinates:tuple[float, float], 
            radius_mi: int | None = None, 
            price_min:int | None=None,
            price_max:int | None=None,
            num_beds_min:int | None=None,
            num_beds_max:int | None=None,
            num_baths_min: int | float | None = None,
            limit: int | None = None,
            page: int | None = None,
            ) -> httpx.Request:

            url = "https://zm.zillow.com/api/public/v2/mobile-search/homes/search"

            radius_mi = int(radius_mi) if radius_mi != None else 5
            price_min = int(price_min) if price_min != None else None
            price_max = int(price_max) if price_max != None else None
            limit = int(limit) if limit != None else 100

            if (price_min, price_max) == (None, None):
                price_max = 500000000

            bbox = get_bounding_box(coordinates[0], coordinates[1], radius=radius_mi)
            
            payload = read_payload("zillow-MapSearch.json")

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
            polygon:_Polygon | None = None, 
            multi_polygon: _MultiPolygon | None = None,
            price_range_min:int | None=None,
            price_range_max:int | None=None,
            num_beds_min:int | None=None,
            num_beds_max:int | None=None,
            num_baths_min: int | float | None = None,
            limit:int | None=None,
            page:int | None=None,
        ):
            url = "https://zm.zillow.com/api/public/v2/mobile-search/homes/search"

            payload = read_payload("zillow-clipPolygonSearch.json")

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
        def region_lookup(
            region_id, 
            region_type: str, 
            coordinates: list[tuple[float, float]],
            price_min: int | None = None,
            price_max: int | None = None,
            num_beds_min: int | None = None,
            num_beds_max: int | None = None,
            num_baths_min: int | float | None = None,
            num_baths_max: int | float | None = None,
            include_pending_listings: bool = False,
            include_accepting_offers: bool = False,
            open_houses_only: bool = False,
            has_3d_tour_only: bool | None = None,
            year_built_min: int | None = None,
            year_built_max: int | None = None,
            has_finished_basement: bool | None = None,
            has_unfinished_basement: bool | None = None,
            has_garage: bool | None = None,
            hide_55plus: bool = False,
            single_story_only: bool | None = None,
            has_ac: bool | None = None,
            has_pool: bool | None = None,
            doz: Literal["1","7","14","30","90","6m","12m","24m","36m"] | None = None,
            page: int | None = None,
            limit: int | None = None,
            sort_order: Literal["globalrelevanceex", "days", "beds", "baths", "lot", "paymentd", "paymenta", "featured", "size", "zest", "zesta", "pricea", "priced", "mostrecentchange", "listingstatus"] | None = None,
            ):

            url = "https://www.zillow.com/async-create-search-page-state"
            
            headers = Zillow.request._desktop_headers()

            payload = readjson(QUERY_DIR.joinpath("zillow-searchQueryState.json"))
            
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
                payload["searchQueryState"]["filterState"]["doz"] = {"value": str(doz)}

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

            page = int(page) if page != None else 1
            payload["searchQueryState"]["pagination"]["currentPage"] = page

            req = httpx.Request("PUT", url, headers=headers, json=payload)

            return req


        @staticmethod
        def autocomplete_results(query):
            query = str(query).strip()

            url = f"https://www.zillow.com/zg-graph"

            params = {
                "query": query,
                "queryOptions": "",
                "resultType": ["REGIONS", "FORSALE", "RENTALS", "SOLD", "BUILDER_COMMUNITIES"],
                "operationName": "getAutocompleteResults",
            }

            headers = Zillow.request._desktop_headers()

            payload = readjson(QUERY_DIR.joinpath("zillow-getAutocompleteResults.json"))

            payload["query"] = readfile(QUERY_DIR.joinpath("zillow-getAutocompleteResults.gql"))
            payload["variables"]["query"] = query

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
        def property_details2(zpid, referer: str) -> httpx.Request:
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
        def query_understanding(query: str) -> httpx.Request:
            url = "https://www.zillow.com/zg-graph"

            payload = readjson(QUERY_DIR.joinpath("zillow-QueryUnderstanding.json"))
            payload["variables"]["query"] = query

            headers = Zillow.request._mobile_headers_alt()

            req = httpx.Request("POST", url, headers=headers, json=payload)

            return req


        @staticmethod
        def property_affordability_estimate(zpid: str):
            url = "https://www.zillow.com/zg-graph"
            
            params = {
                "zpid": str(zpid),
                "operationName": "getAffordabilityEstimateFromPersonalizedPaymentChipMVP",
            }

            query = read_graphql("zillow-AffordabilityEstimate.gql")

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






