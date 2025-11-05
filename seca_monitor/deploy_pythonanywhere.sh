#!/bin/bash
#
# Seca Monitor - PythonAnywhere One-Command Deployment Script
# For $5/month Hacker Plan with MySQL
#
# Usage: bash deploy_pythonanywhere.sh
#

set -e  # Exit on error

echo "=========================================="
echo "Seca Monitor - PythonAnywhere Deployment"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Get PythonAnywhere username
echo ""
print_info "Step 1: Getting your PythonAnywhere username..."
PA_USERNAME=$(whoami)
print_success "Detected username: $PA_USERNAME"

# Confirm username
echo ""
read -p "Is this correct? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    read -p "Enter your PythonAnywhere username: " PA_USERNAME
fi

# Get database password
echo ""
print_info "Step 2: MySQL Database Configuration"
echo "You should have created a MySQL database in the PythonAnywhere 'Databases' tab."
echo "Database name should be: ${PA_USERNAME}\$seca_monitor"
echo ""
read -sp "Enter your MySQL password: " DB_PASSWORD
echo ""

# Get GitHub token
echo ""
print_info "Step 3: GitHub Authentication"
echo "GitHub requires a Personal Access Token (PAT) for cloning repositories."
echo ""
print_warning "If you don't have a token yet:"
echo "  1. Visit: https://github.com/settings/tokens/new"
echo "  2. Select scope: 'repo' (Full control of private repositories)"
echo "  3. Generate token and copy it"
echo "  4. See GITHUB_TOKEN_SETUP.md for detailed instructions"
echo ""
read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

# Validate token
if [ -z "$GITHUB_TOKEN" ]; then
    print_error "GitHub token is required for deployment."
    echo ""
    echo "Please create a token at: https://github.com/settings/tokens/new"
    echo "Then run this script again."
    exit 1
fi

# Get GitHub repo URL
echo ""
print_info "Step 4: Repository Information"
echo "Default repo: https://github.com/landmorris/My-First-Project.git"
read -p "Press Enter to use default or enter custom repo URL: " REPO_URL_BASE
if [ -z "$REPO_URL_BASE" ]; then
    REPO_URL_BASE="https://github.com/landmorris/My-First-Project.git"
fi

# Inject token into URL (extract just the github.com/user/repo.git part)
REPO_PATH=$(echo "$REPO_URL_BASE" | sed 's|https://||' | sed 's|http://||')
REPO_URL="https://${GITHUB_TOKEN}@${REPO_PATH}"

# Get branch name
echo ""
read -p "Enter branch name (default: claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP): " BRANCH_NAME
if [ -z "$BRANCH_NAME" ]; then
    BRANCH_NAME="claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP"
fi

# Confirm settings
echo ""
echo "=========================================="
echo "Deployment Configuration:"
echo "=========================================="
echo "Username: $PA_USERNAME"
echo "Database: ${PA_USERNAME}\$seca_monitor"
echo "Repository: $REPO_URL_BASE"
echo "Branch: $BRANCH_NAME"
echo "GitHub Token: [hidden for security]"
echo "=========================================="
echo ""
read -p "Proceed with deployment? (y/n): " proceed
if [ "$proceed" != "y" ]; then
    print_error "Deployment cancelled."
    exit 1
fi

echo ""
print_info "Starting deployment..."
echo ""

# Navigate to home directory
cd ~

# Clone repository
print_info "Cloning repository..."
if [ -d "My-First-Project" ]; then
    print_warning "Directory exists. Removing old installation..."
    rm -rf My-First-Project
fi
git clone "$REPO_URL"
cd My-First-Project
git checkout "$BRANCH_NAME"
print_success "Repository cloned"

# Navigate to project
cd seca_monitor

# Create virtual environment
print_info "Creating virtual environment..."
python3.10 -m venv venv
print_success "Virtual environment created"

# Activate virtual environment and install dependencies
print_info "Installing dependencies (this may take a few minutes)..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Dependencies installed"

# Install Playwright
print_info "Installing Playwright and Chromium browser (this may take 5-10 minutes)..."
pip install playwright
playwright install chromium
print_success "Playwright installed"

# Generate secret key
print_info "Generating Django secret key..."
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
print_success "Secret key generated"

# Create .env file
print_info "Creating environment configuration..."
cat > .env << EOF
# Production Settings
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=${PA_USERNAME}.pythonanywhere.com

# Database Configuration (MySQL)
DB_NAME=${PA_USERNAME}\$seca_monitor
DB_USER=$PA_USERNAME
DB_PASSWORD=$DB_PASSWORD
DB_HOST=${PA_USERNAME}.mysql.pythonanywhere-services.com
DB_PORT=3306

# Scraper Settings
SCRAPER_HEADLESS=True
SCRAPER_TIMEOUT=30000
SCRAPER_DELAY=2
EOF
print_success "Environment configured"

# Run migrations
print_info "Running database migrations..."
python manage.py migrate
print_success "Migrations completed"

# Create superuser
print_info "Creating superuser account..."
echo ""
echo "Please enter superuser credentials:"
python manage.py createsuperuser
print_success "Superuser created"

# Create sample data
print_info "Creating sample data..."
python manage.py shell << 'PYEOF'
from scrapers.models import Dealer, YourProduct

# Create Henry Schein dealer
if not Dealer.objects.filter(name='Henry Schein').exists():
    Dealer.objects.create(
        name='Henry Schein',
        website='https://www.henryschein.com',
        spider_class='HenryScheinSpider',
        is_active=True
    )
    print('Created Henry Schein dealer')

# Create sample products
sample_products = [
    ('SECA001', 'Seca 220 Scale', 'SECA-220'),
    ('SECA002', 'Seca 360 Wireless Printer', 'SECA-360'),
    ('SECA003', 'Seca 813 High Capacity Digital Scale', 'SECA-813'),
]

for sku, name, mpn in sample_products:
    if not YourProduct.objects.filter(your_sku=sku).exists():
        YourProduct.objects.create(your_sku=sku, product_name=name, mpn=mpn)
        print(f'Created product: {sku}')

print('Sample data created!')
PYEOF
print_success "Sample data loaded"

# Collect static files
print_info "Collecting static files..."
python manage.py collectstatic --noinput
print_success "Static files collected"

# Create WSGI configuration
print_info "Creating WSGI configuration..."
WSGI_FILE=~/My-First-Project/seca_monitor/config/pythonanywhere_wsgi.py
cat > $WSGI_FILE << 'WSGIEOF'
import os
import sys

# Add project directory to path
path = '/home/USERNAME/My-First-Project/seca_monitor'
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
WSGIEOF

# Replace USERNAME placeholder
sed -i "s/USERNAME/$PA_USERNAME/g" $WSGI_FILE
print_success "WSGI configuration created"

# Deactivate virtual environment
deactivate

echo ""
echo "=========================================="
print_success "Deployment Complete!"
echo "=========================================="
echo ""
print_info "Next Steps:"
echo ""
echo "1. Go to PythonAnywhere Web tab: https://www.pythonanywhere.com/user/$PA_USERNAME/webapps/"
echo ""
echo "2. If you don't have a web app yet:"
echo "   - Click 'Add a new web app'"
echo "   - Choose 'Manual configuration'"
echo "   - Select 'Python 3.10'"
echo ""
echo "3. Configure your web app:"
echo ""
echo "   A. WSGI Configuration File:"
echo "      - Click on WSGI configuration file link"
echo "      - Delete all contents"
echo "      - Copy contents from: ~/My-First-Project/seca_monitor/config/pythonanywhere_wsgi.py"
echo "      - Save"
echo ""
echo "   B. Virtualenv:"
echo "      - Enter: /home/$PA_USERNAME/My-First-Project/seca_monitor/venv"
echo ""
echo "   C. Static Files:"
echo "      URL: /static/"
echo "      Directory: /home/$PA_USERNAME/My-First-Project/seca_monitor/staticfiles"
echo ""
echo "4. Click the green 'Reload' button"
echo ""
echo "5. Visit your site: https://$PA_USERNAME.pythonanywhere.com"
echo ""
echo "=========================================="
echo "Login Credentials:"
echo "=========================================="
echo "Dashboard Password: Archer"
echo "Admin URL: https://$PA_USERNAME.pythonanywhere.com/admin/"
echo "Admin Username: (the superuser you just created)"
echo "=========================================="
echo ""
print_success "Happy monitoring! 🎉"
echo ""
