# PythonAnywhere Deployment Guide

Complete guide for deploying Seca Product Monitor to PythonAnywhere ($5/month plan).

## Prerequisites

- PythonAnywhere account ($5/month "Hacker" plan)
- MySQL database (available on PythonAnywhere)
- Git repository with your code

## Deployment Steps

### 1. Create PythonAnywhere Account

1. Sign up at [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Choose the **$5/month "Hacker" plan** (includes MySQL)
3. Verify your account

### 2. Setup MySQL Database

From PythonAnywhere dashboard:

1. Go to **Databases** tab
2. Create a new MySQL database
3. Note your credentials:
   - **Host**: `username-mysql.pythonanywhere-services.com`
   - **Database**: `username$seca_monitor`
   - **Username**: `username`
   - **Password**: (set your password)

### 3. Clone Your Repository

Open a **Bash console** on PythonAnywhere:

```bash
cd ~
git clone https://github.com/yourusername/seca-monitor.git
cd seca-monitor/seca_monitor
```

Or if starting fresh, upload your code using the Files tab.

### 4. Create Virtual Environment

```bash
cd ~/seca-monitor/seca_monitor
python3.11 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Install Playwright

```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Install system dependencies (may require contacting PythonAnywhere support)
playwright install-deps
```

**Note**: If `playwright install-deps` fails due to permissions, contact PythonAnywhere support to install system dependencies for Playwright.

**Alternative**: Use `SCRAPER_HEADLESS=False` locally and run scrapers from your local machine via management commands, only using PythonAnywhere for the web dashboard.

### 7. Configure Environment

Create `.env` file:

```bash
nano .env
```

Add configuration:

```
# Production Settings
DEBUG=False
SECRET_KEY=your-production-secret-key-change-this-to-random-string
ALLOWED_HOSTS=yourusername.pythonanywhere.com

# Database (from step 2)
DB_NAME=yourusername$seca_monitor
DB_USER=yourusername
DB_PASSWORD=your-database-password
DB_HOST=yourusername-mysql.pythonanywhere-services.com
DB_PORT=3306

# Scraper Settings
SCRAPER_HEADLESS=True
SCRAPER_TIMEOUT=30000
SCRAPER_DELAY=2
```

**Generate SECRET_KEY**:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 8. Run Migrations

```bash
source venv/bin/activate
cd ~/seca-monitor/seca_monitor
python manage.py migrate
```

### 9. Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

### 10. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 11. Configure Web App

From PythonAnywhere dashboard:

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.11**

### 12. Configure WSGI File

1. Click on **WSGI configuration file** link
2. Delete all content and replace with:

```python
import os
import sys

# Add project directory to path
path = '/home/yourusername/seca-monitor/seca_monitor'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Load .env file
from dotenv import load_dotenv
project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

# Initialize Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Replace `yourusername` with your actual PythonAnywhere username.**

### 13. Configure Virtual Environment

In the **Web** tab:

1. Scroll to **Virtualenv** section
2. Enter path: `/home/yourusername/seca-monitor/seca_monitor/venv`
3. Click the checkmark

### 14. Configure Static Files

In the **Web** tab, add static files mapping:

| URL           | Directory                                                      |
|---------------|----------------------------------------------------------------|
| /static/      | /home/yourusername/seca-monitor/seca_monitor/staticfiles      |

### 15. Reload Web App

Click the green **Reload** button at the top of the Web tab.

### 16. Test Your Application

Visit: `https://yourusername.pythonanywhere.com`

You should see the password gate. Enter password: **Archer**

### 17. Import Your Product Catalog

From Bash console:

```bash
cd ~/seca-monitor/seca_monitor
source venv/bin/activate

# Upload products.csv to PythonAnywhere first via Files tab
python manage.py import_products ~/products.csv
```

### 18. Configure Dealers

1. Visit `https://yourusername.pythonanywhere.com/admin/`
2. Login with superuser credentials
3. Add dealers with their spider configurations

## Running Scrapers on PythonAnywhere

### Option 1: Via Dashboard (Recommended)

1. Visit your dashboard
2. Click "Scrape All Dealers" or individual scraper buttons
3. Monitor via logs

### Option 2: Via Bash Console

```bash
cd ~/seca-monitor/seca_monitor
source venv/bin/activate

# Scrape all dealers
python manage.py scrape_dealer --all

# Scrape specific dealer
python manage.py scrape_dealer --dealer henryschein
```

### Option 3: Scheduled Tasks

PythonAnywhere Hacker plan includes scheduled tasks:

1. Go to **Tasks** tab
2. Add daily/weekly task:
   ```bash
   cd ~/seca-monitor/seca_monitor && source venv/bin/activate && python manage.py scrape_dealer --all
   ```

## Troubleshooting

### Playwright Issues on PythonAnywhere

PythonAnywhere may have restrictions on Playwright system dependencies.

**Solutions**:

1. **Contact Support**: Ask PythonAnywhere to install Playwright system dependencies
2. **Hybrid Approach**: Run scrapers locally, use PythonAnywhere only for dashboard
3. **Alternative Scrapers**: Use `requests` + BeautifulSoup for static sites

### Database Connection Errors

Verify `.env` settings match PythonAnywhere database credentials:

```bash
# Test connection
python manage.py dbshell
```

### Static Files Not Loading

```bash
# Recollect static files
python manage.py collectstatic --noinput

# Verify static files mapping in Web tab
```

### 500 Internal Server Error

Check error logs:

1. Go to **Web** tab
2. Scroll to **Log files**
3. Check **Error log** and **Server log**

Enable debug temporarily:

```python
# In .env
DEBUG=True
```

**Remember to set `DEBUG=False` after fixing!**

### Import Errors

Ensure virtual environment is activated:

```bash
source ~/seca-monitor/seca_monitor/venv/bin/activate
which python  # Should show venv path
```

Reinstall dependencies:

```bash
pip install -r requirements.txt --force-reinstall
```

## Maintenance

### Update Code

```bash
cd ~/seca-monitor
git pull origin main
cd seca_monitor
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then reload web app from **Web** tab.

### Backup Database

```bash
# Create backup
pg_dump -h yourusername-mysql.pythonanywhere-services.com -U yourusername yourusername$seca_monitor > backup.sql

# Restore backup
psql -h yourusername-mysql.pythonanywhere-services.com -U yourusername yourusername$seca_monitor < backup.sql
```

### Monitor Logs

```bash
# View scraper logs
tail -f ~/seca-monitor/seca_monitor/scraper.log

# View web logs (from Web tab in dashboard)
```

### Clear Old Data

```bash
cd ~/seca-monitor/seca_monitor
source venv/bin/activate

# Django shell
python manage.py shell
```

```python
from scrapers.models import DealerProductListingHistory
from datetime import datetime, timedelta

# Delete history older than 90 days
cutoff = datetime.now() - timedelta(days=90)
DealerProductListingHistory.objects.filter(scraped_at__lt=cutoff).delete()
```

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (random string)
- [ ] Database password is secure
- [ ] `.env` file is not in version control
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] Password gate is active (Archer)

## Performance Tips

1. **Limit Concurrent Scrapers**: Run one dealer at a time
2. **Use Delays**: Keep `SCRAPER_DELAY=2` to avoid rate limiting
3. **Database Indexes**: Already configured in models
4. **Static File CDN**: Not needed for small internal tool
5. **Query Optimization**: Use `select_related()` in views (already implemented)

## Cost Breakdown

**PythonAnywhere Hacker Plan**: $5/month includes:
- 1 web app
- MySQL database
- 1GB disk space
- Scheduled tasks
- Always-on web app

**Total**: $5/month (no additional costs)

## Support

- **PythonAnywhere Help**: help@pythonanywhere.com
- **Documentation**: https://help.pythonanywhere.com/

## Hybrid Deployment Option

If Playwright doesn't work on PythonAnywhere:

1. **PythonAnywhere**: Host dashboard only (web interface)
2. **Local Machine**: Run scrapers via management commands
3. **Shared Database**: Both connect to PythonAnywhere MySQL

This gives you full Playwright capabilities locally while maintaining the web dashboard on PythonAnywhere.

## Alternative: DigitalOcean/AWS

For full Playwright support, consider:

- **DigitalOcean Droplet**: $6/month
- **AWS EC2 t3.micro**: ~$10/month
- **Heroku**: ~$7/month

These provide full system access for Playwright dependencies.
