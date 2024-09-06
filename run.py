import json

import rich
import httpx

from src import geo
from src._api import Realtor
from src._api import Zillow
from src._api import Redfin
from src._util import readjson
from src._util import readfile
from src._util import savejson


realtor = Realtor()
zillow = Zillow()
redfin = Redfin()

