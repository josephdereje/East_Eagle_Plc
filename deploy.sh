#!/bin/bash
# Run on cPanel server — app path: /home/easteag1/easteagleplc
set -e

APP_DIR="${APP_DIR:-/home/easteag1/easteagleplc}"
VENV_DIR="${VENV_DIR:-/home/easteag1/virtualenv/easteagleplc/3.9}"

cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

echo ""
echo "Done. App path: $APP_DIR"
echo "Next steps:"
echo "  1. Set environment variables in cPanel → Setup Python App"
echo "  2. Run: python manage.py createsuperuser"
echo "  3. Restart the Python app in cPanel"
echo "  4. Visit https://yourdomain.com/"
