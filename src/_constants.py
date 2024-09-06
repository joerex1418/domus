RF_UIPT_MAP = {
    "home": 1,
    "condo": 2,
    "townhouse": 3,
    "multi-family": 4,
    "land": 5,
    "other": 6,
    "mobile": 7,
    "co-op": 8
}

RF_FINANCING_TYPE_MAP = {
    "FHA": "1",
    "VA": "2"
}

RF_POOL_TYPE_MAP = {
    "private": "1", 
    "community": "2", 
    "private_or_community": "3", 
    "no_private_pool": "4",
}

RF_REGION_TYPE_MAP = {
    "neighborhood": "1",
    "zipcode": "2",
    "county": "5",
    "city": "6",
}

RF_REGION_TYPE_REVERSE_MAP = {
    "1": "neighborhood",
    "2": "zipcode",
    "5": "county",
    "6": "city",
}

ZI_REGION_TYPE_MAP = {
    "state": "2",
    "county": "4",
    "city": "6",
    "zipcode": "7",
    "neighborhood": "17",
    "STATE": "2",
    "COUNTY": "4",
    "CITY": "6",
    "ZIPCODE": "7",
    "NEIGHBORHOOD": "17",
}

HM_PROPERTY_TYPE = {
    "house": 1,
    "townhouse": 2,
    "condo": 4,
    "co_op": 256,
    "lot_land": 32,
    "manufactured": 64,
    "multifamily": 16,
    "other": 8,
}

HM_LISTING_TYPE_MAP = {
    "resale": 1,
    "new_construction": 2,
    "short_sale": 4,
    "foreclosure": 8,
    "auction": 16,
    "pre_foreclosure": 64,
}

HM_LISTING_STATUS_MAP = {
    "under_contract": 1,
    "for_sale": 5,
    "pending": 6,
    "coming_soon": 7,
}

HM_LOT_SIZE = {
    "3000sqft": 0.068870523415978,
    "5000sqft": 0.114784205693297,
    "7000sqft": 0.160697887970615,
    "0.25acres": 0.25,
    "0.5acres": 0.5,
    "0.75acres": 0.75,
    "1acre": 1,
    "1.5acres": 1.5,
    "2acres": 2,
    "2.5acres": 2.5,
    "3acres": 3,
    "4acres": 4,
    "5acres": 5,
    "10acres": 10,
    "15acres": 15
}

HM_AMENITY_VIEW = {
    "mountains_hills": 20,
    "woods": 21,
    "water": 19,
    "city": 22,
    "other": 23,
}

# "exclude_senior_living": 53
# "garage_parking": 1

HM_AMENTITY_ARCHITSTYLE = {
    "mid_century_modern": 61,
    "modern_contemporary": 54,
    "ranch_style": 57,
    "spanish_mediterranean": 58,
    "farmhouse": 55,
    "colonial": 59,
    "craftsman": 56,
    "victorian": 60,
}

HM_AMENITY_INTERIOR = {
    "mainfloor_bedroom": 75,
    "elevator": 71,
    "inlaw_suite": 13,
    "upgraded_counters": 76,
    "kitchen_island": 82,
    "guest_house": 81,
    "walk_in_closet": 10,
    "dishwasher": 36,
    "fireplace": 6,
    "high_ceilings": 84,
    "furnished": 77,
    "skylights": 85,
    "laundry_in_unit": 32,
    "laundry_room": 78,
    "ev_charging": 86,
    "basement": 2,
    "attic": 79,
    "pet_friendly_unit": 31,
    "ada_friendly": 80,
    "eco_friendly": 83,
}

HM_AMENITY_FLOORING = {
    "hardwood": 11,
    "stone": 72,
    "marble": 73,
}

HM_AMENITY_OUTDOOR = {
    "private_pool": 7,
    "private_spa": 62,
    "deck": 63,
    "rooftop_deck": 64,
    "porch": 65,
    "balcony": 37,
    "patio": 66,
    "sports_court": 67,
    "tennis_court": 68,
    "boat_dock": 69
}

HM_AMENITY_LOT_DETAILS = {
    "corner_lot": 24,
    "waterfront": 17,
    "culdesac": 25,
    "yard": 74
}

HM_AMENITY_UTILITIES = {
    "central_ac": 16,
    "central_heat": 14,
    "solar": 87,
    "high_speed_internet": 88
}

HM_AMENITY_COMMUNITY = {
    "gated_community": 40,
    "valet": 30,
    "doorman": 28,
    "concierge": 29,
    "clubhouse": 41,
    "sauna": 43,
    "storage": 35,
    "laundry_facilities": 33,
    "pet_friendly": 70,
    "security": 44,
    "parking_garage": 42,
    "senior_living": 12
}

HM_AMENITY_RECREATION = {
    "community_pool": 5,
    "spa": 45,
    "bike_storage": 46,
    "golf_course": 18,
    "fitness_center": 47,
    "community_tennis_court": 48,
    "community_boat_dock": 49,
    "beach_access": 50,
    "horse_facilities": 51,
    "ski_accessible": 52
}

HM_SORT_TYPE = {
    "recommended": 0,
    "newest": 4,
    "price_lth": 1,
    "price_htl": 2,
    "price_reduced_date": 3,
    "sqft": 9,
    "price_sqft": 12,
    "open_house": 13,
    "num_beds": 7,
    "num_baths": 11,
}

HM_NICHE_GRADE = {
    "C": 7,
    "B": 4,
    "B+": 5,
    "A-": 3,
    "A": 1,
    "A+": 2,
}
HM_GREATSCHOOLS_RATING = {
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
}

HM_DAYS_ON_MARKET = {
    "any": 0,
    "new_listings": 1,
    "-3d": 2,
    "-7d": 3,
    "-1m": 4,
    "7d+": 5,
    "14d+": 6,
    "1m+": 7,
    "3m+": 8,
    "6m+": 9,
    "1y+": 10,
}

HM_SCHOOL_LEVELS = {
    "elementary": 4,
    "middle": 8,
    "high": 16
}

HM_PRICE_REDUCTION = {
    "any": 0,
    "1d": 1,
    "3d": 2,
    "7d": 3,
    "14d": 4,
    "30d": 5,
    "1m+": 6,
    "2m+": 7,
    "3m+": 8
}

HM_TOUR_TYPE = {
    "open_house": 1,
    "3d_virtual": 2,
    "video": 4,
}
