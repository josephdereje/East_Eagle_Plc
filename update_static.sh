#!/bin/bash
# Refresh static CSS/JS only — env + venv already configured in cPanel
set -e

APP_DIR="${APP_DIR:-/home/easteag1/easteagleplc}"
VENV_DIR="${VENV_DIR:-/home/easteag1/virtualenv/easteagleplc/3.9}"
SITE_URL="${SITE_URL:-https://www.easteagleplc.com}"
CSS_MARKER="${CSS_MARKER:-nav-drawer-list}"

cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

echo "==> Refreshing static files..."
if [[ -f static/css/style.css ]]; then
  echo "    Source: static/css/style.css ($(wc -c < static/css/style.css | tr -d ' ') bytes)"
fi

python manage.py collectstatic --noinput --clear

if [[ -f staticfiles/css/style.css ]]; then
  echo "    Output: staticfiles/css/style.css ($(wc -c < staticfiles/css/style.css | tr -d ' ') bytes)"
fi

echo "==> Restarting app..."
mkdir -p tmp
touch tmp/restart.txt

cache_bust="?v=$(date +%s)"
echo ""
echo "==> Testing static files on $SITE_URL (cache-bypass) ..."

for path in "/static/css/style.css" "/static/js/script.js" "/static/images/logo.svg"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 \
    -H "Cache-Control: no-cache" -H "Pragma: no-cache" \
    "${SITE_URL}${path}${cache_bust}" || echo "000")
  if [[ "$code" == "200" ]]; then
    echo "  OK   HTTP $code  ${path}"
  else
    echo "  FAIL HTTP $code  ${path}"
    exit 1
  fi
done

live_css=$(curl -s --max-time 20 \
  -H "Cache-Control: no-cache" -H "Pragma: no-cache" \
  "${SITE_URL}/static/css/style.css${cache_bust}" || true)

if [[ -n "$live_css" ]] && echo "$live_css" | grep -q "$CSS_MARKER"; then
  echo "  OK   Live CSS contains latest styles ($CSS_MARKER)"
else
  echo "  FAIL Live CSS missing '$CSS_MARKER'"
  echo "       Hard-refresh browser or clear cache on phone"
  exit 1
fi

echo ""
echo "Static CSS/JS refreshed successfully."
