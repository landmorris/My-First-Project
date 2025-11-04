"""
Views for Seca Product Monitor
"""
import asyncio
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Count
from django.core.management import call_command
from django.utils import timezone
from .models import Dealer, YourProduct, DealerProductListing
from .utils.export import export_to_excel

logger = logging.getLogger('scrapers')


# ============================================================================
# AUTHENTICATION
# ============================================================================

@require_POST
def authenticate(request):
    """
    Handle password authentication
    """
    password = request.POST.get('password', '')

    if password == "Archer":  # Case-sensitive comparison
        request.session['authenticated'] = True
        return redirect('dashboard')
    else:
        request.session['auth_error'] = True
        return redirect('dashboard')  # Will show password gate with error


def logout_view(request):
    """
    Logout user by clearing session
    """
    request.session.flush()
    return redirect('dashboard')


# ============================================================================
# DASHBOARD VIEWS
# ============================================================================

def dashboard(request):
    """
    Main dashboard view with overview stats and dealer table
    """
    # Get query parameters for filtering
    search = request.GET.get('search', '')
    dealer_filter = request.GET.get('dealer', '')
    changes_filter = request.GET.get('changes', '')

    # Base queryset
    listings = DealerProductListing.objects.select_related('dealer', 'your_product')

    # Apply filters
    if search:
        listings = listings.filter(
            Q(product_name__icontains=search) |
            Q(dealer_sku__icontains=search) |
            Q(mpn__icontains=search) |
            Q(your_product__your_sku__icontains=search)
        )

    if dealer_filter:
        listings = listings.filter(dealer_id=dealer_filter)

    if changes_filter == 'yes':
        listings = listings.filter(content_changed=True)
    elif changes_filter == 'none':
        listings = listings.filter(content_changed=False)

    # Order by most recent scrapes
    listings = listings.order_by('-scrape_timestamp')[:100]  # Limit to 100 for performance

    # Statistics
    total_products = DealerProductListing.objects.count()
    total_dealers = Dealer.objects.filter(is_active=True).count()
    recent_changes = DealerProductListing.objects.filter(content_changed=True).count()

    # Last scrape time
    last_scrape = DealerProductListing.objects.order_by('-scrape_timestamp').first()
    last_scrape_time = last_scrape.scrape_timestamp if last_scrape else None

    # Dealer list for filters and overview
    dealers = Dealer.objects.annotate(
        product_count=Count('listings')
    ).filter(is_active=True)

    context = {
        'listings': listings,
        'dealers': dealers,
        'total_products': total_products,
        'total_dealers': total_dealers,
        'recent_changes': recent_changes,
        'last_scrape_time': last_scrape_time,
        'search': search,
        'dealer_filter': dealer_filter,
        'changes_filter': changes_filter,
    }

    return render(request, 'dashboard.html', context)


def dealer_detail(request, dealer_id):
    """
    Dealer-specific view showing all products from that dealer
    """
    dealer = get_object_or_404(Dealer, id=dealer_id)

    # Get query parameters
    search = request.GET.get('search', '')
    changes_filter = request.GET.get('changes', '')

    # Get listings for this dealer
    listings = DealerProductListing.objects.filter(dealer=dealer).select_related('your_product')

    # Apply filters
    if search:
        listings = listings.filter(
            Q(product_name__icontains=search) |
            Q(dealer_sku__icontains=search) |
            Q(mpn__icontains=search)
        )

    if changes_filter == 'yes':
        listings = listings.filter(content_changed=True)
    elif changes_filter == 'none':
        listings = listings.filter(content_changed=False)

    listings = listings.order_by('-scrape_timestamp')

    # Statistics for this dealer
    total_products = listings.count()
    changed_products = listings.filter(content_changed=True).count()
    last_scrape = listings.first()

    context = {
        'dealer': dealer,
        'listings': listings,
        'total_products': total_products,
        'changed_products': changed_products,
        'last_scrape': last_scrape,
        'search': search,
        'changes_filter': changes_filter,
    }

    return render(request, 'dealer_detail.html', context)


def product_detail(request, listing_id):
    """
    Individual product detail view
    """
    listing = get_object_or_404(
        DealerProductListing.objects.select_related('dealer', 'your_product'),
        id=listing_id
    )

    context = {
        'listing': listing,
    }

    return render(request, 'product_detail.html', context)


# ============================================================================
# API ENDPOINTS FOR SCRAPING
# ============================================================================

@require_POST
def scrape_all_dealers(request):
    """
    Trigger scraping for all active dealers
    This runs asynchronously via management command
    """
    try:
        # Run scraping in background
        # Note: For production, use Celery or similar task queue
        import threading

        def run_scrape():
            call_command('scrape_dealer', '--all')

        thread = threading.Thread(target=run_scrape)
        thread.start()

        return JsonResponse({
            'success': True,
            'message': 'Scraping started for all dealers'
        })

    except Exception as e:
        logger.error(f"Failed to start scraping: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
def scrape_single_dealer(request, dealer_id):
    """
    Trigger scraping for a single dealer
    """
    try:
        dealer = get_object_or_404(Dealer, id=dealer_id)

        # Run scraping in background
        import threading

        def run_scrape():
            call_command('scrape_dealer', '--dealer-id', str(dealer.id))

        thread = threading.Thread(target=run_scrape)
        thread.start()

        return JsonResponse({
            'success': True,
            'message': f'Scraping started for {dealer.name}'
        })

    except Exception as e:
        logger.error(f"Failed to start scraping for dealer {dealer_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
def refresh_product(request, listing_id):
    """
    Refresh a single product listing
    """
    try:
        listing = get_object_or_404(DealerProductListing, id=listing_id)

        # Run scraping in background for this specific product
        import threading

        def run_scrape():
            spider = listing.dealer.get_spider_instance()
            asyncio.run(spider.run(product_urls=[listing.product_url]))

        thread = threading.Thread(target=run_scrape)
        thread.start()

        return JsonResponse({
            'success': True,
            'message': f'Refreshing product {listing.dealer_sku}'
        })

    except Exception as e:
        logger.error(f"Failed to refresh product {listing_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# EXPORT
# ============================================================================

@require_GET
def export_excel(request):
    """
    Export all listings to Excel file
    """
    try:
        # Get query parameters for filtering (same as dashboard)
        search = request.GET.get('search', '')
        dealer_filter = request.GET.get('dealer', '')
        changes_filter = request.GET.get('changes', '')

        # Base queryset
        listings = DealerProductListing.objects.select_related('dealer', 'your_product')

        # Apply same filters as dashboard
        if search:
            listings = listings.filter(
                Q(product_name__icontains=search) |
                Q(dealer_sku__icontains=search) |
                Q(mpn__icontains=search)
            )

        if dealer_filter:
            listings = listings.filter(dealer_id=dealer_filter)

        if changes_filter == 'yes':
            listings = listings.filter(content_changed=True)
        elif changes_filter == 'none':
            listings = listings.filter(content_changed=False)

        listings = listings.order_by('dealer__name', 'dealer_sku')

        # Generate Excel file
        excel_file = export_to_excel(listings)

        # Return as download
        response = HttpResponse(
            excel_file,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'seca_monitor_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        logger.error(f"Failed to export Excel: {str(e)}")
        return HttpResponse(f"Error generating Excel file: {str(e)}", status=500)
