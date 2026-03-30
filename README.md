# Competitor Price Tracker

## Problem
Companies that sell physical products need to monitor competitor pricing regularly, but manual checking is slow, repetitive, and unreliable.  
Without structured tracking, price drops and price increases can be missed, which weakens response speed in pricing and sales decisions.

## Solution
Competitor Price Tracker is a business-oriented monitoring solution that collects product variant prices from a competitor storefront, compares the latest values with previously stored data, and records all price changes in Google Sheets.

It is designed for market observation, competitor benchmarking, and lightweight pricing intelligence workflows without requiring a complex BI stack.

## Features
- Scrapes competitor collection data from a public Shopify JSON endpoint
- Extracts product variants and prices
- Tracks current competitor prices in Google Sheets
- Detects price changes between runs
- Logs every historical price change
- Highlights price drops in console output
- Supports local CSV export
- Uses centralized configuration in `src/config.py`

## Tech Stack
- Python
- requests
- gspread
- Google Sheets API
- python-dotenv

## Demo Output
```text
Page 1: 42 products
Page 2: 18 products

Price changed:
Gold Necklace (default)
120 → 99 🔥 PRICE DROP

Price changed:
Silver Necklace (Large)
89 → 95 ⬆ PRICE UP

Run summary:
- Total products: 73
- New: 4
- Updated: 2
- Price drops: 1
```

## Setup
Project structure:

```text
competitor-price-tracker/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── run.py
│   ├── scraper.py
│   └── sheets.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── service_account.json
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
SPREADSHEET_ID=your_google_sheet_id
```

Prepare Google Sheets with 2 worksheets:

### `current_data`
Stores the latest known state of each tracked product variant.

| product_id | title | variant | price | url | updated_at |
|-----------:|-------|---------|------:|-----|------------|

### `price_history`
Stores all detected price changes.

| product_id | old_price | new_price | changed_at |
|-----------:|----------:|----------:|------------|

Google Sheets access:
1. Create a Google Cloud project.
2. Enable Google Sheets API.
3. Create a Service Account.
4. Download the JSON key file.
5. Save it as `service_account.json` in the project root.
6. Share the spreadsheet with the service account email as Editor.

Run the tracker:

```bash
python -m src.run
```