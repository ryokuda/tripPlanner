# Traveler's requirements
user_requirement = """
I would like to plan a trip within Miyagi Prefecture, You are an excellent travel advisor.
The traveler has the following requests:
I would like to plan a trip within Miyagi Prefecture, centered around Sendai.
- I am interested in Japan's old buildings and culture, and I would like to visit museums or facilities where I can see them.
- If there are any places related to Date Masamune or Yuzuru Hanyu, I would like to visit them.
- I would like to see scenic natural landscapes.
- If there are old townscapes, I would like to take a walk around them.
- If there are dishes that can only be enjoyed in Sendai, I would like to try them.
- I would like to taste Sendai's local sake.
- I will be staying in Sendai for three nights.
- On the first day, I will arrive at Sendai Station by Shinkansen around noon, and on the last day, I will take the Shinkansen from Sendai Station around noon.
"""

# Number of days in the itinerary
NUM_DAYS = 2

# Directory to store execution results
run_dir="./runs/run001/"

# Radius of the circle indicating the geographical range of locations visited in a day (unit: km)
DISTANCE_TH = 15.0

# Maximum number of locations to visit in a day
TIME_TH = 5

# Language for displaying results
LANG = "Japanese"   # Used for OpenAI
LANG_TA = "ja"      # Used for TripAdvisor, en/ja/...
