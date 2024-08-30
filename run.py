import json

import rich
import httpx

from src.api import Realtor
from src.api import Zillow
from src.api import Redfin
from src.util import readjson
from src.util import readfile
from src.util import savejson


realtor = Realtor()
zillow = Zillow()
redfin = Redfin()

def polystring_to_list(polystring:str):
    polygon_coordinates = []
    for c in polystring.split("|"):
        c_tup = c.split(",")
        polygon_coordinates.append([float(c_tup[0]), float(c_tup[1])])

def string_to_polygon_tuples(polygon_str):
    # Check if the string starts with "clipPolygon=" and remove it
    if polygon_str.startswith("clipPolygon="):
        polygon_str = polygon_str.replace("clipPolygon=", "")
    
    # Split the string by ':' to separate different polygon groups
    polygon_groups = polygon_str.split(':')
    
    # Initialize the list that will hold the final output
    polygons = []
    
    for group in polygon_groups:
        if group:  # Only process non-empty groups
            # Split the group by '|' to separate individual points
            points = group.split('|')
            
            # Filter out any empty strings (which might occur if there's a trailing '|')
            points = [point for point in points if point]
            
            # Convert each point to a tuple of floats and add it to the list
            try:
                polygon = [tuple(map(float, point.split(','))) for point in points]
            except ValueError as e:
                # print(f"Error converting point to floats: {point} - {e}")
                raise e
            
            # Append the polygon to the list of polygons
            polygons.append(polygon)
    
    return polygons

def polygon_tuples_to_string(polygons):
    # Initialize the list that will hold the string for each polygon group
    polygon_strings = []
    
    for polygon in polygons:
        # Convert each tuple of floats back to a comma-separated string
        point_strings = [','.join(map(str, point)) for point in polygon]
        
        # Join the points with '|' to form the group string
        polygon_string = '|'.join(point_strings)
        
        # Add "|:" at the end of each polygon group
        polygon_strings.append(polygon_string + '|:')
    
    # Join all polygon group strings to form the final string
    final_string = ''.join(polygon_strings)
    
    return f"clipPolygon={final_string}"

x = string_to_polygon_tuples("clipPolygon=42.014001168938194,-88.1274867995979|42.01237913553621,-88.13647608175168|42.002836935291796,-88.14867582643629|41.98059805143459,-88.15740827582009|41.96933247911384,-88.14623587985079|41.96866411683953,-88.12376266564866|41.98689826608463,-88.09512537679024|41.998160731059386,-88.086007672373|42.009898299328704,-88.08408139720584|42.01619561399491,-88.09486853814174|42.01838998770148,-88.11143450457907|42.01829458324259,-88.12170797409655|42.01132956195521,-88.14020021570093|:41.95787391981295,-88.0573703835146|41.95854239091304,-88.06469022914965|41.95137982003279,-88.08010043048665|41.93179802086258,-88.09974843719135|41.91985494583403,-88.10578410134116|41.91297472070992,-88.10424308120747|41.909534330001556,-88.09396961168994|41.91268802856658,-88.0661028328984|41.927594312487145,-88.04144651075922|41.939535938751916,-88.03258564499042|41.953385421017565,-88.03091620259322|41.95968832755456,-88.03695186674304|41.963030526512846,-88.05107788659481|41.96131170397871,-88.06109451746384|41.95300340810504,-88.07046905465106|:")

# x = polygon_tuples_to_string(x)

print(x)

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
# data = zillow.property_lookup(5071833)


# data = redfin.map_search()

# savejson(data, "temp.json")
