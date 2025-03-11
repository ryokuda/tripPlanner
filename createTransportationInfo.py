import requests
import json
from environs import Env
import parameters
import sys


def getLatLongValue(location):
    #print( dailyLocations )
    days = [[item.get("latLong") for item in day] for day in dailyLocations]
    #print( days )

    # days is an array of latLong strings like the following:
    # days =  [
    #  [
    #    "38.31718,140.89276", # Ice Rink Sendai
    #    "38.251724,140.8664", # Zuihoden Mausoleum
    #    "38.25714,140.85695", # Goshikinuma
    #    "38.260296,140.88223", # Sendai Tourist Information Center
    #    "38.318996,140.87993", # Nanakita Park
    #  ],
    #   "38.26058,140.88133",  # Sendai Station
    #   "38.263847,140.85512",  # Miyagi Museum of Art
    #   "38.258537,140.87238",  # Poke Lids Miyagi/Senda
    #   "38.26869,140.87222",  # Miyagi Tourism Information Center
    #  [
    #  ],
    # ]

    return days


def accessEkispertAPI(FROM, TO):
    # Ekispert API endpoint
    API_URL = "https://api.ekispert.jp/v1/json/search/course/plain"  # Route search with average waiting time

    env = Env()
    env.read_env()
    API_KEY = env.str("EKISPERT_API_KEY", "")

    # API request parameters
    #print( f"{FROM} -> {TO}" )
    #return FROM+TO

    params = {
        "key": API_KEY,
        "from": FROM,
        "to": TO,
    }

    # API request
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        # Save results to a new JSON file
        #with open(output_file, "w", encoding="utf-8") as f:
        #    json.dump(data, f, indent=4, ensure_ascii=False)

        # Display results
        if "ResultSet" in data and "Course" in data["ResultSet"]:
            courses = data["ResultSet"]["Course"]
            course = courses[0] if isinstance(courses, list) else courses
            route = course["Route"]
            #time = (int(route["timeOther"]) if "timeOther" in route else 0) + \
            time = (int(route["timeOnBoard"]) if "timeOnBoard" in route else 0) + \
                   (int(route["timeWalk"]) if "timeWalk" in route else 0)
            #print(f"  Travel time: {time} min")
            return time, route
        else:
            print(f"{FROM}->{TO} Route not found.")
            return -1, None
    else:
        print(f"{FROM}->{TO} Error: {response.status_code}")
        return -1, None


def createTransportationInfo(dailyLocations):
    print("")
    print("------ Step 5: Check transportation info with Ekispert API ------")

    transportationInfo = []

    # print(days)
    print("    Checking all possible routes with Ekispert API ...")
    matrix = {"locations": [], "timeMatrix": []}
    for day in dailyLocations:
        n = len(day)
        timeMatrix = [[0] * n for _ in range(n)]
        isDirty = [True] * n
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # Get travel routes using Ekispert API
                print(f'       Checking route from "{day[i].get("name")}" -> "{day[j].get("name")}"')
                #print( f'{day[i].get("latLong")}-{day[j].get("latLong")}')
                time, route = accessEkispertAPI(day[i].get("latLong"), day[j].get("latLong"))
                timeMatrix[i][j] = time
                if time >= 0:
                    # Successfully retrieved route data
                    isDirty[i] = False
                    isDirty[j] = False
                    transportationInfo.append({
                        "from": day[i],
                        "to": day[j],
                        "route": route
                    })
        #print( transportationInfo )
        #print( timeMatrix )

        new_day = day
        for i in range(n - 1, -1, -1):
            if isDirty[i]:
                # Remove locations where route data retrieval failed
                timeMatrix = [row[:i] + row[i + 1:] for row in timeMatrix]
                timeMatrix.pop(i)
                new_day.pop(i)
        #print( timeMatrix )
        #print( new_day )
        matrix["locations"].append(new_day)
        matrix["timeMatrix"].append(timeMatrix)

    with open(parameters.run_dir + "7.transportationInfo.json", "w", encoding="utf-8") as f:
        json.dump(transportationInfo, f, indent=4, ensure_ascii=False)
    print(f'    Store transportation info to "{parameters.run_dir}7.transportationInfo.json"')

    return matrix


if __name__ == '__main__':
    with open(parameters.run_dir + "6.dailyLocations.json", "r", encoding="utf-8") as f:
        dailyLocations = json.load(f)

    matrix = createTransportationInfo(dailyLocations)
    with open(parameters.run_dir + "8.timeMatrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=4, ensure_ascii=False)
    #print(matrix)
