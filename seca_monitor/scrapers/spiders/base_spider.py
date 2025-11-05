"""
Base spider class with common Selenium initialization and methods
All dealer spiders inherit from this
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from django.conf import settings

logger = logging.getLogger('scrapers')


class BaseSpider:
    """
    Base class with common Selenium initialization and utility methods
    """

    def __init__(self, dealer):
        """
        Initialize spider with dealer instance

        Args:
            dealer: Django Dealer model instance
        """
        self.dealer = dealer
        self.base_url = dealer.website
        self.driver = None

        # Settings from Django config
        self.user_agent = settings.SCRAPER_USER_AGENT
        self.headless = settings.SCRAPER_HEADLESS
        self.timeout = settings.SCRAPER_TIMEOUT // 1000  # Convert ms to seconds
        self.delay = settings.SCRAPER_DELAY

        logger.info(f"Initialized {self.__class__.__name__} for {dealer.name}")

    def init_browser(self):
        """
        Initialize Selenium browser with optimal settings
        """
        try:
            # Configure Chrome options
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')

            # Anti-detection settings
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument(f'user-agent={self.user_agent}')
            chrome_options.add_argument('--window-size=1920,1080')

            # Exclude automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Initialize WebDriver with webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Set timeouts
            self.driver.implicitly_wait(self.timeout)
            self.driver.set_page_load_timeout(self.timeout)

            logger.info("Browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    def close_browser(self):
        """
        Clean up browser resources
        """
        try:
            if self.driver:
                self.driver.quit()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

    def navigate_to_url(self, url, wait_for_selector=None):
        """
        Navigate to URL with error handling

        Args:
            url: URL to navigate to
            wait_for_selector: Optional CSS selector to wait for after page load

        Returns:
            Page content as string
        """
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)

            # Wait for specific element if provided
            if wait_for_selector:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )

            # Additional delay for content to load
            time.sleep(self.delay)

            content = self.driver.page_source
            return content

        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise

    def _extract_text(self, soup, selector, default=''):
        """
        Extract text from BeautifulSoup element using CSS selector
        Tries multiple selectors if provided as comma-separated string

        Args:
            soup: BeautifulSoup object
            selector: CSS selector or comma-separated selectors
            default: Default value if not found

        Returns:
            Extracted text or default value
        """
        if not soup:
            return default

        # Split selectors if comma-separated
        selectors = [s.strip() for s in selector.split(',')]

        for sel in selectors:
            try:
                element = soup.select_one(sel)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
            except Exception as e:
                logger.debug(f"Selector '{sel}' failed: {str(e)}")
                continue

        return default

    def _extract_specifications(self, soup):
        """
        Extract technical specifications from product page
        Looks for common specification table patterns

        Args:
            soup: BeautifulSoup object

        Returns:
            Formatted specifications string
        """
        specs = []

        # Common specification table selectors
        spec_selectors = [
            '.specifications table',
            '.product-specs table',
            '.tech-specs table',
            'table.specs',
            '#specifications table',
            '.product-details table',
        ]

        for selector in spec_selectors:
            tables = soup.select(selector)
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            specs.append(f"{key}: {value}")

        # Also look for dl/dt/dd patterns
        dl_selectors = [
            '.specifications dl',
            '.product-specs dl',
            '#specifications dl',
        ]

        for selector in dl_selectors:
            dls = soup.select(selector)
            for dl in dls:
                dts = dl.find_all('dt')
                dds = dl.find_all('dd')
                for dt, dd in zip(dts, dds):
                    key = dt.get_text(strip=True)
                    value = dd.get_text(strip=True)
                    if key and value:
                        specs.append(f"{key}: {value}")

        return '\n'.join(specs) if specs else ''

    def _extract_list_items(self, soup, selector):
        """
        Extract list items from ul/ol elements

        Args:
            soup: BeautifulSoup object
            selector: CSS selector for list container

        Returns:
            List of text items
        """
        items = []
        container = soup.select_one(selector)
        if container:
            list_items = container.find_all('li')
            for li in list_items:
                text = li.get_text(strip=True)
                if text:
                    items.append(text)
        return items

    def parse_html(self, html_content):
        """
        Parse HTML content with BeautifulSoup

        Args:
            html_content: HTML string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html_content, 'html.parser')

    def scrape_product_detail(self, url):
        """
        Scrape individual product detail page
        This method should be implemented by each dealer-specific spider

        Args:
            url: Product URL to scrape

        Returns:
            Product data dictionary
        """
        raise NotImplementedError("Subclasses must implement scrape_product_detail()")

    def run(self):
        """
        Main execution method
        This method should be implemented by each dealer-specific spider
        """
        raise NotImplementedError("Subclasses must implement run()")
