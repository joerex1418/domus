import json

import rich
import httpx

from src.api import RealtorAPI
from src.api import ZillowAPI
from src.util import readjson
from src.util import readfile
from src.util import savejson


realtor = RealtorAPI()
zillow = ZillowAPI()

# data = realtor.map_search((41.8757, -88.386897), radius_mi=10)
# data = realtor.zipcode_search(60013)
# data = realtor.city_search("St Charles", "IL")
# data = realtor.property_and_tax_history("7037747684")
# data = realtor.property_details("7037747684")
# data = realtor.property_school_data("7037747684")
# data = realtor.property_estimates("7037747684")
# data = realtor.property_saves("7037747684")
# data = realtor.property_gallery("7037747684")


# url = "https://www.zillow.com/async-create-search-page-state"
# url = "https://zm.zillow.com/api/public/v2/mobile-search/homes/search"
# url = "https://www.zillow.com/async-create-search-page-state"


# data = zillow.coordinates_lookup((41.85770608977258, -88.05687809090907), radius_mi=5)
# data = zillow.query_understanding("Naperville IL")
# data = zillow.query_understanding("940 Pearson Rd Cary, IL")
data = zillow.property_lookup(5071833)

savejson(data, "temp.json")
