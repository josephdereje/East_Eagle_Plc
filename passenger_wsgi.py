"""
cPanel / Passenger entry point for East Eagle Trading PLC.
Application name: easteagleplc
Point your Python App "Application startup file" to this file.
"""
import os
import sys

# Project root on the server
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easteagleplc.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
