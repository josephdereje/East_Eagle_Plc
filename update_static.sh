#!/bin/bash
# Update static files only — env + venv already configured in cPanel
set -e

APP_DIR="${APP_DIR:-/home/easteag1/easteagleplc}"
VENV_DIR="${VENV_DIR:-/home/easteag1/virtualenv/easteagleplc/3.9}"
SITE_URL="${SITE_URL:-https://www.easteagleplc.com}"

cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Restarting app..."
mkdir -p tmp
touch tmp/restart.txt

echo ""
echo "==> Testing static files on $SITE_URL ..."
for path in "/static/css/style.css" "/static/js/script.js" "/static/images/logo.svg"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "${SITE_URL}${path}" || echo "000")
  if [[ "$code" == "200" ]]; then
    echo "  OK   HTTP $code  ${path}"
  else
    echo "  FAIL HTTP $code  ${path}"
    exit 1
  fi
done

echo ""
echo "Static files updated."
