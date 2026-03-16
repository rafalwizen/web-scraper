"""
Email scraper for panoramafirm.pl
"""
import time
import re
from typing import List
from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup
from config import settings


def is_valid_email(email: str) -> bool:
    """Check if email is valid"""
    if not email or email.lower() == 'brak':
        return False
    # Simple regex validation - checks for basic email structure
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    if not url:
        return False
    # Simple URL validation
    return url.startswith('http://') or url.startswith('https://')


def accept_cookies(page: Page) -> bool:
    """
    Accept cookies on the page using multiple selectors
    Similar to the JavaScript function provided

    Args:
        page: Playwright Page object

    Returns:
        True if cookies were accepted, False otherwise
    """
    print('Searching for and accepting cookies...')

    # Try multiple selectors for cookie acceptance
    selectors = [
        # Specific text-based selectors
        "button:has-text('Akceptuj wszystko')",
        "button:has-text('Accept all')",
        "button:has-text('Zaakceptuj')",
        "button:has-text('Akceptuj')",
        "button:has-text('Akceptuję')",
        "button:has-text('Zgadzam się')",
        # Data attributes
        "button[data-cookiefirst-action='accept']",
        "[data-cy='cookie-banner-button-accept']",
        "#onetrust-accept-btn-handler",
        ".accept-cookies",
        "#cookie-consent-accept",
        ".cookie-consent__accept",
        # Generic selectors
        "[id*='accept'][id*='cookie']",
        "[class*='accept'][class*='cookie']",
    ]

    # Try each selector
    for selector in selectors:
        try:
            button = page.locator(selector).first
            if button.is_visible(timeout=1000):
                print(f'Clicking cookie acceptance button (selector: {selector})...')
                button.click()
                print('Cookies accepted')
                time.sleep(1)  # Wait for popup to disappear
                return True
        except:
            continue

    # Try to find by text content in all buttons
    try:
        buttons = page.locator('button').all()
        for button in buttons:
            text = button.text_content()
            if text and (
                'Akceptuj' in text or
                'Accept' in text or
                'Zaakceptuj' in text or
                'Akceptuję' in text or
                'Zgadzam się' in text
            ):
                print('Clicking cookie acceptance button (by text content)...')
                button.click()
                print('Cookies accepted')
                time.sleep(1)
                return True
    except:
        pass

    print('Cookie acceptance button not found')
    return False


def handle_captcha(page: Page) -> bool:
    """
    Handle captcha/identity confirmation page

    Args:
        page: Playwright Page object

    Returns:
        True if captcha was handled, False otherwise
    """
    print('Checking for captcha/identity confirmation...')

    # Look for captcha confirmation button - try multiple selectors
    try:
        # Try by exact value
        captcha_button = page.locator('input[type="submit"][value="Potwierd"]').first
        if captcha_button.is_visible(timeout=1000):
            print('Found captcha confirmation button (exact match)')
            print('Manual intervention required for captcha - please complete the captcha and press Enter to continue')
            input('Press Enter after completing captcha...')
            print('Captcha handled')
            return True
    except:
        pass

    # Try by id
    try:
        captcha_form = page.locator('#form-recaptcha-submit').first
        if captcha_form.is_visible(timeout=1000):
            print('Found captcha form by id')
            print('Manual intervention required for captcha - please complete the captcha and press Enter to continue')
            input('Press Enter after completing captcha...')
            print('Captcha handled')
            return True
    except:
        pass

    # Try partial text match
    try:
        captcha_button = page.locator('input[type="submit"]').filter(has_text="Potwierd").first
        if captcha_button.is_visible(timeout=1000):
            print('Found captcha button (partial match)')
            print('Manual intervention required for captcha - please complete the captcha and press Enter to continue')
            input('Press Enter after completing captcha...')
            print('Captcha handled')
            return True
    except:
        pass

    print('No captcha found')
    return False


class PanoramaFirmScraper:
    """Class for scraping emails from panoramafirm.pl using Playwright"""

    def __init__(self):
        self.base_url = settings.base_url
        self.search_category = settings.search_category
        self.delay = settings.delay
        self.browser = None
        self.page = None
        self.playwright = None

    def start_browser(self):
        """Start Playwright browser"""
        self.playwright = sync_playwright().start()
        browser = getattr(self.playwright, settings.browser_type)
        self.browser = browser.launch(headless=settings.headless)
        self.page = self.browser.new_page()

    def stop_browser(self):
        """Stop Playwright browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def build_url(self, page: int = 1) -> str:
        """Build URL for results page"""
        url = f"{self.base_url}/{self.search_category}"
        if page > 1:
            url += f"?page={page}"
        return url

    def scrape_emails_from_page(self, page: int = 1) -> List[tuple]:
        """
        Scrape emails and websites from a single page

        Args:
            page: Page number

        Returns:
            List of tuples (website, email)
        """
        url = self.build_url(page)
        print(f"Fetching page: {url}")

        try:
            self.page.goto(url, wait_until='networkidle', timeout=30000)
        except Exception as e:
            print(f"Error loading page: {e}")
            return []

        # Handle cookie popup if present
        accept_cookies(self.page)

        # Handle captcha if present
        handle_captcha(self.page)

        # Get page content and parse with BeautifulSoup
        content = self.page.content()
        soup = BeautifulSoup(content, 'lxml')
        results = []

        # Debug: check what's on the page
        all_links = soup.find_all('a', attrs={'data-ga': True})
        data_ga_values = set([link.get('data-ga') for link in all_links])
        print(f"  DEBUG: Found {len(all_links)} links with data-ga attribute")
        print(f"  DEBUG: Unique data-ga values: {data_ga_values}")

        # Check for captcha form
        captcha_forms = soup.find_all('form')
        print(f"  DEBUG: Found {len(captcha_forms)} forms on page")
        for form in captcha_forms:
            inputs = form.find_all('input', attrs={'type': 'submit'})
            for inp in inputs:
                print(f"  DEBUG: Found submit input: value='{inp.get('value')}', id='{inp.get('id')}'")

        # Find all website links with data-ga="l-www"
        website_links = soup.find_all('a', attrs={'data-ga': 'l-www'})

        for website_link in website_links:
            website = website_link.get('href')
            if not website or not is_valid_url(website):
                continue

            # Find the parent element containing both website and email
            parent = website_link.find_parent()
            if not parent:
                continue

            # Find email link in the same parent container
            email_link = parent.find('a', attrs={'data-popup-param-email': True})
            email = email_link.get('data-popup-param-email') if email_link else None

            # Validate both website and email
            if is_valid_email(email):
                results.append((website, email))
                print(f"  Found: {website} | {email}")
            elif email:
                print(f"  Skipped invalid email: {email} (www: {website})")

        return results

    def scrape_all_emails(self) -> List[tuple]:
        """
        Scrape emails and websites from all pages

        Returns:
            List of all found (website, email) tuples
        """
        all_results = []
        page = 1
        max_pages = settings.max_pages

        while True:
            results = self.scrape_emails_from_page(page)

            if not results:
                print(f"No results found on page {page}, finishing...")
                break

            all_results.extend(results)
            print(f"Collected {len(all_results)} results total")

            # Delay between requests
            time.sleep(self.delay)

            page += 1

            # Safety limit - max pages from settings
            if page > max_pages:
                print(f"Reached {max_pages} page limit, finishing...")
                break

        return all_results

    def save_to_file(self, results: List[tuple], filename: str = None) -> None:
        """
        Save websites and emails to file in format: www,email

        Args:
            results: List of (website, email) tuples to save
            filename: Filename (default from settings)
        """
        if filename is None:
            filename = settings.output_file

        print(f"\nSaving {len(results)} results to file: {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            for website, email in sorted(set(results)):
                f.write(f"{website},{email}\n")

        print(f"Saved successfully!")


def main():
    """Main function"""
    print("=" * 60)
    print("Website and email scraper for panoramafirm.pl")
    print("=" * 60)
    print(f"Search category: {settings.search_category}")
    print(f"Base URL: {settings.base_url}")
    print(f"Delay: {settings.delay}s")
    print(f"Max pages: {settings.max_pages}")
    print("=" * 60)
    print()

    scraper = PanoramaFirmScraper()

    try:
        scraper.start_browser()
        results = scraper.scrape_all_emails()

        if results:
            scraper.save_to_file(results)
            print(f"\nCompleted! Found {len(results)} results.")
        else:
            print("\nNo results found.")
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    main()
