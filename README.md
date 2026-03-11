# PanoramaFirm Website and Email Scraper

Website and email scraper for panoramafirm.pl service.

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
- `MAX_PAGES` - maximum number of pages to scrape (default `50`)

## Usage

Run the scraper:
```bash
python panoramafirm_scraper.py
```

## Output Format

The scraper saves data in format: `www,email`
```
http://example.com,email@example.com
http://website.pl,info@website.pl
```

## How it works

The scraper:
1. Visits URL: `https://panoramafirm.pl/{SEARCH_CATEGORY}`
2. Searches the page for business cards with both website and email
3. Extracts website URLs from `data-ga="l-www"` links
4. Extracts emails from `data-popup-param-email` attributes
5. Validates both website and email formats
6. Saves pairs (website,email) to file
7. Moves to next pages if available

## Category Examples

- `fryzjerzy_i_salony_fryzjerskie` - hair salons
- `restauracje` - restaurants
- `stacje_paliw` - gas stations
- `sklepy_spozywcze` - grocery stores

## Notes

- The scraper only extracts visible data from business cards
- Default limit is 50 pages (can be changed in `.env` file)
- Only business cards with valid website AND email are saved
- Remember to comply with website terms and legal scraping guidelines
