import os
from typing import Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars


class Settings:
    """Simple configuration class"""

    def __init__(self):
        # Keyword to append to URL
        self.search_category = os.getenv('SEARCH_CATEGORY', 'fryzjerzy_i_salony_fryzjerskie')
        # Base URL
        self.base_url = os.getenv('BASE_URL', 'https://panoramafirm.pl')
        # Output file name
        self.output_file = os.getenv('OUTPUT_FILE', 'emails.txt')
        # Delay between requests (seconds)
        self.delay = float(os.getenv('DELAY', '1.0'))
        # Max pages to scrape
        self.max_pages = int(os.getenv('MAX_PAGES', '50'))
        # Headless mode
        self.headless = os.getenv('HEADLESS', 'false').lower() == 'true'
        # Browser type
        self.browser_type = os.getenv('BROWSER_TYPE', 'chromium')

    def __getattr__(self, name: str) -> Any:
        """Get attribute value"""
        return self.__dict__.get(name)


settings = Settings()
