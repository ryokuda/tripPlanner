# Traveler's requirements
user_requirement = """
"I want to travel to Kyoto City and its surrounding areas, including nearby cities in Kyoto Prefecture such as Uji City.
I am interested in traditional Japanese culture, architecture, and events.
Additionally, I am also interested in beautiful landscapes
"""

# Number of days in the itinerary
NUM_DAYS = 3

# Directory to store execution results
run_dir="./runs/run003/"

# Radius of the circle indicating the geographical range of locations visited in a day (unit: km)
DISTANCE_TH = 20.0

# Maximum number of locations to visit in a day
TIME_TH = 6

# Language for displaying results
LANG = "English" # "Japanese"   # Used for OpenAI
LANG_TA = "en" # "ja"      # Used for TripAdvisor, en/ja/...
