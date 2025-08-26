import argparse
from io import FileIO
import json
import os
import pathlib


from dotenv import load_dotenv

from utils import places


def main(text: str, outfile: pathlib.Path | None):
    client = places.PlacesClient(os.environ["GOOGLE_MAPS_API_KEY"])

    fields = [*places.PLACE_DETAILS_ESSENTIALS, *places.PLACE_DETAILS_PRO]
    resp = client.search_text(text, fields)
    if resp.is_error:
        print(resp.status_code, resp.content)
        return
    
    resp_payload = resp.json()
    results = resp_payload["places"]
    if len(results) == 0:
        print("no results found")
        return

    elif len(results) > 1:
        print("more than one result found")
        return

    place_id = results[0]["id"]

    resp = client.place_details(place_id, places.ALL_FIELDS)
    if resp.is_error:
        print(resp.status_code, resp.content)
        return
    
    place = resp.json()
    print(place["displayName"]["text"])
    print(place["formattedAddress"])
    if outfile is not None:
        data = json.loads(outfile.read_text())
        data[place["id"]] = place
        outfile.write_text(json.dumps(data, indent=1))
   
    # store result in data.

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Search for pizza & bagel shop data via Google Places API"
    )

    # Positional argument
    parser.add_argument("text", help="Name of the shop to look up")
    parser.add_argument("--outfile", "-o", help="output file")
    args = parser.parse_args()
    print(args)

    p = None
    if args.outfile is not None:
        p = pathlib.Path(args.outfile)
        if not p.exists or not p.is_file:
            raise parser.error("invalid outfile")

    main(args.text, p)
