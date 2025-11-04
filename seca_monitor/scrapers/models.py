"""
Django models for Seca Product Monitor
"""
import hashlib
from django.db import models
from django.utils import timezone


class Dealer(models.Model):
    """
    Dealer/Partner websites to monitor
    """
    name = models.CharField(max_length=200, unique=True, help_text="Dealer name (e.g., Henry Schein)")
    website = models.URLField(help_text="Dealer website URL")
    spider_class = models.CharField(
        max_length=100,
        help_text="Spider class name (e.g., HenryScheinSpider)"
    )
    is_active = models.BooleanField(default=True, help_text="Enable/disable scraping for this dealer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dealers'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_spider_instance(self):
        """
        Dynamically import and instantiate the spider class
        """
        from scrapers.spiders.henryschein_spider import HenryScheinSpider
        from scrapers.spiders.dealer2_spider import Dealer2Spider
        from scrapers.spiders.dealer3_spider import Dealer3Spider
        from scrapers.spiders.dealer4_spider import Dealer4Spider

        spider_classes = {
            'HenryScheinSpider': HenryScheinSpider,
            'Dealer2Spider': Dealer2Spider,
            'Dealer3Spider': Dealer3Spider,
            'Dealer4Spider': Dealer4Spider,
        }

        spider_class = spider_classes.get(self.spider_class)
        if spider_class:
            return spider_class(self)
        else:
            raise ValueError(f"Unknown spider class: {self.spider_class}")


class YourProduct(models.Model):
    """
    Your internal product catalog
    """
    your_sku = models.CharField(max_length=100, unique=True, help_text="Your internal SKU")
    mpn = models.CharField(max_length=100, blank=True, help_text="Manufacturer Part Number")
    product_name = models.CharField(max_length=500, help_text="Your product name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'your_products'
        ordering = ['your_sku']
        verbose_name = 'Your Product'
        verbose_name_plural = 'Your Products'

    def __str__(self):
        return f"{self.your_sku} - {self.product_name}"


class DealerProductListing(models.Model):
    """
    Current dealer product listings with change tracking
    """
    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    your_product = models.ForeignKey(
        YourProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dealer_listings',
        help_text="Link to your product catalog (optional)"
    )

    # Dealer product information
    product_name = models.CharField(max_length=500, help_text="Product name on dealer site")
    dealer_sku = models.CharField(max_length=100, help_text="Dealer SKU/Part Number")
    mpn = models.CharField(max_length=100, blank=True, help_text="Manufacturer Part Number")

    # Content fields
    description_features = models.TextField(
        blank=True,
        help_text="Combined description and features from dealer site"
    )
    specifications = models.TextField(
        blank=True,
        help_text="Technical specifications"
    )

    # Metadata
    product_url = models.URLField(max_length=1000, help_text="URL to product on dealer site")
    scrape_timestamp = models.DateTimeField(default=timezone.now, help_text="Last scraped date/time")

    # Change tracking
    content_changed = models.BooleanField(default=False, help_text="Content changed since last scrape")
    previous_content_hash = models.CharField(max_length=32, blank=True, help_text="MD5 hash of previous content")
    diff_content = models.TextField(blank=True, help_text="Description of what changed")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dealer_product_listings'
        ordering = ['-scrape_timestamp']
        unique_together = ['dealer', 'dealer_sku']
        indexes = [
            models.Index(fields=['dealer', 'dealer_sku']),
            models.Index(fields=['mpn']),
            models.Index(fields=['content_changed']),
        ]

    def __str__(self):
        return f"{self.dealer.name} - {self.dealer_sku}"

    def check_for_changes(self):
        """
        Compare current content with previous scrape
        Returns: (status, diff_details) where status is 'Yes' or 'None'
        """
        # Generate current content hash
        current_content = f"{self.product_name}{self.description_features}{self.specifications}"
        current_hash = hashlib.md5(current_content.encode('utf-8')).hexdigest()

        # If we have a previous hash, compare
        if self.previous_content_hash and self.previous_content_hash != current_hash:
            # Content changed!
            self.content_changed = True

            # Save to history before updating
            DealerProductListingHistory.objects.create(
                dealer=self.dealer,
                dealer_sku=self.dealer_sku,
                product_name=self.product_name,
                description_features=self.description_features,
                specifications=self.specifications,
                product_url=self.product_url,
                scraped_at=self.scrape_timestamp
            )

            # Determine what changed
            diff_details = self._get_diff_details()
            self.diff_content = diff_details
            self.previous_content_hash = current_hash

            return 'Yes', diff_details

        # No changes or first scrape
        self.content_changed = False
        self.previous_content_hash = current_hash
        return 'None', ''

    def _get_diff_details(self):
        """
        Get details about what changed
        """
        # Get the most recent history entry
        history = DealerProductListingHistory.objects.filter(
            dealer=self.dealer,
            dealer_sku=self.dealer_sku
        ).order_by('-scraped_at').first()

        if not history:
            return "First scrape - no previous data"

        changes = []

        if history.product_name != self.product_name:
            changes.append(f"Name: '{history.product_name}' → '{self.product_name}'")

        if history.description_features != self.description_features:
            changes.append("Description/Features changed")

        if history.specifications != self.specifications:
            changes.append("Specifications changed")

        return "; ".join(changes) if changes else "Content hash mismatch"

    def get_your_sku(self):
        """
        Get your SKU if linked to your product catalog
        """
        return self.your_product.your_sku if self.your_product else ''


class DealerProductListingHistory(models.Model):
    """
    Historical snapshots of dealer product listings for change tracking
    """
    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE,
        related_name='listing_history'
    )

    # Product snapshot
    dealer_sku = models.CharField(max_length=100)
    product_name = models.CharField(max_length=500)
    description_features = models.TextField(blank=True)
    specifications = models.TextField(blank=True)
    product_url = models.URLField(max_length=1000)

    # Timestamp
    scraped_at = models.DateTimeField(help_text="When this snapshot was taken")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dealer_product_listing_history'
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['dealer', 'dealer_sku', '-scraped_at']),
        ]
        verbose_name = 'Product Listing History'
        verbose_name_plural = 'Product Listing History'

    def __str__(self):
        return f"{self.dealer.name} - {self.dealer_sku} - {self.scraped_at}"
