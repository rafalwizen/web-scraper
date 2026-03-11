"""
Email scraper for panoramafirm.pl
"""
import time
import re
from typing import List
import requests
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


class PanoramaFirmScraper:
    """Class for scraping emails from panoramafirm.pl"""

    def __init__(self):
        self.base_url = settings.base_url
        self.search_category = settings.search_category
        self.delay = settings.delay
        self.session = requests.Session()
        # Add headers to look like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

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
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        results = []

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
    results = scraper.scrape_all_emails()

    if results:
        scraper.save_to_file(results)
        print(f"\nCompleted! Found {len(results)} results.")
    else:
        print("\nNo results found.")


if __name__ == "__main__":
    main()
