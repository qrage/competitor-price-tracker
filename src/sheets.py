"""
Google Sheets synchronization helpers for the competitor price tracker.

This module loads current product data, compares scraped prices,
updates changed records, and appends price history rows.
"""

import re
from datetime import datetime, UTC

import gspread

from src.config import (
    SPREADSHEET_ID,
    SERVICE_ACCOUNT_FILE,
    CURRENT_SHEET,
    HISTORY_SHEET,
)


def get_sheets():
    """Return the current-data and history worksheets."""
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.worksheet(CURRENT_SHEET), sh.worksheet(HISTORY_SHEET)


def load_current_data(current_ws):
    """Load current worksheet rows into dictionaries for fast comparison."""
    values = current_ws.get_all_values()
    existing = {}
    row_map = {}

    for row_index, row in enumerate(values[1:], start=2):
        if not row:
            continue

        row = row + [""] * (6 - len(row))
        product_id = row[0].strip()

        if not product_id:
            continue

        existing[product_id] = {
            "product_id": row[0],
            "title": row[1],
            "variant": row[2],
            "price": row[3],
            "url": row[4],
            "updated_at": row[5],
        }
        row_map[product_id] = row_index

    return existing, row_map


def sync_products(parsed_data: list[dict]):
    """Sync scraped products with Google Sheets and log price changes."""
    current_ws, history_ws = get_sheets()
    existing, row_map = load_current_data(current_ws)
    now = datetime.now(UTC).isoformat()

    new_rows = []
    current_updates = []
    history_rows = []

    total_products = len(parsed_data)
    new_count = 0
    updated_count = 0
    price_drop_count = 0

    for product in parsed_data:
        product_id = str(product["product_id"]).strip()
        title = str(product["title"]).strip()
        variant = "" if product["variant"] is None else str(product["variant"]).strip()
        price = str(product["price"]).strip()
        url = str(product["url"]).strip()

        if product_id not in existing:
            new_rows.append([product_id, title, variant, price, url, now])
            new_count += 1
            continue

        old_price = existing[product_id]["price"]

        if price != old_price:
            row_num = row_map[product_id]

            current_updates.append({
                "range": f"A{row_num}:F{row_num}",
                "values": [[product_id, title, variant, price, url, now]],
            })

            history_rows.append([product_id, old_price, price, now])
            updated_count += 1

            old_num = to_number(old_price)
            new_num = to_number(price)

            suffix = ""
            if old_num is not None and new_num is not None:
                if new_num < old_num:
                    suffix = " 🔥 PRICE DROP"
                    price_drop_count += 1
                elif new_num > old_num:
                    suffix = " ⬆ PRICE UP"

            print("Price changed:")
            print(f"{title} ({variant or 'default'})")
            print(f"{old_price} → {price}{suffix}")

    if new_rows:
        current_ws.append_rows(
            new_rows,
            value_input_option="USER_ENTERED",
            table_range="A:F",
        )

    if current_updates:
        current_ws.batch_update(
            current_updates,
            value_input_option="USER_ENTERED",
        )

    if history_rows:
        history_ws.append_rows(
            history_rows,
            value_input_option="USER_ENTERED",
            table_range="A:D",
        )

    print("\nRun summary:")
    print(f"- Total products: {total_products}")
    print(f"- New: {new_count}")
    print(f"- Updated: {updated_count}")
    print(f"- Price drops: {price_drop_count}")


def to_number(price: str) -> float | None:
    """Convert a formatted price string to float for comparison."""
    if not price:
        return None

    cleaned = re.sub(r"[^\d,\.]", "", str(price)).strip()

    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return None