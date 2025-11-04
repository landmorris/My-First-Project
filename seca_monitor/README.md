# Seca Product Monitor

A Django web application for monitoring dealer product listings with quality control tracking across multiple dealer partner websites.

## Features

- 🔍 **Automated Scraping**: Playwright-based web scraping with BeautifulSoup
- 📊 **Modern Dashboard**: Clean, responsive interface with Tailwind CSS
- 🔄 **Change Detection**: Automatic diff tracking to identify content changes
- 📁 **Excel Export**: Export listings with customizable column order
- 🔐 **Password Protection**: Simple password gate for internal use
- 🏢 **Multi-Dealer Support**: Extensible spider architecture for multiple dealers
- ⚡ **On-Demand Scraping**: Manual trigger via dashboard or management commands

## Project Structure

```
seca_monitor/
├── manage.py
├── config/                     # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scrapers/                   # Main Django app
│   ├── models.py               # Dealer, Product, Listing models
│   ├── views.py                # Dashboard and API views
│   ├── urls.py
│   ├── admin.py                # Django admin configuration
│   ├── middleware.py           # Password gate middleware
│   ├── management/commands/    # Management commands
│   │   ├── scrape_dealer.py
│   │   └── import_products.py
│   ├── spiders/                # Dealer-specific scrapers
│   │   ├── base_spider.py      # Base spider class
│   │   ├── henryschein_spider.py
│   │   └── dealer*_spider.py   # Placeholder spiders
│   ├── utils/
│   │   ├── export.py           # Excel export utilities
│   │   └── diff_checker.py     # Change detection
│   └── templates/              # HTML templates
│       ├── password_gate.html
│       ├── dashboard.html
│       ├── dealer_detail.html
│       └── product_detail.html
├── exports/                    # Generated Excel files
└── requirements.txt
```

## Installation

### 1. Clone and Setup

```bash
cd seca_monitor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

### 3. Database Setup

Create PostgreSQL database:

```bash
createdb seca_monitor
```

Or use your existing PostgreSQL instance.

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=seca_monitor
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (for Django Admin)

```bash
python manage.py createsuperuser
```

### 7. Import Your Product Catalog (Optional)

Create a CSV file with your products:

```csv
your_sku,product_name,mpn
SKU001,Product Name 1,MPN001
SKU002,Product Name 2,MPN002
```

Import:

```bash
python manage.py import_products products.csv
```

### 8. Configure Dealers

Access Django admin at `http://localhost:8000/admin/` and add dealers:

- Name: Henry Schein
- Website: https://www.henryschein.com
- Spider Class: `HenryScheinSpider`
- Is Active: ✓

## Usage

### Start Development Server

```bash
python manage.py runserver
```

Access at: `http://localhost:8000`

**Password**: `Archer` (case-sensitive)

### Manual Scraping

#### Via Dashboard

1. Go to dashboard
2. Click "Scrape All Dealers" or individual "Scrape" buttons

#### Via Command Line

```bash
# Scrape all dealers
python manage.py scrape_dealer --all

# Scrape specific dealer
python manage.py scrape_dealer --dealer henryschein
python manage.py scrape_dealer --dealer-id 1

# Scrape specific URLs
python manage.py scrape_dealer --dealer henryschein --urls https://example.com/product1 https://example.com/product2
```

### Export to Excel

Click "Export" in navigation or visit:
```
http://localhost:8000/export/excel/
```

Export includes all filtered results with columns:
- Dealer_Name
- Your_SKU
- Dealer_SKU
- Dealer_Listing_Name
- Dealer_Listing_Description
- Dealer_Listing_Specifications
- Date_Last_Scraped
- Diff (Yes/None)
- Diff_Content_Change
- Product_URL

## Adding New Dealers

### 1. Create Spider Class

Copy `dealer2_spider.py` and customize selectors:

```python
# scrapers/spiders/newdealer_spider.py

class NewDealerSpider(BaseSpider):
    async def scrape_product_detail(self, url):
        html_content = await self.navigate_to_url(url)
        soup = self.parse_html(html_content)

        # Customize selectors for this dealer's website
        product_data = {
            'product_name': self._extract_text(soup, '.dealer-product-name'),
            'dealer_sku': self._extract_text(soup, '.dealer-sku'),
            # ...
        }

        return self.save_to_django(product_data)
```

### 2. Register in Models

Edit `scrapers/models.py`:

```python
def get_spider_instance(self):
    from scrapers.spiders.newdealer_spider import NewDealerSpider

    spider_classes = {
        'HenryScheinSpider': HenryScheinSpider,
        'NewDealerSpider': NewDealerSpider,  # Add here
        # ...
    }
```

### 3. Add Dealer in Admin

- Name: New Dealer
- Website: https://newdealer.com
- Spider Class: `NewDealerSpider`
- Is Active: ✓

## Change Detection

The system automatically:

1. Generates MD5 hash of product content
2. Compares with previous scrape
3. Marks products with `content_changed = True`
4. Saves historical snapshots
5. Displays diff summary in dashboard

## Password Protection

- Password: **Archer** (case-sensitive)
- Session-based (expires when browser closes)
- No user database required
- Simple middleware implementation

To change password, edit `scrapers/middleware.py`:

```python
self.password = "YourNewPassword"
```

## Django Admin

Access at `/admin/` with superuser credentials.

Manage:
- Dealers
- Your Products
- Product Listings
- Listing History

## Deployment

See `DEPLOYMENT.md` for PythonAnywhere deployment instructions.

## Troubleshooting

### Playwright Issues

```bash
# Reinstall browsers
playwright install chromium --force

# Check installation
playwright --version
```

### Database Connection

```bash
# Test PostgreSQL connection
psql -U postgres -d seca_monitor

# Check Django database config
python manage.py dbshell
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Technology Stack

- **Backend**: Django 4.2
- **Database**: PostgreSQL
- **Scraping**: Playwright + BeautifulSoup
- **Frontend**: Tailwind CSS + Font Awesome
- **Export**: openpyxl
- **Server**: Gunicorn (production)

## License

Internal use only - Proprietary

## Support

For issues or questions, contact the development team.
