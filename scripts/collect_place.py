import argparse
import json
import os
import pathlib

from dotenv import load_dotenv

from utils import places


def collect_place(text_query: str, outfile: pathlib.Path, replace: bool = False):
    client = places.PlacesClient(os.environ["GOOGLE_MAPS_API_KEY"])

    # Search for place
    fields = [*places.PLACE_DETAILS_ESSENTIALS, *places.PLACE_DETAILS_PRO]
    resp = client.search_text(text_query, fields)
    if resp.is_error:
        print(resp.status_code, resp.content)
        return

    resp_payload = resp.json()
    results = resp_payload["places"]
    assert isinstance(results, list), "expected list"

    result_idx = 0
    if len(results) == 0:
        print("no results found")
        return

    elif len(results) > 1:
        print("More than one result found:")
        for idx, result in enumerate(results):
            display_name = result["displayName"]["text"]
            address = result["formattedAddress"]
            print("\t", f"[{idx}]", display_name, " - ", address)

        chosen_idx = input("Choose result: ")
        if not chosen_idx:
            return
        
        try:
            chosen_idx = int(chosen_idx)
        except (TypeError, ValueError):
            print("invalid choice")
            return
        
        if chosen_idx >= len(results):
            print("invalid choice")
            return

        result_idx = chosen_idx        

    # Get place data
    place_id = results[result_idx]["id"]
    fields = [
        *places.PLACE_DETAILS_ESSENTIALS,
        *places.PLACE_DETAILS_PRO,
        *places.PLACE_DETAILS_ENTERPRISE
    ]
    resp = client.place_details(place_id, fields)
    if resp.is_error:
        print(resp.status_code, resp.content)
        return
    
    place = resp.json()
    display_name = place["displayName"]["text"]
    address = place["formattedAddress"]
    print(display_name, " - ", address)

    # load json data
    raw_text = outfile.read_text()
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        data = {}

    assert isinstance(data, dict), "expected dict"

    if place["id"] not in data or replace is True:
        data[place["id"]] = place
    else:
        current_data = data[place["id"]]
        assert isinstance(current_data, dict), "expected dict"
        current_data.update(place)
    
    outfile.write_text(json.dumps(data, separators=(',', ':')))


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Search for pizza & bagel shop data via Google Places API"
    )

    # Positional argument
    parser.add_argument("query", help="Text query for the place")
    parser.add_argument("--output", "-o", default="./data/places.json", help="Path to save output JSON file")
    parser.add_argument("--replace", action='store_true', help="Overwrite existing entry for the place if it already exists")
    args = parser.parse_args()

    path = pathlib.Path(args.output)
    if not path.exists or not path.is_file:
        raise parser.error("invalid output file")

    collect_place(args.query, path, args.replace)
