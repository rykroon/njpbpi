import argparse
import json
import os
import pathlib

from dotenv import load_dotenv

from utils import places


def collect_place(text_query: str, outfile: pathlib.Path):
    client = places.PlacesClient(os.environ["GOOGLE_MAPS_API_KEY"])

    fields = [*places.PLACE_DETAILS_ESSENTIALS, *places.PLACE_DETAILS_PRO]
    resp = client.search_text(text_query, fields)
    if resp.is_error:
        print(resp.status_code, resp.content)
        return

    resp_payload = resp.json()
    results = resp_payload["places"]
    if len(results) == 0:
        print("no results found")
        return

    elif len(results) > 1:
        print("More than one result found.")
        for result in results:
            display_name = result["displayName"]["text"]
            address = result["formattedAddress"]
            print(display_name, address)

        return

    place_id = results[0]["id"]

    resp = client.place_details(place_id, places.ALL_FIELDS)
    if resp.is_error:
        print(resp.status_code, resp.content)
        return
    
    place = resp.json()
    print(place["displayName"]["text"])
    print(place["formattedAddress"])

    raw_text = outfile.read_text()
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        data = {}

    data[place["id"]] = place
    outfile.write_text(json.dumps(data))


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Search for pizza & bagel shop data via Google Places API"
    )

    # Positional argument
    parser.add_argument("query", help="Text query for the place")
    parser.add_argument("--output", "-o", default="./data/places.json", help="Path to save output JSON file")
    args = parser.parse_args()


    path = pathlib.Path(args.output)
    if not path.exists or not path.is_file:
        raise parser.error("invalid output file")

    collect_place(args.query, path)
