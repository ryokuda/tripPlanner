import json
import parameters

def printItinerary( itinerary ):
    print('')
    print( '###########  Suggested Itinerary ############')
    for i, oneDay in enumerate( itinerary ):
        print('')
        print( f'Day {i+1}:')
        num_locations = len(oneDay.get("locations"))
        for j in range(num_locations):
            print( f"  {oneDay.get('locations')[j].get('name')}")
            if j < num_locations-1:
                print( f"      {oneDay.get('transport_time')[j]} minutes's transportation")


if __name__ == '__main__':
    with open(parameters.run_dir + "9.dailyItinerary.json", "r", encoding="utf-8") as f:
        itinerary = json.load(f)
        printItinerary(itinerary)
