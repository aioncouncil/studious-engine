#!/usr/bin/env python
"""
Simple test script to verify Django server functionality.
"""
import os
import sys
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.urls import path
from django.core.management import execute_from_command_line

# Configure minimal settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-key',
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=['*'],
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
        ],
    )

# Define a simple view
def hello_world(request):
    return HttpResponse("<h1>Hello, World! This is a test Django server.</h1>")

# Define URL patterns
urlpatterns = [
    path('', hello_world),
]

# Set up the application
application = get_wsgi_application()

if __name__ == '__main__':
    print("Starting test Django server on port 9000...")
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:9000']
    execute_from_command_line(sys.argv) 