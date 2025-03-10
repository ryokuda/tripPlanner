# Traveler's requirements
user_requirement = """
東京都を訪問したい
日本のアニメが大好きです。スタジオジブリ、ドラゴンボール、ワンピース、ナルト、ポケットモンスターなど
アニメに関係するattractionに行きたい。
"""

# Number of days in the itinerary
NUM_DAYS = 3

# Directory to store execution results
run_dir="./runs/run002/"

# Radius of the circle indicating the geographical range of locations visited in a day (unit: km)
DISTANCE_TH = 20.0

# Maximum number of locations to visit in a day
TIME_TH = 6

# Language for displaying results
LANG = "Japanese"   # Used for OpenAI
LANG_TA = "ja"      # Used for TripAdvisor, en/ja/...
