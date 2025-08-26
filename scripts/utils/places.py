from dataclasses import dataclass, field
from typing import Sequence
import httpx


TYPES = ("pizza_restaurant", "italian_restaurant", "bagel_shop")


PLACE_DETAILS_ESSENTIALS = (
    "id",
    "addressComponents",
    "formattedAddress",
    "location",
    "shortFormattedAddress",
    "types",
)

PLACE_DETAILS_PRO = (
    "accessibilityOptions",
    "displayName",
    "primaryType",
)

PLACE_DETAILS_ENTERPRISE = (
    "priceLevel",
    "priceRange",
    "rating",
    "userRatingCount",
    "websiteUri",
)

PLACE_DETAILS_ENTERPRISE_ATMOSPHERE = (
    "allowsDogs",
    "curbsidePickup",
    "delivery",
    "dineIn",
    "goodForChildren",
    "goodForGroups",
    "goodForWatchingSports",
    "liveMusic",
    "menuForChildren",
    "parkingOptions",
    "paymentOptions",
    "outdoorSeating",
    "reservable",
    "restroom",
    "servesBeer",
    "servesBreakfast",
    "servesBrunch",
    "servesCocktails",
    "servesCoffee",
    "servesDessert",
    "servesDinner",
    "servesLunch",
    "servesVegetarianFood",
    "servesWine",
    "takeout",
)


ALL_FIELDS = (
    *PLACE_DETAILS_ESSENTIALS,
    *PLACE_DETAILS_PRO,
    *PLACE_DETAILS_ENTERPRISE,
    *PLACE_DETAILS_ENTERPRISE_ATMOSPHERE
)


@dataclass(frozen=True)
class PlacesClient:
    api_key: str = field(repr=False)
    
    def _build_headers(self, field_mask: Sequence[str]) -> dict[str, str]:
        return {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": ",".join(field_mask)
        }

    def search_text(
        self,
        text_query: str,
        field_mask: Sequence[str],
        included_type: str | None = None,
    ):
        # prepend "places." to fields.
        field_mask = [f"places.{f}" for f in field_mask]

        payload = {"textQuery": text_query}
        if included_type is not None:
            payload["includedType"] = included_type

        return httpx.post(
            url="https://places.googleapis.com/v1/places:searchText",
            headers=self._build_headers(field_mask),
            json=payload
        )

    def place_details(self, place_id: str, field_mask: Sequence[str]):
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        return httpx.get(
            url=url,
            headers=self._build_headers(field_mask),
        )
