from itertools import permutations
import json
import parameters
import sys

def createItinerary(matrix):
    print("")
    print("------ Step 6: Finding shortest routes ------")
    dailyLocations = matrix.get("locations")
    timeMatrix = matrix.get("timeMatrix")
    #print( timeMatrix)
    # Time matrix, representing the travel time (minutes) required to move between two points
    # timeMatrix = [
    #  [  Day 1
    #       [0, 45, 54, 49],
    #       [37, 0, 81, 54],
    #       [54, 86, 0, 90],
    #       [45, 82, 86, 0],
    #  ],
    #  [  Day 2
    #       [0, 13, 11, 92, 82],
    #       [13, 0, 14, 95, 85],
    #       [11, 14, 0, 93, 83],
    #       [92, 95, 93, 0, 50],
    #       [88, 91, 89, 56, 0]
    # ]

    routes = []
    for mat in timeMatrix:
        # Number of locations
        n = len(mat)

        # Find the shortest route for each starting point
        for start in range(n):
            min_path = None
            min_time = float('inf')

            # Fix the starting point and explore all possible orders of visiting other locations
            nodes = list(range(n))
            nodes.remove(start)  # Create a list excluding the starting location

            for perm in permutations(nodes):  # Iterate over all possible visiting orders
                route = [start] + list(perm)  # Create a route starting from the fixed location
                total_time = sum(mat[route[i]][route[i+1]] for i in range(n-1))

                if total_time < min_time:
                    min_time = total_time
                    min_path = route

        # Display the optimal solution
        print(f"    Start at {start}: Shortest route = {min_path}, transportation time = {min_time}")
        routes.append(route)

    itinerary = []
    for d in range(len(dailyLocations)):
        locs = dailyLocations[d]
        route = routes[d]
        mat = timeMatrix[d]
        location_list = [locs[i] for i in route]
        transport_time_list = [(mat[route[i]][route[i+1]] if i < len(route)-1 else 0) for i in range(len(route))]
        item = {
            "locations": location_list,
            "transport_time": transport_time_list
        }
        #print( item )
        itinerary.append(item)

    #print( itinerary)
    with open(parameters.run_dir + "9.dailyItinerary.json", "w", encoding="utf-8") as f:
        json.dump(itinerary, f, indent=4, ensure_ascii=False)

    return itinerary

if __name__ == "__main__":
    with open(parameters.run_dir+"8.timeMatrix.json", "r", encoding="utf-8") as f:
        matrix = json.load(f)

    createItinerary(matrix)
