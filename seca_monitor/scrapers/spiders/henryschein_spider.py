"""
Henry Schein Spider - Adapted from SecaScraper
Specific to Henry Schein website structure
"""
import time
import logging
from django.utils import timezone
from .base_spider import BaseSpider
from scrapers.models import DealerProductListing, YourProduct

logger = logging.getLogger('scrapers')


class HenryScheinSpider(BaseSpider):
    """
    Spider for scraping Henry Schein product listings
    Adapted from original SecaScraper implementation
    """

    def __init__(self, dealer):
        super().__init__(dealer)
        self.products_scraped = 0
        self.products_with_changes = 0
        self.errors = 0

    def scrape_product_detail(self, url):
        """
        Scrape individual Henry Schein product detail page

        Args:
            url: Product URL to scrape

        Returns:
            Product data dictionary or None if failed
        """
        try:
            logger.info(f"Scraping product: {url}")

            # Navigate to product page
            html_content = self.navigate_to_url(url)
            soup = self.parse_html(html_content)

            # Extract product information using Henry Schein-specific selectors
            product_data = {
                'product_name': self._extract_text(
                    soup,
                    'h1.product-name, .product-title, h1.product-detail-title, .pdp-title'
                ),
                'dealer_sku': self._extract_text(
                    soup,
                    '.product-sku, [data-sku], .sku-number, .item-number'
                ),
                'mpn': self._extract_text(
                    soup,
                    '.mpn, .manufacturer-number, [data-mpn], .mfr-part-number'
                ),
                'description': self._extract_description(soup),
                'features': self._extract_features(soup),
                'technical_specs': self._extract_specifications(soup),
                'product_url': url,
            }

            # Combine description and features
            description_features = self._combine_description_features(
                product_data['description'],
                product_data['features']
            )

            # Save to Django ORM
            listing = self.save_to_django({
                'product_name': product_data['product_name'],
                'dealer_sku': product_data['dealer_sku'],
                'mpn': product_data['mpn'],
                'description_features': description_features,
                'specifications': product_data['technical_specs'],
                'product_url': product_data['product_url'],
            })

            self.products_scraped += 1

            if listing and listing.content_changed:
                self.products_with_changes += 1
                logger.info(f"Content changed for {product_data['dealer_sku']}")

            logger.info(f"Successfully scraped: {product_data['product_name']}")
            return product_data

        except Exception as e:
            logger.error(f"Failed to scrape product {url}: {str(e)}")
            self.errors += 1
            return None

    def _extract_description(self, soup):
        """
        Extract product description from Henry Schein page

        Args:
            soup: BeautifulSoup object

        Returns:
            Description text
        """
        # Try multiple common description selectors
        description_selectors = [
            '.product-description',
            '.description',
            '#product-description',
            '.product-detail-description',
            '.pdp-description',
            '[itemprop="description"]',
        ]

        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                # Get all text, preserving paragraph breaks
                paragraphs = element.find_all('p')
                if paragraphs:
                    return '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                else:
                    return element.get_text(strip=True)

        return ''

    def _extract_features(self, soup):
        """
        Extract product features/bullet points

        Args:
            soup: BeautifulSoup object

        Returns:
            Features as formatted string
        """
        features = []

        # Try multiple feature list selectors
        feature_selectors = [
            '.product-features ul',
            '.features ul',
            '#product-features ul',
            '.key-features ul',
            '.highlights ul',
        ]

        for selector in feature_selectors:
            feature_items = self._extract_list_items(soup, selector)
            if feature_items:
                features.extend(feature_items)
                break

        # Also check for div-based features
        if not features:
            feature_divs = soup.select('.feature-item, .product-feature')
            for div in feature_divs:
                text = div.get_text(strip=True)
                if text:
                    features.append(text)

        return '\n• '.join([''] + features) if features else ''

    def _combine_description_features(self, description, features):
        """
        Combine description and features into single field

        Args:
            description: Description text
            features: Features text

        Returns:
            Combined text
        """
        parts = []

        if description:
            parts.append(description)

        if features:
            parts.append("\n\nFeatures:" + features)

        return '\n\n'.join(parts)

    def save_to_django(self, product_data):
        """
        Save product data to Django ORM with change detection

        Args:
            product_data: Dictionary with product information

        Returns:
            DealerProductListing instance or None
        """
        try:
            # Skip if missing required fields
            if not product_data.get('dealer_sku'):
                logger.warning(f"Skipping product - missing dealer_sku")
                return None

            # Update or create listing
            listing, created = DealerProductListing.objects.update_or_create(
                dealer=self.dealer,
                dealer_sku=product_data['dealer_sku'],
                defaults={
                    'product_name': product_data.get('product_name', ''),
                    'mpn': product_data.get('mpn', ''),
                    'description_features': product_data.get('description_features', ''),
                    'specifications': product_data.get('specifications', ''),
                    'product_url': product_data.get('product_url', ''),
                    'scrape_timestamp': timezone.now(),
                }
            )

            # Check for content changes
            diff_status, diff_content = listing.check_for_changes()
            listing.save()

            if created:
                logger.info(f"Created new listing for {product_data['dealer_sku']}")
            else:
                logger.info(f"Updated listing for {product_data['dealer_sku']} - Changed: {diff_status}")

            return listing

        except Exception as e:
            logger.error(f"Failed to save product to database: {str(e)}")
            return None

    def scrape_product_list_page(self, list_url):
        """
        Scrape product listing/category page to get product URLs
        Implement this based on your specific needs

        Args:
            list_url: URL of product listing page

        Returns:
            List of product URLs
        """
        try:
            logger.info(f"Scraping product list: {list_url}")

            html_content = self.navigate_to_url(list_url)
            soup = self.parse_html(html_content)

            # Extract product URLs (adjust selectors based on actual site structure)
            product_links = []
            link_selectors = [
                '.product-item a',
                '.product-link',
                'a.product-name',
                '.product-grid a',
                '.search-result-items a',
                'a[href*="/dental/"], a[href*="/medical/"]',  # Henry Schein specific
            ]

            for selector in link_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        # Make absolute URL
                        if href.startswith('/'):
                            href = self.base_url.rstrip('/') + href
                        elif not href.startswith('http'):
                            href = self.base_url.rstrip('/') + '/' + href

                        # Only add product detail pages, not category/search pages
                        if 'Search.aspx' not in href and href not in product_links:
                            product_links.append(href)

            logger.info(f"Found {len(product_links)} product links on this page")
            return product_links

        except Exception as e:
            logger.error(f"Failed to scrape product list {list_url}: {str(e)}")
            return []

    def scrape_all_list_pages(self, start_url, max_pages=10):
        """
        Scrape all paginated product listing pages

        Args:
            start_url: First page URL
            max_pages: Maximum number of pages to scrape (safety limit)

        Returns:
            List of all product URLs from all pages
        """
        all_product_urls = []

        try:
            logger.info(f"Starting pagination scrape from: {start_url}")

            # Henry Schein uses URL parameter: pagenumber=1, pagenumber=2, etc.
            for page_num in range(1, max_pages + 1):
                logger.info(f"Scraping page {page_num} of {max_pages}...")

                # Build URL for this page
                if 'pagenumber=' in start_url:
                    # Replace existing page number
                    import re
                    page_url = re.sub(r'pagenumber=\d+', f'pagenumber={page_num}', start_url)
                else:
                    # Add page number parameter
                    separator = '&' if '?' in start_url else '?'
                    page_url = f"{start_url}{separator}pagenumber={page_num}"

                # Navigate to page
                html_content = self.navigate_to_url(page_url)
                soup = self.parse_html(html_content)

                # Extract product URLs from current page
                page_urls = self.scrape_product_list_page_from_soup(soup)

                # If no products found, we've likely reached the end
                if not page_urls:
                    logger.info(f"No products found on page {page_num}. Stopping pagination.")
                    break

                all_product_urls.extend(page_urls)
                logger.info(f"Page {page_num}: Found {len(page_urls)} products. Total so far: {len(all_product_urls)}")

                # Small delay between pages
                time.sleep(1)

            logger.info(f"Pagination complete. Total products found: {len(all_product_urls)}")
            return all_product_urls

        except Exception as e:
            logger.error(f"Error during pagination: {str(e)}")
            return all_product_urls

    def scrape_product_list_page_from_soup(self, soup):
        """
        Extract product URLs from a BeautifulSoup object of a listing page

        Args:
            soup: BeautifulSoup object of listing page

        Returns:
            List of product URLs
        """
        product_links = []

        link_selectors = [
            '.product-item a',
            '.product-link',
            'a.product-name',
            '.product-grid a',
            '.search-result-items a',
            'a[href*="/dental/"], a[href*="/medical/"]',
        ]

        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Make absolute URL
                    if href.startswith('/'):
                        href = self.base_url.rstrip('/') + href
                    elif not href.startswith('http'):
                        href = self.base_url.rstrip('/') + '/' + href

                    # Only add product detail pages
                    if 'Search.aspx' not in href and href not in product_links:
                        product_links.append(href)

        return product_links

    def run(self, product_urls=None, listing_page_url=None):
        """
        Main execution method for Henry Schein scraper

        Args:
            product_urls: Optional list of product URLs to scrape
            listing_page_url: Optional URL of product listing page (will paginate through all pages)
        """
        try:
            logger.info(f"Starting Henry Schein scraper for {self.dealer.name}")

            # Initialize browser
            self.init_browser()

            # If listing page URL is provided, scrape all pages to get product URLs
            if listing_page_url:
                logger.info(f"Scraping listing page with pagination: {listing_page_url}")
                product_urls = self.scrape_all_list_pages(listing_page_url, max_pages=10)
                logger.info(f"Collected {len(product_urls)} product URLs from listing pages")

            # If no product URLs provided or collected, show warning
            if not product_urls:
                logger.warning("No product URLs provided. You need to either:")
                logger.warning("1. Pass product_urls to run() method")
                logger.warning("2. Pass listing_page_url to run() method")
                logger.warning("3. Provide URLs from your product catalog")
                product_urls = []

            # Scrape each product
            for i, url in enumerate(product_urls, 1):
                try:
                    logger.info(f"Scraping product {i}/{len(product_urls)}")
                    self.scrape_product_detail(url)
                    # Add delay between requests
                    time.sleep(self.delay)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    continue

            # Summary
            logger.info("=" * 60)
            logger.info("SCRAPING SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Dealer: {self.dealer.name}")
            logger.info(f"Products scraped: {self.products_scraped}")
            logger.info(f"Products with changes: {self.products_with_changes}")
            logger.info(f"Errors: {self.errors}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Fatal error in scraper: {str(e)}")
            raise

        finally:
            # Clean up browser
            self.close_browser()
