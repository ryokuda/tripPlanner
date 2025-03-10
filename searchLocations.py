import requests
import json
import re
import sys

from environs import Env
import parameters

def searchLocations():
    print("")
    print("------ Step 2: Enumerate possible locations by TripAdvisor API search ------")

    # TripAdvisor Content API endpoint
    url = "https://api.content.tripadvisor.com/api/v1/location/search"

    # API key
    env = Env()
    env.read_env()
    api_key = env.str("TRIPADVISOR_API_KEY", "")

    # Load request parameters
    params_file = parameters.run_dir + "2.tripadvisorAccessParams.json"
    with open(params_file, "r", encoding="utf-8") as json_file:
        params = json.load(json_file)

    print(f'    Load search parameters from "{parameters.run_dir}2.tripadvisorAccessParams.json"')
    # print(json.dumps(params, indent=4, ensure_ascii=False))

    # params = [     Access TripAdvisor API
    #  {
    #    "searchQuery": "Rhine River Germany",
    #    "category": "geos"
    #  },
    #  ...
    #  {
    #    "searchQuery": "UNESCO World Heritage Rhine Valley",
    #    "category": "attractions"
    #  }
    # ]

    locations = []
    locationDetails = []

    print("    Accessing TripAdvisor's API to gather information of locations.")
    for p in params:
        keyword = p.get("searchQuery")
        latLong = p.get("latLong")
        category = p.get("category")
        param = {
            "key": api_key,
            "searchQuery": keyword,
            "category": category,
            "latLong": latLong,
            "radius": 10000,  # Search for tourist attractions within a 10km radius
            "radiusUnit": "m",
            "language": parameters.LANG_TA
        }

        # Send request
        print(f"        Accessing location/search API with searchQuery={keyword} ...")
        response = requests.get(url, params=param)

        # Parse response in JSON format
        data = response.json().get("data")  # Array
        locations += data

    # Remove duplicate search results
    seen = set()
    new_array = []
    for item in locations:
        # print(item)
        id_str = item.get("location_id")
        if id_str is not None:
            location_id = int(id_str)
            if location_id not in seen:
                seen.add(location_id)
                new_array.append(item)
    locations = new_array

    # Save the list of locations to a file
    with open(parameters.run_dir + "3.locations.json", "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=4)
    print(f'    Store location list to "{parameters.run_dir}3.locations.json"')

    # Retrieve detailed information for each location
    for loc in locations:
        location_id = loc.get("location_id")
        if location_id is not None:
            name = loc.get("name", "none")
            url2 = f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details"
            params = {
                "key": api_key,
                "language": parameters.LANG_TA
            }
            print(f'        Accessing location/details API for "{name}" ...')
            response = requests.get(url2, params=params)
            data2 = response.json()  # Dictionary data
            # print(data2)
            locationDetails.append(data2)
            # print(locationDetails)
            # sys.exit(0)
            # print(json.dumps(data2, indent=4, ensure_ascii=False))
        else:
            print("Could not retrieve information for the tourist attraction.")

    # If the same location appears multiple times in the locationDetails array, keep only one
    seen = set()
    new_array = []
    for item in locationDetails:
        # print(item)
        id_str = item.get("location_id")
        if id_str is not None:
            location_id = int(id_str)
            if location_id not in seen:
                seen.add(location_id)
                new_array.append(item)
    locationDetails = new_array

    with open(parameters.run_dir + "4.locationDetails.json", "w", encoding="utf-8") as f:
        json.dump(locationDetails, f, ensure_ascii=False, indent=4)
    print(f'    Store location detailed information to "{parameters.run_dir}4.locationDetails.json"')

if __name__ == '__main__':
    searchLocations()
