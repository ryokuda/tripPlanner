import json
from openai import OpenAI
from environs import Env
import re
import sys

import parameters


def generateTripadvisorParams():
    print("")
    print("------ Step 1: Use OpenAI to generate TripAdvisor search parameters based on user requests  ------")

    env = Env()
    env.read_env()  # Load OPENAI_API_KEY as an environment variable

    # Retrieve the user's request document from parameters.py
    req = parameters.user_requirement

    # Save the request document to an execution file
    with open(parameters.run_dir + "1.user_requirement.txt", "w", encoding="utf-8") as f:
        f.write(req)

    # Create the prompt text
    prompt_text = f"""
    You are an excellent travel advisor. The traveler has the following requests: 
    ---
    {req}
    ---
    I want to search for candidate locations to visit using Tripadvisor's API:
    API) Location Search: [https://api.content.tripadvisor.com/api/v1/location/search](https://api.content.tripadvisor.com/api/v1/location/search)  
    Those locations may contain attractions, hotels, restaurants, shops.
    I want to enumerate appropriate candidates to match the traveler's requests.

    For the search, I will use the following parameters:  
    {{
      'searchQuery': "search string",
      "latLong": "latitude_value,longitude_value",
      "category": category
    }}

    Please let me know appropriate parameters for up to 10 times searches.  
    The searchQuery string must be in {parameters.LANG}.
    The category string can be one of the following: "hotels", "attractions", "restaurants", or "geos" (geographical areas).
    Provide just a list of parameter values in JSON format to match the traveler’s preferences
    without any extra message.
    """

    # Call ChatGPT-4o API
    client = OpenAI()
    print(f"Asking OpenAI to generate search parameters for TripAdvisor API ... ", end="")
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7,
        max_tokens=1000
    )
    print("done.")

    content_json_str = completion.choices[0].message.model_dump().get("content", "{}")
    content_json_str = re.sub(r"^```json\n|\n```$", "", content_json_str.strip())
    result = json.loads(content_json_str)

    with open(parameters.run_dir + "2.tripadvisorAccessParams.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f'    Store generated search parameters to the file "{parameters.run_dir}2.tripadvisorAccessParams.json"')

    return result


if __name__ == '__main__':
    result = generateTripadvisorParams()
    print(json.dumps(result, indent=4, ensure_ascii=False))
