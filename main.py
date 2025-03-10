import json
import parameters
import os
from generateTripadvisorParams import generateTripadvisorParams
from searchLocations import searchLocations
from evaluateLocations import evaluateLocations
from assignLocationsToDays import assignLocationsToDays
from createTransportationInfo import createTransportationInfo
from createItinerary import createItinerary
from printItinerary import printItinerary

if __name__ == '__main__':
    # Create the execution directory if it does not exist
    if not os.path.exists( parameters.run_dir ):
        os.makedirs( parameters.run_dir )

    # Use OpenAI to generate parameters for searching TripAdvisor API
    generateTripadvisorParams()

    # Retrieve location information from TripAdvisor API
    searchLocations()

    # Use OpenAI to evaluate and score locations
    evaluateLocations()

    # Assign locations to travel itinerary using clustering process
    dailyLocations = assignLocationsToDays()

    # Retrieve transportation route information between locations for each travel day from Ekispert API
    matrix = createTransportationInfo(dailyLocations)

    # Determine the order of visiting locations for each travel day
    itinerary = createItinerary( matrix )

    # Output the travel itinerary information (needs to be modified to output more details)
    printItinerary( itinerary )
