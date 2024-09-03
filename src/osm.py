from typing import Literal

import httpx
import orjson


OSM_BASE = "https://nominatim.openstreetmap.org/search"
OSM_REVERSE_BASE = "https://nominatim.openstreetmap.org/reverse?lat=<value>&lon=<value>&<params>"
TIGER_WEB = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/1/query?where=&text=60606&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=geojson"
# polygon_geojson

def search(
        query:str=None,
        street_address:str=None,
        city:str=None,
        county:str=None,
        state:str=None,
        country:str=None,
        postalcode:str=None,
        format:Literal["jsonv2", "xml", "json", "geojson", "geocodejson"]="jsonv2",
        limit:int=10,
    ):
    params = {
        "query": query,
        "street": street_address,
        "city": city,
        "county": county,
        "state": state,
        "country": country,
        "postalcode": postalcode,
        "format": format,
        "limit": limit,
    }

    r = httpx.get(OSM_BASE, params=params)

    data = orjson.loads(r.content)

    return data