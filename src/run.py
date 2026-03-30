"""
Main entry point for the competitor price tracker.

The script scrapes competitor product variants, compares current prices
with stored values in Google Sheets, and logs price changes over time.
"""

import os
from dotenv import load_dotenv

from src.scraper import scrape_collection_variants
from src.sheets import sync_products


load_dotenv()


def validate_env():
    """Validate required environment variables before application startup."""
    required_vars = ["SPREADSHEET_ID"]
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


def main():
    """Run the scraping and synchronization workflow."""
    validate_env()
    parsed_data = scrape_collection_variants()
    sync_products(parsed_data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")