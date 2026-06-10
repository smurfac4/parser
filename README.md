# Vinted Parser

A desktop app for monitoring Vinted listings. Scrapes a catalog, stores items in a local database, and tracks price changes.

## Stack

- Python 3.x
- Playwright (headless Chromium) — page rendering
- BeautifulSoup4 — HTML parsing
- SQLite3 — local storage
- Tkinter/TTK — UI

## Installation

```bash
pip install playwright beautifulsoup4
playwright install chromium
```

## Usage

```bash
python main.py
```

On Windows, if PowerShell complains about `&`:

```powershell
Start-Process "python" -ArgumentList "main.py" -NoNewWindow -Wait
```

## Interface

1. Paste a Vinted catalog URL into the URL field
2. Click **Run Parser** — the app scrapes the page and saves items to `base.db`
3. Click a column header (`ID`, `Title`, `Price`) to sort
4. **Enable auto-scraping** — reruns automatically every 5/15/30 minutes
5. **Export to CSV** — saves current data to a file