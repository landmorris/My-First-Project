"""
Django admin configuration for Seca Product Monitor
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Dealer, YourProduct, DealerProductListing, DealerProductListingHistory


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    """
    Admin interface for Dealer model
    """
    list_display = ['name', 'website_link', 'spider_class', 'is_active_badge', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'website']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'website', 'is_active')
        }),
        ('Spider Configuration', {
            'fields': ('spider_class',),
            'description': 'Specify the spider class to use for this dealer (e.g., HenryScheinSpider)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def website_link(self, obj):
        """Display website as clickable link"""
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website[:50])
        return '-'
    website_link.short_description = 'Website'

    def is_active_badge(self, obj):
        """Display active status as colored badge"""
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        return format_html('<span style="color: red;">● Inactive</span>')
    is_active_badge.short_description = 'Status'

    def product_count(self, obj):
        """Display count of products for this dealer"""
        return obj.listings.count()
    product_count.short_description = 'Products'


@admin.register(YourProduct)
class YourProductAdmin(admin.ModelAdmin):
    """
    Admin interface for YourProduct model (your internal catalog)
    """
    list_display = ['your_sku', 'product_name', 'mpn', 'dealer_listings_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['your_sku', 'mpn', 'product_name']
    ordering = ['your_sku']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Product Information', {
            'fields': ('your_sku', 'product_name', 'mpn')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def dealer_listings_count(self, obj):
        """Display count of dealer listings linked to this product"""
        return obj.dealer_listings.count()
    dealer_listings_count.short_description = 'Dealer Listings'


@admin.register(DealerProductListing)
class DealerProductListingAdmin(admin.ModelAdmin):
    """
    Admin interface for DealerProductListing model
    """
    list_display = [
        'dealer_sku',
        'dealer',
        'product_name_truncated',
        'mpn',
        'your_product_sku',
        'content_changed_badge',
        'scrape_timestamp'
    ]
    list_filter = ['dealer', 'content_changed', 'scrape_timestamp', 'created_at']
    search_fields = ['product_name', 'dealer_sku', 'mpn', 'your_product__your_sku']
    ordering = ['-scrape_timestamp']
    readonly_fields = [
        'scrape_timestamp',
        'previous_content_hash',
        'diff_content',
        'created_at',
        'updated_at',
        'view_product_url'
    ]
    autocomplete_fields = ['your_product']

    fieldsets = (
        ('Product Information', {
            'fields': ('dealer', 'your_product', 'product_name', 'dealer_sku', 'mpn')
        }),
        ('Content', {
            'fields': ('description_features', 'specifications')
        }),
        ('Metadata', {
            'fields': ('product_url', 'view_product_url', 'scrape_timestamp')
        }),
        ('Change Tracking', {
            'fields': ('content_changed', 'previous_content_hash', 'diff_content'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_name_truncated(self, obj):
        """Display truncated product name"""
        if len(obj.product_name) > 60:
            return obj.product_name[:60] + '...'
        return obj.product_name
    product_name_truncated.short_description = 'Product Name'

    def your_product_sku(self, obj):
        """Display your SKU if linked"""
        if obj.your_product:
            return obj.your_product.your_sku
        return '-'
    your_product_sku.short_description = 'Your SKU'

    def content_changed_badge(self, obj):
        """Display change status as colored badge"""
        if obj.content_changed:
            return format_html('<span style="background-color: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">Yes</span>')
        return format_html('<span style="background-color: #F3F4F6; color: #4B5563; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">None</span>')
    content_changed_badge.short_description = 'Changed'

    def view_product_url(self, obj):
        """Display product URL as clickable link"""
        if obj.product_url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.product_url, obj.product_url)
        return '-'
    view_product_url.short_description = 'Product URL'

    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('dealer', 'your_product')


@admin.register(DealerProductListingHistory)
class DealerProductListingHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for DealerProductListingHistory model
    """
    list_display = ['dealer_sku', 'dealer', 'product_name_truncated', 'scraped_at', 'created_at']
    list_filter = ['dealer', 'scraped_at', 'created_at']
    search_fields = ['product_name', 'dealer_sku']
    ordering = ['-scraped_at']
    readonly_fields = ['dealer', 'dealer_sku', 'product_name', 'description_features', 'specifications', 'product_url', 'scraped_at', 'created_at']

    fieldsets = (
        ('Product Snapshot', {
            'fields': ('dealer', 'dealer_sku', 'product_name')
        }),
        ('Content', {
            'fields': ('description_features', 'specifications')
        }),
        ('Metadata', {
            'fields': ('product_url', 'scraped_at', 'created_at')
        }),
    )

    def product_name_truncated(self, obj):
        """Display truncated product name"""
        if len(obj.product_name) > 60:
            return obj.product_name[:60] + '...'
        return obj.product_name
    product_name_truncated.short_description = 'Product Name'

    def has_add_permission(self, request):
        """Disable manual addition - history is auto-created"""
        return False

    def has_change_permission(self, request, obj=None):
        """Make history read-only"""
        return False

    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('dealer')


# Customize admin site headers
admin.site.site_header = "Seca Product Monitor Administration"
admin.site.site_title = "Seca Monitor Admin"
admin.site.index_title = "Welcome to Seca Product Monitor Administration"
