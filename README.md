# PanoramaFirm Website and Email Scraper

Website and email scraper for panoramafirm.pl service using Playwright with JavaScript support.

## Features

- **JavaScript Support**: Uses Playwright for full JavaScript rendering
- **Cookie Handling**: Automatically accepts cookies to access protected content
- **Captcha Handling**: Detects and handles captcha verification
- **Result Categorization**: Segregates business cards into 3 categories
- **Headless Mode**: Option to run browser invisibly in background
- **Smart Scraping**: Finds businesses with websites only, emails only, or both

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy configuration file:
```bash
cp .env.example .env
```

3. Install Playwright browsers:
```bash
python -m playwright install
```

## Configuration

Edit `.env` file and set appropriate values:
- `SEARCH_CATEGORY` - keyword to append to URL (e.g. `fryzjerzy_i_salony_fryzjerskie`)
- `BASE_URL` - base URL (default `https://panoramafirm.pl`)
- `OUTPUT_FILE` - output file name (default `emails.txt`)
- `DELAY` - delay between requests in seconds (default `1.0`)
- `MAX_PAGES` - maximum number of pages to scrape (default `3`)
- `HEADLESS` - headless mode (default `false` - shows browser window)
- `BROWSER_TYPE` - browser type (default `chromium`, options: `firefox`, `webkit`)

## Usage

Run the scraper:
```bash
python panoramafirm_scraper.py
```

## Output Files

The scraper creates 4 categorized files:

1. **resultOnlyWebsites.txt** - businesses with websites only (one per line)
```
http://example.com
https://website.pl
```

2. **resultOnlyEmail.txt** - businesses with emails only (one per line)
```
email@example.com
info@website.pl
```

3. **resultWebAndEmail.txt** - businesses with both website and email (www,email format)
```
http://example.com,email@example.com
https://website.pl,info@website.pl
```

4. **websites.txt** - all unique websites (from both resultOnlyWebsites.txt and resultWebAndEmail.txt)
```
http://example.com
https://website.pl
```

## How it works

The scraper:
1. Starts Playwright browser with configured settings
2. Visits URL: `https://panoramafirm.pl/{SEARCH_CATEGORY}`
3. Accepts cookie consent if present
4. Handles captcha verification if required
5. Searches the page for business cards
6. Extracts website URLs from `data-ga="l-www"` links
7. Extracts emails from `data-popup-param-email` attributes
8. Categorizes results:
   - **Both**: Business cards with valid website AND email
   - **Website only**: Business cards with website but no email
   - **Email only**: Business cards with email but no website
9. Saves categorized results to separate files
10. Moves to next pages if available
11. Creates websites.txt with all unique websites

## Category Examples

- `fryzjerzy_i_salony_fryzjerskie` - hair salons
- `restauracje` - restaurants
- `stacje_paliw` - gas stations
- `sklepy_spozywcze` - grocery stores

## Browser Modes

### Headless Mode (Default: false)
- `HEADLESS=false` - Shows browser window (useful for debugging)
- `HEADLESS=true` - Runs browser invisibly (faster, uses less resources)

### Browser Types
- `chromium` - Default browser, fastest
- `firefox` - Firefox browser
- `webkit` - Safari/WebKit browser

## Notes

- The scraper uses Playwright for full JavaScript support
- Overwrites output files on each run
- Creates 4 categorized files plus websites.txt
- All files are sorted and contain no duplicates
- Default limit is 3 pages (can be changed in `.env` file)
- Automatically handles cookies and captcha
- Remember to comply with website terms and legal scraping guidelines
