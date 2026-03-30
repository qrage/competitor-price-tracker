"""
Scraper module for collecting competitor product variant data.

Fetches Shopify collection data through the public products JSON endpoint
and prepares normalized product variant rows.
"""

import csv
import re
from datetime import datetime, UTC
from decimal import Decimal, InvalidOperation

import requests

from src.config import BASE_URL, COLLECTION_HANDLE, HEADERS, CSV_FILENAME


def normalize_price(raw_price) -> str:
    """Normalize raw Shopify price value into a stable string format."""
    if raw_price is None:
        return ""

    cleaned = re.sub(r"[^\d.,]", "", str(raw_price)).strip()
    if not cleaned:
        return ""

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            normalized = cleaned.replace(".", "").replace(",", ".")
        else:
            normalized = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        normalized = cleaned.replace(",", ".") if len(parts[-1]) in (1, 2) else cleaned.replace(",", "")
    else:
        normalized = cleaned

    try:
        value = Decimal(normalized)
        return format(value.normalize(), "f")
    except InvalidOperation:
        return cleaned


def scrape_collection_variants() -> list[dict]:
    """Scrape all product variants from the configured Shopify collection."""
    page = 1
    rows = []
    checked_at = datetime.now(UTC).isoformat()

    while True:
        url = f"{BASE_URL}/en/collections/{COLLECTION_HANDLE}/products.json?limit=250&page={page}"
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()

        products = response.json().get("products", [])
        if not products:
            break

        for product in products:
            product_title = product.get("title")
            product_url = f"{BASE_URL}/en/products/{product.get('handle')}"

            for variant in product.get("variants", []):
                rows.append({
                    "product_id": variant.get("id"),
                    "title": product_title,
                    "variant": None if variant.get("title") == "Default Title" else variant.get("title"),
                    "price": normalize_price(variant.get("price")),
                    "url": product_url,
                    "checked_at": checked_at,
                })

        print(f"Page {page}: {len(products)} products")
        page += 1

    unique = {}
    for row in rows:
        unique[row["product_id"]] = row

    return list(unique.values())


def save_to_csv(rows: list[dict], filename: str = CSV_FILENAME):
    """Save scraped product variant rows to a local CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["product_id", "title", "variant", "price", "url", "checked_at"],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = scrape_collection_variants()
    save_to_csv(rows)
    print(f"Saved {len(rows)} rows")