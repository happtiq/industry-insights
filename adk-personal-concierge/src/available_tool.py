import json
import os
from typing import Dict, List, Optional

from google.adk.tools.tool_context import ToolContext

BASE_DIR = os.path.dirname(__file__)
STORE_PATH = os.path.join(BASE_DIR, "..", "data", "store.json")

with open(STORE_PATH, "r", encoding="utf-8") as fh:
    _store_payload = json.load(fh)

_SHOPS: List[dict] = _store_payload.get("shops", [])
_STATUS_LEGEND: Dict[str, str] = _store_payload.get("status_legend", {})


def _format_availability_entry(shop: dict, inventory_entry: dict) -> dict:
    status = inventory_entry.get("status", "unknown")
    legend = _STATUS_LEGEND.get(status)
    return {
        "shop_id": shop.get("shop_id"),
        "shop_name": shop.get("name"),
        "city": shop.get("location", {}).get("city"),
        "country": shop.get("location", {}).get("country"),
        "status": status,
        "status_label": legend or status.replace("_", " ").title(),
        "quantity": inventory_entry.get("quantity"),
        "viewing_available": inventory_entry.get("viewing_available"),
        "reservation_supported": inventory_entry.get("reservation_supported"),
        "transfer_eta_days": inventory_entry.get("transfer_eta_days"),
        "last_updated": inventory_entry.get("last_updated"),
        "contact": shop.get("contact"),
        "capabilities": shop.get("capabilities"),
        "opening_hours": shop.get("opening_hours"),
    }


async def check_product_availability(
    product_id: str,
    shop_id: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> List[dict]:
    """Return boutique availability for a Cartier product.

    Args:
        product_id: The Cartier SKU (for example "CRWSPN0015").
        shop_id: Optional boutique identifier to narrow the search.
        tool_context: Unused; present for signature compatibility with ADK.

    Returns:
        A list of availability entries, one per boutique that stocks the product.
        Each entry contains the boutique metadata, current status, and service capabilities.
    """
    matches: List[dict] = []
    for shop in _SHOPS:
        if shop_id and shop.get("shop_id") != shop_id:
            continue
        for inventory_entry in shop.get("inventory", []):
            if inventory_entry.get("product_id") == product_id:
                matches.append(_format_availability_entry(shop, inventory_entry))
                break

    return matches
