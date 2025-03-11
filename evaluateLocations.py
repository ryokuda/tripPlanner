import json
from openai import OpenAI
from environs import Env
import sys
import re

import parameters


def extract_location_details():
    # Load JSON file
    file_path = parameters.run_dir + "4.locationDetails.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load JSON data as a list of dictionaries

    print(f'    Load location detailed information from "{parameters.run_dir}4.locationDetails.json"')

    locations = []

    for item in data:
        # Check if all required keys exist
        if all(key in item for key in ["location_id", "name", "latitude", "longitude"]):
            locations.append({
                "location_id": item["location_id"],
                "name": item["name"],
                "website": item.get("website", ""),  # Use an empty string if not available
                "description": item.get("description", ""),  # Use an empty string if not available
            })

    return locations


def create_prompt_text(subLocations):
    # Retrieve the user's request document from parameters.py
    req = parameters.user_requirement

    # Create prompt text
    prompt_text = f"""
    You are an excellent travel advisor. The traveler has the following requests: 

    --- requests ---
    {req}
    ----------------

    The description of the candidate destinations(locations) are described as follows in the JSON format,

    --- JSON(description of the locations) ---
    {subLocations}
    ------------------------------------

    Evaluate those locations individually how well each location fits the traveler's preferences and assign a score between 0 and 100.  
    If the location is recommended, assign a score greater than 50; if it is not recommended, assign a score less than 50.  
    For the evaluation, do not rely solely on the location's name and description, also check the website and gather necessary information.  

    Output the results as an array of JSON objects with the following structure for each location:  

    {{
        "location_id": 'location_id' value in the "JSON(description of the locations)",
        "name": 'name' value in the "JSON(description of the locations)",
        "score": <assigned score by the evaluation, 0 to 100 value, how well this location fits the traveler's preferences>,
        "advice": <brief advice to the traveler how to enjoy the location>
    }}

    Make sure that all the locations in "JSON(description of the locations)" must be evaluated and appear in the JSON output.
    Create all the sentences in the output in {parameters.LANG}.
    Do not output any text other than JSON.
    """
    return prompt_text


def accessOpenAI(prompt_text):
    env = Env()
    env.read_env()  # Load OPENAI_API_KEY as an environment variable
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7,
        max_tokens=8192
    )

    content_json_str = completion.choices[0].message.model_dump().get("content", "{}")
    content_json_str = re.sub(r"^```json\n|\n```$", "", content_json_str.strip())
    result = json.loads(content_json_str)

    # Output response
    # print(result)
    return result


def evaluateLocations():
    print("")
    print("------ Step 3: Evaluate enumerated locations using OpenAI and put score to each location  ------")

    # Execute the function and obtain results
    locations = extract_location_details()
    total = len(locations)
    N = 20  # Maximum number of locations to be evaluated at once by ChatGPT

    scores = []
    for i in range(0, total, N):
        subset = locations[i:i + N]
        prompt_text = create_prompt_text(subset)

        print(f"    Asking OpenAI to evaluate locations No.{i + 1}-{i + len(subset)} ... ")
        # print( "Asking OpenAI to evaluation the following locations ...")
        print("        ", end="")
        for item in subset:
            print(f'"{item.get("name")}" ', end="")
        print("")
        result = accessOpenAI(prompt_text)
        print("done.")
        scores += result

    # Sort the array in descending order of the "score" value
    sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    with open(parameters.run_dir + "5.locationScores.json", "w", encoding="utf-8") as f:
        json.dump(sorted_scores, f, indent=4, ensure_ascii=False)
    print(f'    Store location score to "{parameters.run_dir}5.locationScores.json"')


if __name__ == '__main__':
    evaluateLocations()
