"""
URL configuration for scrapers app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('authenticate/', views.authenticate, name='authenticate'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dealer/<int:dealer_id>/', views.dealer_detail, name='dealer_detail'),
    path('product/<int:listing_id>/', views.product_detail, name='product_detail'),

    # API endpoints for scraping
    path('api/scrape-all/', views.scrape_all_dealers, name='scrape_all_dealers'),
    path('api/scrape-dealer/<int:dealer_id>/', views.scrape_single_dealer, name='scrape_single_dealer'),
    path('api/refresh-product/<int:listing_id>/', views.refresh_product, name='refresh_product'),

    # Export
    path('export/excel/', views.export_excel, name='export_excel'),
]
