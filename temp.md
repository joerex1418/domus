# Redfin API Parameters Documentation

This document provides a detailed summary of the parameters used in the Redfin API queries.

```python
# agent-listed homes = 1,7
# mls-listed foreclosure = 2
# for sale by owner = 3
# foreclosures = 4
# new construction = 5,6
sf = "1,2,3,4,5,6,7"

# Home features

# wd - washer/dryery
# wf - waterfront
# ac - air conditioning
# view - has view
# fixer - fixer-upper
# primary_bed_on_main
# green - green home
# accessible - accessible home
# fireplace
# pets_allowed
# guest_house
# elevator
# rv_parking
# basement_types: finished/unfinished = 0,1,3 | finished = 1 | unfinished = 3
# garage spots - pkg (1- 2- 3- 4- 5-)
```


## Common Parameters

1. **`al`**: 
   - Description: Likely a binary flag (e.g., `1` for enabled).

2. **`basement_types`**:
   - Description: Specifies types of basements (numerical codes).
   - Example Values: `0,1,3`

3. **`include_nearby_homes`**:
   - Description: Boolean flag to include nearby homes in the search.
   - Example Values: `true`

4. **`market`**:
   - Description: Specifies the market or location.
   - Example Values: `chicago`

5. **`max_listing_approx_size`**:
   - Description: Filters for the maximum approximate size of the listing.
   - Example Values: `10000`

6. **`max_sqft`**:
   - Description: Filters for the maximum square footage.
   - Example Values: `10000`

7. **`min_listing_approx_size`**:
   - Description: Filters for the minimum approximate size of the listing.
   - Example Values: `750`

8. **`min_sqft`**:
   - Description: Filters for the minimum square footage.
   - Example Values: `750`

9. **`min_stories`**:
   - Description: Filters for the minimum number of stories.
   - Example Values: `2`

10. **`mpt`**:
    - Description: Likely indicates a specific property type or another category.
    - Example Values: `99`

11. **`num_baths`**:
    - Description: Filters for the number of bathrooms.
    - Example Values: `1.5`, `2.5`

12. **`num_beds`**:
    - Description: Filters for the number of bedrooms.
    - Example Values: `1`, `2`

13. **`num_homes`**:
    - Description: Limits the number of homes in the result.
    - Example Values: `350`

14. **`ord`**:
    - Description: Sorting order of the results.
    - Example Values:
        - `redfin-recommended-asc`
        - `days-on-redfin-asc`
        - `price-asc`
        - `price-desc`
        - `square-footage-desc`
        - `lot-sq-ft-desc`
        - `dollars-per-sq-ft-asc`

15. **`page_number`**:
    - Description: The page number of the results.
    - Example Values: `1`

16. **`poly`**:
    - Description: Specifies the polygon area for the search.
    - Example Values: Latitude and Longitude coordinates.

17. **`pool_types`**:
    - Description: Filters for homes with certain types of pools.
    - Example Values: `4`

18. **`sf`**:
    - Description: Specifies the types of single-family homes.
    - Example Values: `1,2,5,6,7`

19. **`start`**:
    - Description: The starting index of the result set.
    - Example Values: `0`

20. **`status`**:
    - Description: Represents the status of the listing.
    - Example Values:
        - `1`   = active
        - `8`   = coming soon
        - `9`   = active | coming soon
        - `130` = under contract/pending
        - `131` = active | under contract/pending
        - `138` = coming soon | under contract/pending
        - `139` = active | coming soon | under contract/pending

21. **`time_on_market_range`**:
    - Description: Filters by the time the property has been on the market.
    - Example Values: `7-`, `-30`

22. **`uipt`**:
    - Description: Represents the type of home.
    - Example Values:
        - `1` = home
        - `2` = condo
        - `3` = townhouse
        - `4` = multi-family
        - `5` = land
        - `6` = other
        - `7` = mobile
        - `8` = co-op

23. **`v`**:
    - Description: Likely a version number.
    - Example Values: `8`

24. **`zoomLevel`**:
    - Description: The zoom level for the map.
    - Example Values: `12`, `13`

25. **`excl_ar`**:
    - Description: Excludes homes with specific attributes (likely active rentals).
    - Example Values: `true`

26. **`excl_ss`**:
    - Description: Excludes short sales.
    - Example Values: `true`

27. **`max_parcel_size`**:
    - Description: Filters by maximum parcel size (in square feet).
    - Example Values: `435600`, `1742400`

28. **`max_stories`**:
    - Description: Filters for the maximum number of stories.
    - Example Values: `3`, `4`

29. **`min_parcel_size`**:
    - Description: Filters by minimum parcel size (in square feet).
    - Example Values: `2000`

30. **`min_stories`**:
    - Description: Filters for the minimum number of stories.
    - Example Values: `1`

31. **`pkg`**:
    - Description: Likely filters for parking availability.
    - Example Values: `2-`

32. **`hoa`**:
    - Description: Filters based on Homeowner Association fees.
    - Example Values: `0` (possibly for no fees)

33. **`max_price_per_sqft`**:
    - Description: Filters by maximum price per square foot.
    - Example Values: `400`

34. **`max_property_tax`**:
    - Description: Filters by maximum property tax.
    - Example Values: `14000`

35. **`max_year_built`**:
    - Description: Filters by the maximum year the property was built.
    - Example Values: `2023`

36. **`min_price_per_sqft`**:
    - Description: Filters by minimum price per square foot.
    - Example Values: `50`

37. **`min_year_built`**:
    - Description: Filters by the minimum year the property was built.
    - Example Values: `1940`

38. **`region_id`**:
    - Description: Identifies the specific region for the search.
    - Example Values: `25756`

39. **`region_type`**:
    - Description: Indicates the type of region (e.g., city, neighborhood).
    - Example Values: `2`

40. **`insurance_rate`**:
    - Description: Represents the insurance rate used in calculations.
    - Example Values: `0.44`, `0.45`

41. **`interest_rate`**:
    - Description: Represents the interest rate used in calculations.
    - Example Values: `6.795`

42. **`mortgage_down_payment_percent`**:
    - Description: Represents the down payment percentage.
    - Example Values: `20`

43. **`mortgage_term`**:
    - Description: Represents the mortgage term.
    - Example Values: `1`, `2`

44. **`mortgage_down_payment_amount`**:
    - Description: Represents the down payment amount.
    - Example Values: `50000`

45. **`max_monthly_payment`**:
    - Description: Filters by maximum monthly payment.
    - Example Values: `40000`

46. **`min_monthly_payment`**:
    - Description: Filters by minimum monthly payment.
    - Example Values: `1000`

47. **`rdfn_lst`**:
    - Description: Unspecified, likely related to listing details.

48. **`open_house`**:
    - Description: Filters for open house events.
    - Example Values:
        - `1` = any time
        - `2` = this weekend

49. **`financing_type`**:
    - Description: Represents the type of financing.
    - Example Values:
        - `1` = FHA
        - `2` = VA

50. **`has_virtual_tour`**:
    - Description: Filters for listings with virtual tours.
    - Example Values: `true`

51. **`virtual_tour`**:
    - Description: Filters for listings with virtual tours.
    - Example Values: `true`


