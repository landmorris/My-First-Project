"""
Django management command for scraping dealer products
Usage:
    python manage.py scrape_dealer --dealer henryschein
    python manage.py scrape_dealer --all
    python manage.py scrape_dealer --dealer-id 1
"""
import asyncio
from django.core.management.base import BaseCommand, CommandError
from scrapers.models import Dealer


class Command(BaseCommand):
    help = 'Scrape dealer products on-demand'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dealer',
            type=str,
            help='Dealer name (case-insensitive search)'
        )
        parser.add_argument(
            '--dealer-id',
            type=int,
            help='Specific dealer ID'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Scrape all active dealers'
        )
        parser.add_argument(
            '--urls',
            type=str,
            nargs='+',
            help='Specific product URLs to scrape (optional)'
        )

    def handle(self, *args, **options):
        # Determine which dealers to scrape
        dealers = self.get_dealers(options)

        if not dealers:
            raise CommandError('No dealers found with the given criteria')

        self.stdout.write(self.style.SUCCESS(f"Found {len(dealers)} dealer(s) to scrape"))

        # Get product URLs if provided
        product_urls = options.get('urls', None)

        # Scrape each dealer
        for dealer in dealers:
            self.stdout.write("-" * 60)
            self.stdout.write(f"Scraping: {dealer.name}")
            self.stdout.write("-" * 60)

            try:
                # Get spider instance for this dealer
                spider = dealer.get_spider_instance()

                # Run spider asynchronously
                asyncio.run(spider.run(product_urls=product_urls))

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Successfully scraped {dealer.name}")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to scrape {dealer.name}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS("\n✓ Scraping complete!"))

    def get_dealers(self, options):
        """
        Get dealers to scrape based on command options

        Args:
            options: Command options

        Returns:
            QuerySet of Dealer objects
        """
        if options['all']:
            # Scrape all active dealers
            return Dealer.objects.filter(is_active=True)

        elif options['dealer_id']:
            # Scrape specific dealer by ID
            return Dealer.objects.filter(id=options['dealer_id'])

        elif options['dealer']:
            # Scrape dealer by name (case-insensitive search)
            return Dealer.objects.filter(
                name__icontains=options['dealer'],
                is_active=True
            )

        else:
            # No criteria provided
            return Dealer.objects.none()
