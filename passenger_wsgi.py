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

# Production defaults on cPanel (env vars in Setup Python App override these)
os.environ.setdefault('DJANGO_DEBUG', 'False')
_required_hosts = (
    'localhost',
    '127.0.0.1',
    'easteagleplc.com',
    'www.easteagleplc.com',
)
_existing_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
_merged_hosts = [
    host.strip()
    for host in (_existing_hosts + ',' + ','.join(_required_hosts)).split(',')
    if host.strip()
]
os.environ['DJANGO_ALLOWED_HOSTS'] = ','.join(dict.fromkeys(_merged_hosts))

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
