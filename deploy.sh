#!/bin/bash
# Run this on your cPanel server after uploading the project.
set -e

APP_DIR="${APP_DIR:-$HOME/easteagleplc}"
VENV_DIR="${VENV_DIR:-$HOME/virtualenv/easteagleplc/3.11}"

cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

echo ""
echo "Done. Next steps:"
echo "  1. Set environment variables in cPanel → Setup Python App"
echo "  2. Run: python manage.py createsuperuser"
echo "  3. Restart the Python app in cPanel"
echo "  4. Visit https://yourdomain.com/"
