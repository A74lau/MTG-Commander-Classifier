import time
import csv
import requests
from unidecode import unidecode

def convert_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

# csv file creation
scryfall_csv_file = "all_together_output.csv"
card_info_columns = ["Name", "Type", "CMC", "Color Identity", "Oracle Text", "Keywords", "Power", "Toughness", "theme_label"]

edhrec_csv_file = "commander_cards_w_tag.csv"
tag_info_columns = ["Name", "Tag", "Num Decks"]

non_matches_file = "non_matching_commander_cards.csv"
non_matching_columns = ["Name", "Type", "CMC", "Color Identity", "Oracle Text", "Keywords", "Power", "Toughness"]

# open file/create if not existing
with open(scryfall_csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=card_info_columns)
    writer.writeheader()

with open(edhrec_csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=tag_info_columns)
    writer.writeheader()

with open(non_matches_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=non_matching_columns)
    writer.writeheader()

# START OF EDHREC FETCH #

# EDHREC URL for API requests (may need to change?)
url_base = "https://json.edhrec.com/pages/tags.json"

# get tag URL data
response = requests.get(url_base)
if response.status_code != 200:
    print(f"Failed to fetch data: {response.status_code} - {response.text}")
else:
    print(f"Fetched tag data")

try:
    data = response.json()
except ValueError as e:
    print(f"Failed to decode JSON: {str(e)} - {response.text}")

# list of tags
tag_urls = []
tag_data = data['container']['json_dict']['cardlists'][0]['cardviews']
for tag in tag_data:
    tag_urls.append(tag['url'])

# edhrec requests a delay so we dont get IP banned of around 200-500 ms
time.sleep(0.400) # 400 ms delay

print(tag_urls)
print("Completed tag fetching")

# create a dict of commanders -> (top tag, num_decks)
commanders = {}
tag_url_idx = 0

while True:

    tag_short_url = tag_urls[tag_url_idx]
    tag_url = "https://json.edhrec.com/pages" + str(tag_short_url) + ".json"
    tag_url_idx += 1

    # reached the end of the list
    if (tag_url_idx == len(tag_urls)):
        break

    print(f"Fetching from {tag_url}...")

    response = requests.get(tag_url)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")
        break
    else:
        print(f"Fetched data from {tag_url}")

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to decode JSON: {str(e)} - {response.text}")
        break

    # get name of tag
    tag_name = data['container']['breadcrumb'][1][tag_short_url]
    print(f"Parsing commander data for tag {tag_name}...")

    # get commander data, i.e., names of all commanders under this tag
    commander_data = data['container']['json_dict']['cardlists'][0]['cardviews']
    for commander in commander_data:
        name = str(commander['name'])
        new_num_decks = commander['num_decks']
        # Check if there is an existing entry with a higher num_decks
        if name in commanders.keys():
            curr_num_decks = commanders[name][1]
            # Overwrite the existing if the num_decks value is higher
            if (new_num_decks > curr_num_decks):
                print(f"Overwriting {name}'s old num_decks of {commanders[name][0]},{curr_num_decks} with {tag_name}, {new_num_decks}")
                commanders[name] = (tag_name, new_num_decks)
        # Simply add the new commander if not
        else:
            commanders[name] = (tag_name, new_num_decks)

    # edhrec requests a delay so we dont get IP banned of around 200-500 ms
    time.sleep(0.400) # 400 ms delay

# Write the commanders to CSV for now
with open(edhrec_csv_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=tag_info_columns)
    for commander in commanders.keys():
        new_row = {
            "Name": commander,
            "Tag": commanders[commander][0],
            "Num Decks": commanders[commander][1]
        }
        writer.writerow(new_row)

# END OF EDHREC FETCH

# START OF SCRYFALL FETCH + CSV WRITING #

# scryfall URL for API requests (may need to change?)
url_base = "https://api.scryfall.com/cards/search"
# parameters for search on scryfall
search_params = {
    "q": "is:commander",
    "order": "name",
    "page": 1,
}

while True:
    response = requests.get(url_base, params=search_params)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")
        break

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to decode JSON: {str(e)} - {response.text}")
        break

    for card in data['data']:
        type_parts = card["type_line"].split(' — ') # remove Legendary Creature -
        relevant_type = type_parts[1] if len(type_parts) > 1 else "No Subtype"
        normalized_name = unidecode(card["name"])

        tag = ""
        # get tag from tag database
        if card["name"] in commanders.keys():
            tag = commanders[card["name"]][0]

            card_info = {
                "Name": normalized_name,
                "Type": relevant_type,
                "CMC": card["cmc"],
                "Color Identity": ", ".join(card["color_identity"]) if card["color_identity"] else "No Color Identity",
                "Oracle Text": card.get("oracle_text", "Missing Oracle Text").replace('\n', ''),
                "Keywords": ", ".join(card.get("keywords", [])),
                "Power": convert_to_int(card.get("power", 0)),
                "Toughness": convert_to_int(card.get("toughness", 0)),
                "theme_label": tag,
            }

            # now write it to csv
            with open(scryfall_csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=card_info_columns)
                writer.writerow(card_info)

        else:
            # add to the no_match file
            card_info = {
                "Name": normalized_name,
                "Type": relevant_type,
                "CMC": card["cmc"],
                "Color Identity": ", ".join(card["color_identity"]) if card["color_identity"] else "No Color Identity",
                "Oracle Text": card.get("oracle_text", "Missing Oracle Text").replace('\n', ''),
                "Keywords": ", ".join(card.get("keywords", [])),
                "Power": convert_to_int(card.get("power", 0)),
                "Toughness": convert_to_int(card.get("toughness", 0)),
            }

            # now write it to csv
            with open(non_matches_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=non_matching_columns)
                writer.writerow(card_info)

    # scryfall requests a delay so we dont get IP banned of around 50-100 ms
    time.sleep(0.075) # 75 ms delay

    # iterate to the next page
    if "next_page" in data:
        search_params["page"] += 1
    else:
        break
print("Completed commander card fetching")
