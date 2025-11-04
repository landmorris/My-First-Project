# PythonAnywhere Deployment Walkthrough
## Seca Product Monitor - Complete Step-by-Step Guide

**Plan Required:** $5/month Hacker Plan (includes PostgreSQL)
**Time Required:** 15-20 minutes
**Skill Level:** Beginner-friendly

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [x] PythonAnywhere account ($5/month Hacker plan)
- [x] Account is verified and activated
- [x] Access to PythonAnywhere dashboard

---

## 🗄️ Part 1: Create PostgreSQL Database (5 minutes)

### Step 1: Go to Databases Tab

1. Login to PythonAnywhere: https://www.pythonanywhere.com
2. Click on the **"Databases"** tab in the top navigation
3. Scroll to the **"PostgreSQL"** section

### Step 2: Initialize PostgreSQL

If this is your first time using PostgreSQL:

1. You'll see a button **"Initialize PostgreSQL"**
2. Click it and wait for initialization (takes ~30 seconds)
3. You'll see a message: "PostgreSQL initialized"

### Step 3: Create Database

1. In the **"Create a database"** field, enter: `seca_monitor`
2. Click **"Create"**
3. You'll see your database listed as: `yourusername$seca_monitor`

### Step 4: Set PostgreSQL Password

1. Find the **"PostgreSQL password"** section
2. Enter a secure password (you'll need this later)
3. Click **"Set password"**
4. **IMPORTANT:** Save this password somewhere - you'll need it for deployment

**Example:**
```
Database name: landmorris$seca_monitor
Host: landmorris-postgres.postgres.pythonanywhere-services.com
Username: landmorris
Password: [your secure password]
```

✅ **Checkpoint:** You should now see your PostgreSQL database listed under "Databases"

---

## 💻 Part 2: Run Deployment Script (10 minutes)

### Step 1: Open Bash Console

1. Click on the **"Consoles"** tab in the top navigation
2. Click **"Bash"** to open a new Bash console
3. You'll see a terminal window

### Step 2: Download and Run Deployment Script

Copy and paste this **one command** into the console:

```bash
curl -sSL https://raw.githubusercontent.com/landmorris/My-First-Project/claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP/seca_monitor/deploy_pythonanywhere.sh | bash
```

**Alternative** (if above doesn't work):

```bash
wget https://raw.githubusercontent.com/landmorris/My-First-Project/claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP/seca_monitor/deploy_pythonanywhere.sh
bash deploy_pythonanywhere.sh
```

### Step 3: Follow Interactive Prompts

The script will ask you several questions. Here's what to enter:

#### Prompt 1: Confirm Username
```
Detected username: yourusername
Is this correct? (y/n):
```
**Answer:** Type `y` and press Enter

#### Prompt 2: PostgreSQL Password
```
Enter your PostgreSQL password:
```
**Answer:** Enter the password you set in Part 1, Step 4 (it won't show as you type)

#### Prompt 3: Repository URL
```
Press Enter to use default or enter custom repo URL:
```
**Answer:** Just press Enter (uses default)

#### Prompt 4: Branch Name
```
Enter branch name (default: claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP):
```
**Answer:** Just press Enter (uses default)

#### Prompt 5: Confirm Deployment
```
Proceed with deployment? (y/n):
```
**Answer:** Type `y` and press Enter

#### Prompt 6: Create Superuser

The script will ask you to create a superuser account for Django admin:

```
Username (leave blank to use 'landmorris'):
```
**Answer:** Press Enter or type your preferred admin username

```
Email address:
```
**Answer:** Enter your email (can be fake for testing, like `admin@example.com`)

```
Password:
```
**Answer:** Enter a secure password (minimum 8 characters)

```
Password (again):
```
**Answer:** Re-enter the same password

### Step 4: Wait for Installation

The script will now:

- ✅ Clone the repository
- ✅ Create virtual environment
- ✅ Install Python packages (~2 minutes)
- ✅ Install Playwright & Chromium browser (~5 minutes)
- ✅ Configure database
- ✅ Run migrations
- ✅ Create sample data
- ✅ Collect static files

**Total time:** 8-10 minutes

You'll see progress messages like:
```
✓ Repository cloned
✓ Virtual environment created
✓ Dependencies installed
✓ Playwright installed
...
```

### Step 5: Deployment Complete

When finished, you'll see:

```
==========================================
✓ Deployment Complete!
==========================================
```

The script will show you the next steps. **Keep this terminal open** - you'll need to copy the WSGI file path.

✅ **Checkpoint:** Script completed successfully with green checkmarks

---

## 🌐 Part 3: Configure Web App (5 minutes)

### Step 1: Go to Web Tab

1. Click on the **"Web"** tab in the top navigation
2. URL: `https://www.pythonanywhere.com/user/yourusername/webapps/`

### Step 2: Create Web App (if you don't have one)

**If you see "You don't have any web apps yet":**

1. Click **"Add a new web app"**
2. Click **"Next"** on the domain confirmation
3. Choose **"Manual configuration"**
4. Select **"Python 3.10"**
5. Click **"Next"**

**If you already have a web app:**

- You can use your existing app or delete it and create a new one

### Step 3: Configure WSGI File

1. Find the **"Code"** section on the Web tab
2. Click on the **WSGI configuration file** link (looks like `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. A code editor will open

**Delete ALL existing content in the file**

4. Go back to your Bash console from Part 2
5. Run this command to display the WSGI file:

```bash
cat ~/My-First-Project/seca_monitor/config/pythonanywhere_wsgi.py
```

6. **Copy** the entire output
7. **Paste** it into the WSGI configuration file editor
8. Click **"Save"** (button at top)

**Your WSGI file should look like this:**

```python
import os
import sys

# Add project directory to path
path = '/home/yourusername/My-First-Project/seca_monitor'
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

✅ **Checkpoint:** WSGI file saved with your configuration

### Step 4: Configure Virtual Environment

1. Scroll down to the **"Virtualenv"** section on the Web tab
2. Click **"Enter the path to a virtualenv, if desired"**
3. Enter exactly:

```
/home/yourusername/My-First-Project/seca_monitor/venv
```

**Replace `yourusername` with your actual PythonAnywhere username**

4. Click the **checkmark** ✓ to save

You should see a green message: "Virtualenv successfully set up"

✅ **Checkpoint:** Virtual environment path configured

### Step 5: Configure Static Files

1. Scroll down to the **"Static files"** section
2. Click **"Enter URL"** in the first row

**First static files entry:**

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/My-First-Project/seca_monitor/staticfiles` |

**Replace `yourusername` with your actual username**

3. Click the checkmark ✓ to save

✅ **Checkpoint:** Static files configured

### Step 6: Reload Web App

1. Scroll to the **top** of the Web tab
2. Find the big green **"Reload"** button
3. Click **"Reload yourusername.pythonanywhere.com"**
4. Wait 5-10 seconds for reload to complete

You'll see a message: "Your website has been reloaded"

✅ **Checkpoint:** Web app reloaded successfully

---

## 🎉 Part 4: Test Your Application (2 minutes)

### Step 1: Visit Your Site

Open a new browser tab and go to:

```
https://yourusername.pythonanywhere.com
```

**Replace `yourusername` with your actual PythonAnywhere username**

### Step 2: Test Password Gate

You should see a beautiful blue password modal:

1. Enter password: `Archer` (case-sensitive)
2. Click **"Access Dashboard"**
3. You should be redirected to the dashboard

✅ **Success:** Dashboard loads with stats cards and dealer table

### Step 3: Test Django Admin

Visit:

```
https://yourusername.pythonanywhere.com/admin/
```

1. Login with the superuser credentials you created in Part 2, Step 3
2. You should see the Django admin interface
3. Click on **"Dealers"** - you should see "Henry Schein"
4. Click on **"Your Products"** - you should see 3 sample products

✅ **Success:** Admin panel works and shows sample data

### Step 4: Test Scraping (Optional)

1. Go back to the dashboard
2. Click the **"Scrape"** button next to Henry Schein
3. Wait a few seconds
4. You should see a success message

**Note:** First scrape may take 30-60 seconds as Playwright initializes

---

## 🐛 Troubleshooting

### Issue: "502 Bad Gateway" or "Something went wrong"

**Solution:**

1. Go to Web tab
2. Check the **Error log** (link at bottom of page)
3. Look for the most recent error
4. Common fixes:
   - Make sure WSGI file is correctly configured
   - Verify virtualenv path is correct
   - Check that .env file has correct database credentials

### Issue: "Database connection error"

**Solution:**

1. Go to Bash console
2. Check .env file:
```bash
cat ~/My-First-Project/seca_monitor/.env
```
3. Verify database credentials match your PostgreSQL setup
4. Test database connection:
```bash
cd ~/My-First-Project/seca_monitor
source venv/bin/activate
python manage.py dbshell
```

### Issue: "Static files not loading" (no CSS styling)

**Solution:**

1. Go to Web tab
2. Verify static files mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/My-First-Project/seca_monitor/staticfiles`
3. Reload web app
4. If still not working, run:
```bash
cd ~/My-First-Project/seca_monitor
source venv/bin/activate
python manage.py collectstatic --noinput
```

### Issue: "Password gate doesn't work"

**Solution:**

Make sure you're using the correct password: `Archer` (capital A)

### Issue: Script fails during installation

**Solution:**

1. Check your internet connection
2. Make sure you're on the $5/month Hacker plan (not free tier)
3. Try running the script again:
```bash
cd ~
rm -rf My-First-Project
bash deploy_pythonanywhere.sh
```

---

## 📊 Access Information

Once deployed, here's your access info:

**Public Dashboard:**
- URL: `https://yourusername.pythonanywhere.com`
- Password: `Archer` (case-sensitive)

**Django Admin:**
- URL: `https://yourusername.pythonanywhere.com/admin/`
- Username: (the superuser you created)
- Password: (the password you set)

**Database:**
- Host: `yourusername-postgres.postgres.pythonanywhere-services.com`
- Database: `yourusername$seca_monitor`
- Username: `yourusername`
- Password: (the password you set)

---

## 🔄 Updating Your Application

To update the application after making code changes:

```bash
cd ~/My-First-Project
git pull origin claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP
cd seca_monitor
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then go to the Web tab and click **"Reload"**

---

## 📝 Next Steps

Now that your application is deployed:

1. **Import your product catalog:**
```bash
cd ~/My-First-Project/seca_monitor
source venv/bin/activate
python manage.py import_products ~/products.csv
```

2. **Add more dealers:**
   - Go to admin panel
   - Add dealers with their spider configurations

3. **Set up scheduled scraping:**
   - Go to **Tasks** tab
   - Add daily/weekly scheduled task:
```bash
cd ~/My-First-Project/seca_monitor && source venv/bin/activate && python manage.py scrape_dealer --all
```

4. **Test scraping:**
   - Click "Scrape" buttons in dashboard
   - Monitor results
   - Export to Excel

---

## 🎯 Success Criteria

You've successfully deployed when:

- ✅ Site loads at `https://yourusername.pythonanywhere.com`
- ✅ Password gate works (password: Archer)
- ✅ Dashboard displays correctly with Tailwind CSS styling
- ✅ Admin panel accessible and shows sample data
- ✅ Scraping buttons work (may show "no URLs" message - expected)
- ✅ Excel export works

---

## 💡 Tips for Success

1. **Take your time** - Read each step carefully
2. **Copy exact paths** - Replace `yourusername` with YOUR username
3. **Save passwords** - Keep database and superuser passwords safe
4. **Check error logs** - If something fails, check the error log first
5. **Ask for help** - PythonAnywhere forums are helpful

---

## 📞 Support

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **PythonAnywhere Forums:** https://www.pythonanywhere.com/forums/
- **Email Support:** help@pythonanywhere.com

---

## 🎉 Congratulations!

You now have a fully functional, publicly accessible Django application with:

- ✅ Beautiful web interface
- ✅ Full scraping capabilities
- ✅ PostgreSQL database
- ✅ Change tracking
- ✅ Excel export
- ✅ Public URL

**Your site is live at:** `https://yourusername.pythonanywhere.com`

Share it with your team! 🚀
