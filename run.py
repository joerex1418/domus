import json

import rich
import httpx

from src import _geo
from src._api import RealtorAPI
from src._api import ZillowAPI
from src._api import RedfinAPI
from src._util import readjson
from src._util import readfile
from src._util import savejson


realtor = RealtorAPI()
zillow = ZillowAPI()
redfin = RedfinAPI()

