# PanoramaFirm Email Scraper

Email scraper for panoramafirm.pl service.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy configuration file:
```bash
cp .env.example .env
```

3. Edit `.env` file and set appropriate values:
- `SEARCH_CATEGORY` - keyword to append to URL (e.g. `fryzjerzy_i_salony_fryzjerskie`)
- `BASE_URL` - base URL (default `https://panoramafirm.pl`)
- `OUTPUT_FILE` - output file name (default `emails.txt`)
- `DELAY` - delay between requests in seconds (default `1.0`)

## Usage

Run the scraper:
```bash
python panoramafirm_scraper.py
```

## How it works

The scraper:
1. Visits URL: `https://panoramafirm.pl/{SEARCH_CATEGORY}`
2. Searches the page for elements with `data-popup-param-email` attribute
3. Saves found emails to file
4. Moves to next pages if available

## Category Examples

- `fryzjerzy_i_salony_fryzjerskie` - hair salons
- `restauracje` - restaurants
- `stacje_paliw` - gas stations
- `sklepy_spozywcze` - grocery stores

## Notes

- The scraper only extracts visible emails from business cards
- Default limit is 50 pages (can be changed in code)
- Remember to comply with website terms and legal scraping guidelines
