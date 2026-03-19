"""
Email scraper for panoramafirm.pl
"""
import time
import re
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

    def scrape_emails_from_page(self, page: int = 1) -> dict:
        """
        Scrape emails and websites from a single page

        Args:
            page: Page number

        Returns:
            Dictionary with categorized results:
            {
                'only_websites': [websites],
                'only_emails': [emails],
                'both': [(website, email)]
            }
        """
        url = self.build_url(page)
        print(f"Fetching page: {url}")

        try:
            self.page.goto(url, wait_until='networkidle', timeout=30000)
        except Exception as e:
            print(f"Error loading page: {e}")
            return {'only_websites': [], 'only_emails': [], 'both': []}

        # Handle cookie popup if present
        accept_cookies(self.page)

        # Handle captcha if present
        handle_captcha(self.page)

        # Get page content and parse with BeautifulSoup
        content = self.page.content()
        soup = BeautifulSoup(content, 'lxml')

        results = {
            'only_websites': [],
            'only_emails': [],
            'both': []
        }

        # Track processed companies to avoid duplicates
        processed_parents = set()

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

            # Skip if we already processed this parent
            parent_id = str(parent)
            if parent_id in processed_parents:
                continue
            processed_parents.add(parent_id)

            # Find email link in the same parent container
            email_link = parent.find('a', attrs={'data-popup-param-email': True})
            email = email_link.get('data-popup-param-email') if email_link else None

            # Categorize the result
            if is_valid_email(email):
                results['both'].append((website, email))
                print(f"  Found: {website} | {email}")
            else:
                results['only_websites'].append(website)
                print(f"  Found website only: {website}")

        # Also find emails that don't have websites
        email_links = soup.find_all('a', attrs={'data-popup-param-email': True})
        processed_emails = set()

        for email_link in email_links:
            email = email_link.get('data-popup-param-email')
            if not is_valid_email(email):
                continue

            # Skip if this email is already in 'both' category
            for _, both_email in results['both']:
                if both_email == email:
                    continue

            # Check if this email already has a website
            has_website = False
            for website, both_email in results['both']:
                if both_email == email:
                    has_website = True
                    break

            if not has_website and email not in processed_emails:
                results['only_emails'].append(email)
                processed_emails.add(email)
                print(f"  Found email only: {email}")

        return results

    def scrape_all_emails(self) -> dict:
        """
        Scrape emails and websites from all pages

        Returns:
            Dictionary with categorized results:
            {
                'only_websites': [websites],
                'only_emails': [emails],
                'both': [(website, email)]
            }
        """
        all_results = {
            'only_websites': [],
            'only_emails': [],
            'both': []
        }
        page = 1
        max_pages = settings.max_pages

        while True:
            page_results = self.scrape_emails_from_page(page)

            # Continue even if no results on this page - some pages may be empty

            # Merge results
            all_results['only_websites'].extend(page_results['only_websites'])
            all_results['only_emails'].extend(page_results['only_emails'])
            all_results['both'].extend(page_results['both'])

            total_results = (len(all_results['only_websites']) +
                           len(all_results['only_emails']) +
                           len(all_results['both']))
            print(f"Collected {total_results} results total ({len(all_results['only_websites'])} websites, {len(all_results['only_emails'])} emails, {len(all_results['both'])} both)")

            # Delay between requests
            time.sleep(self.delay)

            page += 1

            # Safety limit - max pages from settings
            if page > max_pages:
                print(f"Reached {max_pages} page limit, finishing...")
                break

        return all_results

    def save_to_file(self, results: dict) -> None:
        """
        Save websites and emails to categorized files

        Args:
            results: Dictionary with categorized results:
            {
                'only_websites': [websites],
                'only_emails': [emails],
                'both': [(website, email)]
            }
        """
        print(f"\nSaving results to files...")

        # Save only websites
        with open('resultOnlyWebsites.txt', 'w', encoding='utf-8') as f:
            for website in sorted(set(results['only_websites'])):
                f.write(f"{website}\n")
        print(f"Saved {len(set(results['only_websites']))} websites to resultOnlyWebsites.txt")

        # Save only emails
        with open('resultOnlyEmail.txt', 'w', encoding='utf-8') as f:
            for email in sorted(set(results['only_emails'])):
                f.write(f"{email}\n")
        print(f"Saved {len(set(results['only_emails']))} emails to resultOnlyEmail.txt")

        # Save both website and email
        with open('resultWebAndEmail.txt', 'w', encoding='utf-8') as f:
            for website, email in sorted(set(results['both'])):
                f.write(f"{website},{email}\n")
        print(f"Saved {len(set(results['both']))} website,email pairs to resultWebAndEmail.txt")

        # Save all unique websites
        all_websites = results['only_websites'] + [website for website, _ in results['both']]
        unique_websites = sorted(set(all_websites))
        with open('websites.txt', 'w', encoding='utf-8') as f:
            for website in unique_websites:
                f.write(f"{website}\n")
        print(f"Saved {len(unique_websites)} unique websites to websites.txt")

        print(f"\nAll files saved successfully!")


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

        # Check if any results were found
        total_results = (len(results['only_websites']) +
                       len(results['only_emails']) +
                       len(results['both']))

        if total_results > 0:
            scraper.save_to_file(results)
            print(f"\nCompleted! Found {total_results} results total:")
            print(f"  - {len(results['only_websites'])} websites only")
            print(f"  - {len(results['only_emails'])} emails only")
            print(f"  - {len(results['both'])} both website and email")
        else:
            print("\nNo results found.")
    finally:
        scraper.stop_browser()


if __name__ == "__main__":
    main()
