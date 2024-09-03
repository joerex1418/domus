import json

import rich
import httpx

from src import geo
from src.api import Realtor
from src.api import Zillow
from src.api import Redfin
from src.util import readjson
from src.util import readfile
from src.util import savejson


realtor = Realtor()
zillow = Zillow()
redfin = Redfin()



# data = osm.search(postalcode="60540", country="usa")

data = geo.polygon_city("Naperville", "IL")
# data = osm.polygon_zipcode(60540)
savejson(data, "polycity.json")
