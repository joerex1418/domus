from typing import Literal
from copy import deepcopy

import httpx
import orjson

from ._geo import get_bounding_box
from ._util import readjson
from ._util import always_get
from ._http import fetch_bulk
from .paths import JSON_DIR
from ._constants import RF_UIPT_MAP
from ._constants import RF_POOL_TYPE_MAP
from ._constants import RF_REGION_TYPE_MAP
from ._constants import RF_FINANCING_TYPE_MAP
from ._constants import RF_REGION_TYPE_REVERSE_MAP

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


    def query_search(
            self, 
            query: str, 
            **kwargs
        ):
        req = self.request.query_region(query)

        client = httpx.Client()

        r = client.send(req)
        
        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))

        lookup_data = self._compact_region_data(rawdata)
        region_id = lookup_data.get("regions", [{}])[0].get("id", {}).get("tableId")
        region_type = lookup_data.get("regions", [{}])[0].get("id", {}).get("type")

        req = self.request.search_by_region_id(region_id, region_type, **kwargs)
        r = client.send(req)

        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))
        
        client.close()

        data = self.normalize.property_search(rawdata)
        return data
        return rawdata


    def region_lookup(self, query:str):
        req = self.request.query_region(query)

        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))

        data = self._compact_region_data(rawdata)

        return data
    

    def search_by_region_id(
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
        """
        Search for properties by region id
        """
        req = self.request.search_by_region_id(
            region_id=region_id, 
            region_type=region_type, 
            home_types=home_types,
            num_beds=num_beds, 
            max_num_beds=max_num_beds, 
            num_baths=num_baths,
            num_homes=num_homes, 
            excl_ar=excl_ar, 
            excl_ss=excl_ss,
            time_on_market_range=time_on_market_range, 
            redfin_listings_only=redfin_listings_only,
            financing_type=financing_type, 
            pool_type=pool_type, 
            sort_by=sort_by
        )
        
        with httpx.Client() as client:
            r = client.send(req)
        
        rawdata = orjson.loads(r.content.replace(b"{}&&", b""))

        data = rawdata.get("payload", {}).get("homes")

        return data


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


    def property_details(self, property_id, listing_id=None):
        """
        /stingray/api/home/details/propertyParcelInfo?propertyId=18049742&accessLevel=1&listingId=193320119
        /stingray/api/home/details/belowTheFold?propertyId=18049742&accessLevel=1&listingId=193320119
        /stingray/api/home/details/aboveTheFold?propertyId=18049742&accessLevel=1&listingId=193320119

        """
        # /stingray/api/home/details/listing/floorplans?listingId=193320119
        # /stingray/api/home/details/avmHistoricalData?propertyId=18049742&accessLevel=1&listingId=193320119
        # /stingray/api/home/details/avm?propertyId=18049742&accessLevel=1&listingId=193320119
        # /stingray/api/home/details/mainHouseInfoPanelInfo?propertyId=18049742&accessLevel=1&listingId=193320119
        request_list = [
            self.request.above_the_fold(property_id, listing_id),
            self.request.below_the_fold(property_id, listing_id),
            self.request.avm(property_id, listing_id),
            self.request.property_parcel_info(property_id, listing_id),
        ]

        responses = fetch_bulk(request_list)

        all_data = {}
        for r in responses:
            endpoint = r.url.path[r.url.path.rfind("/")+1:]
            all_data[endpoint] = orjson.loads(r.content.replace(b"{}&&", b""))
        

        return all_data


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


    def _generate_photo_url(self, datasource_id, mls_id, photo_num:int=0):
        # url = "https://ssl.cdn-redfin.com/photo/{database_id}/bigphoto/{mls_id}/genIslnoResize.{mls_id}_0.jpg"
        full_mls_id = str(mls_id)
        mls_id = full_mls_id[-3:]
        photo_num = int(photo_num)
        
        if photo_num == 0:
            url = f"https://ssl.cdn-redfin.com/photo/{datasource_id}/bigphoto/{mls_id}/{full_mls_id}_0.jpg"
        else:
            url = f"https://ssl.cdn-redfin.com/photo/{datasource_id}/bigphoto/{mls_id}/{full_mls_id}_{photo_num}_0.jpg"
        
        return url
    
    def _generate_photo_url2(self, datasource_id, mls_id, photo_num:int=0):
        # url = "https://ssl.cdn-redfin.com/photo/{database_id}/bigphoto/{mls_id}/genIslnoResize.{mls_id}_0.jpg"
        full_mls_id = str(mls_id)
        mls_id = full_mls_id[-3:]
        photo_num = int(photo_num)
        
        if photo_num == 0:
            url = f"https://ssl.cdn-redfin.com/photo/{datasource_id}/bigphoto/{mls_id}/{full_mls_id}_0.jpg"
        else:
            url = f"https://ssl.cdn-redfin.com/photo/{datasource_id}/bigphoto/{mls_id}/{full_mls_id}_{photo_num}_0.jpg"
        
        return url


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
        def search_by_region_id(
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


            if home_types == None:
                home_types = ["1"]
            else:
                home_types = [str(RF_UIPT_MAP[x]) for x in home_types]

            sort_by = "redfin-recommended-asc" if sort_by == None else sort_by

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
                "rdfn_lst": redfin_listings_only,
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
        def above_the_fold(property_id, listing_id=None):
            url = "https://www.redfin.com/stingray/api/home/details/aboveTheFold"

            params = {"propertyId": property_id, "accessLevel": "1"}
            
            if listing_id:
                params["listingId"] = listing_id
            
            req = httpx.Request("GET", url, params=params, headers=Redfin.request._headers())

            return req


        @staticmethod
        def below_the_fold(property_id, listing_id=None):
            url = "https://www.redfin.com/stingray/api/home/details/belowTheFold"

            params = {"propertyId": property_id, "accessLevel": "1"}
            
            if listing_id:
                params["listingId"] = listing_id
            
            req = httpx.Request("GET", url, params=params, headers=Redfin.request._headers())

            return req


        @staticmethod
        def main_house_info(property_id, listing_id=None):
            url = "https://www.redfin.com/stingray/api/home/details/mainHouseInfoPanelInfo"

            params = {"propertyId": property_id, "accessLevel": "1"}
            
            if listing_id:
                params["listingId"] = listing_id
            
            req = httpx.Request("GET", url, params=params, headers=Redfin.request._headers())

            return req


        @staticmethod
        def avm(property_id, listing_id=None):
            url = "https://www.redfin.com/stingray/api/home/details/avm"
            
            params = {"propertyId": property_id, "accessLevel": "1"}
            
            if listing_id:
                params["listingId"] = listing_id
            
            req = httpx.Request("GET", url, params=params, headers=Redfin.request._headers())

            return req


        @staticmethod
        def property_parcel_info(property_id, listing_id=None):
            url = "https://www.redfin.com/stingray/api/home/details/propertyParcelInfo"

            params = {"propertyId": property_id, "accessLevel": "1"}
            
            if listing_id:
                params["listingId"] = listing_id
            
            req = httpx.Request("GET", url, params=params, headers=Redfin.request._headers())

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


    class normalize:
        @staticmethod
        def property_search(response_data):
            # Load the template
            template = readjson(JSON_DIR.joinpath("listing_search.json"))
            
            normalized_data = []
            i = 0
            for property in response_data.get("payload", {}).get("homes", []):
                i += 1
                property_data = deepcopy(template)

                # mls_id = always_get("mlsId", property, {}).get("value")
                mls_id = property.get("mlsId", {}).get("value")
                datasource_id = property.get("dataSourceId")
                
                # Address information
                property_data["address"]["street"] = always_get("streetLine", property, {}).get("value")
                property_data["address"]["city"] = property.get("city")
                property_data["address"]["state"] = property.get("state")
                property_data["address"]["postal_code"] = always_get("postalCode", property, {}).get("value")
                property_data["address"]["country_code"] = property.get("countryCode", "US")
                print(property["url"])
                # Latitude and Longitude
                _latlong = always_get("latLong", property, {}).get("value", {})
                property_data["address"]["lat"] = _latlong.get("latitude")
                property_data["address"]["lon"] = _latlong.get("longitude")
                
                # Price information
                property_data["price"] = always_get("price", property, {}).get("value")
                
                # Number of beds and baths
                property_data["num_beds"] = property.get("beds")
                property_data["num_baths"] = property.get("baths")
                
                # Images
                property_data["images"] = []
                image_keys: str = always_get("photos", property, {}).get("value")
                if image_keys:
                    property_data["images"].extend(parse_photos(image_keys, mls_id, datasource_id))

                # property_data["images"] = [
                #     always_get("photos", property, {}).get("value")
                # ]
                
                # Agent information
                _agent = always_get("listingAgent", property, {})
                property_data["agent_name"] = _agent.get("name")
                property_data["agency_name"] = None  # No agency info in Redfin data
                
                # Price history (not available in the Redfin sample data)
                property_data["price_history"] = []
                
                # Database fields
                property_data["db_listing_id"] = property.get("listingId")
                property_data["db_property_id"] = property.get("propertyId")
                property_data["db_name"] = "Redfin"

                normalized_data.append(property_data)
            
            return normalized_data


def parse_photos(photos_value, mls_id, datasource_id):
    base_url = f"https://ssl.cdn-redfin.com/photo/{datasource_id}/bigphoto/{mls_id[-3:]}/{mls_id}"
    
    photo_urls = []

    photo_ranges = photos_value.split(",")

    for item in photo_ranges:
        range_part, level = item.split(":")
        level = str(level).strip()
            
        if "-" in range_part:
            start, end = map(int, range_part.split("-"))
        else:
            start = end = int(range_part)

        for photo_id in range(start, end + 1):
            if str(photo_id) == "0" and str(level) == "0":
                # Special case: no level for photo ID 0 and level 0
                photo_url = f"{base_url}_0.jpg"
            else:
                photo_url = f"{base_url}_{photo_id}_{level}.jpg"
            photo_urls.append(photo_url)

    return photo_urls