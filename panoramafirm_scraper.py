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

    def scrape_emails_from_page(self, page: int = 1) -> List[str]:
        """
        Scrape emails from a single page

        Args:
            page: Page number

        Returns:
            List of found emails
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
        emails = []

        # Find all links with data-popup-param-email attribute
        email_links = soup.find_all('a', attrs={'data-popup-param-email': True})

        for link in email_links:
            email = link.get('data-popup-param-email')
            # Email validation - skip "brak" and invalid formats
            if email and is_valid_email(email) and email not in emails:
                emails.append(email)
                print(f"  Found email: {email}")
            elif email and not is_valid_email(email):
                print(f"  Skipped invalid email: {email}")

        return emails

    def scrape_all_emails(self) -> List[str]:
        """
        Scrape emails from all pages

        Returns:
            List of all found emails
        """
        all_emails = []
        page = 1

        while True:
            emails = self.scrape_emails_from_page(page)

            if not emails:
                print(f"No emails found on page {page}, finishing...")
                break

            all_emails.extend(emails)
            print(f"Collected {len(all_emails)} unique emails total")

            # Delay between requests
            time.sleep(self.delay)

            page += 1

            # Safety limit - max 50 pages
            if page > 50:
                print("Reached 50 page limit, finishing...")
                break

        return all_emails

    def save_to_file(self, emails: List[str], filename: str = None) -> None:
        """
        Save emails to file

        Args:
            emails: List of emails to save
            filename: Filename (default from settings)
        """
        if filename is None:
            filename = settings.output_file

        print(f"\nSaving {len(emails)} emails to file: {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            for email in sorted(set(emails)):
                f.write(f"{email}\n")

        print(f"Saved successfully!")


def main():
    """Main function"""
    print("=" * 60)
    print("Email scraper for panoramafirm.pl")
    print("=" * 60)
    print(f"Search category: {settings.search_category}")
    print(f"Base URL: {settings.base_url}")
    print(f"Delay: {settings.delay}s")
    print("=" * 60)
    print()

    scraper = PanoramaFirmScraper()
    emails = scraper.scrape_all_emails()

    if emails:
        scraper.save_to_file(emails)
        print(f"\nCompleted! Found {len(emails)} unique emails.")
    else:
        print("\nNo emails found.")


if __name__ == "__main__":
    main()
