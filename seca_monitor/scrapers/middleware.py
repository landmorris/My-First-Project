"""
Password gate middleware for Seca Product Monitor
Simple shared password protection without Django auth
"""
from django.shortcuts import render, redirect
from django.urls import reverse


class PasswordGateMiddleware:
    """
    Middleware to protect entire site with shared password
    Password: "Archer" (case-sensitive)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.password = "Archer"  # Case-sensitive shared password

        # Paths that bypass authentication
        self.exempt_paths = [
            '/authenticate/',
            '/static/',
            '/admin/',  # Django admin uses its own auth
        ]

    def __call__(self, request):
        # Check if path is exempt
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)

        # Check if user is authenticated via session
        if not request.session.get('authenticated'):
            # Show password gate
            error = request.session.pop('auth_error', None)
            return render(request, 'password_gate.html', {
                'error': error
            })

        # User is authenticated, proceed normally
        response = self.get_response(request)
        return response
