import argparse
import os

from ..utils import places


def main():
    parser = argparse.ArgumentParser(
        description="Search for pizza & bagel shop data via Google Places API"
    )

    # Positional argument
    parser.add_argument("text", help="Name of the shop to look up")
    args = parser.parse_args()
    
    client = places.PlacesClient(os.getenv("GOOGLE_MAPS_API_KEY"))

    fields = [*places.PLACE_DETAILS_ESSENTIALS, *places.PLACE_DETAILS_PRO]
    resp = client.search_text(args.text, fields)
    if resp.is_error:
        print("Search text failed")
        return
    
    resp_payload = resp.json()
    results = resp_payload["places"]
    if len(results) == 0:
        print("no results found")
        return

    elif len(results) > 1:
        print("more than one result found")
        return
    
    place = results[0]
    place_id = place["id"]
    display_name = place["displayName"]["text"]
    print(display_name)

    resp = client.place_details(place_id, places.ALL_FIELDS)
    if resp.is_error:
        print("failed to get place details")
        return
    
    resp_payload = resp.json()
    # store result in data.

if __name__ == "__main__":
    main()