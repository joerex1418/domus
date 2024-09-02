import json

import rich
import httpx

from src import osm
from src.api import Realtor
from src.api import Zillow
from src.api import Redfin
from src.util import readjson
from src.util import readfile
from src.util import savejson


realtor = Realtor()
zillow = Zillow()
redfin = Redfin()



data = osm.search(postalcode="60540", country="usa")

savejson(data, "geotemp.json")
