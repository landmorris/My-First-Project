"""
Base spider class with common Playwright initialization and methods
All dealer spiders inherit from this
"""
import asyncio
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup
from django.conf import settings

logger = logging.getLogger('scrapers')


class BaseSpider:
    """
    Base class with common Playwright initialization and utility methods
    """

    def __init__(self, dealer):
        """
        Initialize spider with dealer instance

        Args:
            dealer: Django Dealer model instance
        """
        self.dealer = dealer
        self.base_url = dealer.website
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

        # Settings from Django config
        self.user_agent = settings.SCRAPER_USER_AGENT
        self.headless = settings.SCRAPER_HEADLESS
        self.timeout = settings.SCRAPER_TIMEOUT
        self.delay = settings.SCRAPER_DELAY

        logger.info(f"Initialized {self.__class__.__name__} for {dealer.name}")

    async def init_browser(self):
        """
        Initialize Playwright browser with optimal settings
        """
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

            self.context = await self.browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True,
            )

            # Set default timeout
            self.context.set_default_timeout(self.timeout)

            self.page = await self.context.new_page()
            logger.info("Browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def close_browser(self):
        """
        Clean up browser resources
        """
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

    async def navigate_to_url(self, url, wait_for='load'):
        """
        Navigate to URL with error handling

        Args:
            url: URL to navigate to
            wait_for: Wait until condition ('load', 'domcontentloaded', 'networkidle')

        Returns:
            Page content as string
        """
        try:
            logger.info(f"Navigating to: {url}")
            response = await self.page.goto(url, wait_until=wait_for)

            if response.status != 200:
                logger.warning(f"Non-200 response: {response.status}")

            # Wait for content to load
            await asyncio.sleep(self.delay)

            content = await self.page.content()
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

    async def scrape_product_detail(self, url):
        """
        Scrape individual product detail page
        This method should be implemented by each dealer-specific spider

        Args:
            url: Product URL to scrape

        Returns:
            Product data dictionary
        """
        raise NotImplementedError("Subclasses must implement scrape_product_detail()")

    async def run(self):
        """
        Main execution method
        This method should be implemented by each dealer-specific spider
        """
        raise NotImplementedError("Subclasses must implement run()")
