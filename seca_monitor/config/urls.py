"""
URL configuration for Seca Monitor project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scrapers.urls')),
]

# Customize admin site
admin.site.site_header = "Seca Product Monitor Admin"
admin.site.site_title = "Seca Monitor"
admin.site.index_title = "Welcome to Seca Product Monitor Administration"
