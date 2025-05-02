import html
#import pdb;pdb.set_trace()
import requests
import ast
import json
import os

# Ensure assets directory exists
if not os.path.exists("assets"):
    os.makedirs("assets")

map_urls = {
    'food': "https://maps.app.goo.gl/oXbFZXySWtKHLoRc9",
    'cafe': "https://maps.app.goo.gl/isNyH6KzxX8USSyb6",
    'drink': "https://maps.app.goo.gl/1XXRQA5HDzqZGDos9",
    #'sweet': "https://maps.app.goo.gl/i5un8KqV5LU22n2f8"
}

for category, map_url in map_urls.items():
    response = requests.get(url=map_url)

    # Unescape and extract the relevant HTML/text section
    html_text = html.unescape(
        response.text.split(r")]}'\n")[2].split("]]\"],")[0] + "]]"
    )
    # with open(f"assets/{category}-raw.txt", 'w', encoding='utf-8') as f:
    #     f.write(html_text)
    # Substrings to locate the data section
    data_start_marker = '[[null,[null,null'
    data_end_marker = ',[null,null,null,'

    # Find the indices for the data section
    data_start_index = html_text.find(data_start_marker)
    data_end_index = html_text.find(data_end_marker)

    # Extract and process the data section
    if data_start_index != -1 and data_end_index != -1:
        data_section = html_text[data_start_index:data_end_index].replace(r'\"', '"').replace('null', 'None')
    else:
        print(f"Target substring not found in html_text for {category}.")
        continue

    # Convert the string representation to a Python list
    places_raw_list = ast.literal_eval(data_section)

    # Build the place list with clear keys
    places_list = []
    for place in places_raw_list:
        # Replace \u0026 with & in name and address
        name = place[2].replace('\\u0026', '&')
        address = place[1][4].replace('\\u0026', '&')
        
        places_list.append({
            "name": name,
            "address": address,
            "latitude": place[1][5][2],
            "longitude": place[1][5][3]
        })

    # Save as valid JSON
    with open(f"assets/{category}.json", 'w', encoding='utf-8') as json_file:
        json.dump(places_list, json_file, ensure_ascii=False, indent=2)



