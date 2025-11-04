"""
Django management command for importing your product catalog from CSV
Usage:
    python manage.py import_products products.csv
"""
import csv
from django.core.management.base import BaseCommand, CommandError
from scrapers.models import YourProduct


class Command(BaseCommand):
    help = 'Import your product catalog from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file with product data'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing products (default: skip duplicates)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        update_existing = options['update']

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Validate required columns
                required_columns = ['your_sku', 'product_name']
                if not all(col in reader.fieldnames for col in required_columns):
                    raise CommandError(
                        f"CSV must contain columns: {', '.join(required_columns)}\n"
                        f"Found columns: {', '.join(reader.fieldnames)}"
                    )

                created_count = 0
                updated_count = 0
                skipped_count = 0
                error_count = 0

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        your_sku = row['your_sku'].strip()
                        product_name = row['product_name'].strip()
                        mpn = row.get('mpn', '').strip()

                        if not your_sku or not product_name:
                            self.stdout.write(
                                self.style.WARNING(f"Row {row_num}: Skipping - missing required fields")
                            )
                            skipped_count += 1
                            continue

                        if update_existing:
                            # Update or create
                            product, created = YourProduct.objects.update_or_create(
                                your_sku=your_sku,
                                defaults={
                                    'product_name': product_name,
                                    'mpn': mpn,
                                }
                            )
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                        else:
                            # Create only if doesn't exist
                            product, created = YourProduct.objects.get_or_create(
                                your_sku=your_sku,
                                defaults={
                                    'product_name': product_name,
                                    'mpn': mpn,
                                }
                            )
                            if created:
                                created_count += 1
                            else:
                                skipped_count += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Row {row_num}: Error - {str(e)}")
                        )
                        error_count += 1

                # Summary
                self.stdout.write("\n" + "=" * 60)
                self.stdout.write("IMPORT SUMMARY")
                self.stdout.write("=" * 60)
                self.stdout.write(f"Created: {created_count}")
                self.stdout.write(f"Updated: {updated_count}")
                self.stdout.write(f"Skipped: {skipped_count}")
                self.stdout.write(f"Errors: {error_count}")
                self.stdout.write("=" * 60)

                if error_count == 0:
                    self.stdout.write(self.style.SUCCESS("\n✓ Import complete!"))
                else:
                    self.stdout.write(self.style.WARNING("\n⚠ Import complete with errors"))

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {str(e)}")
