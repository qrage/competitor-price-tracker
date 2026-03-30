"""
Application configuration for the competitor price tracker.

Contains scraping settings, request headers, spreadsheet settings,
and local export configuration.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://danalor9carati.com"
COLLECTION_HANDLE = "collane"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVICE_ACCOUNT_FILE = "service_account.json"

CURRENT_SHEET = "current_data"
HISTORY_SHEET = "price_history"

CSV_FILENAME = "necklaces_variants.csv"