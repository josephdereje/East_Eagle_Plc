#!/bin/bash
# cPanel deploy — env vars already set in Setup Python App
# App: /home/easteag1/easteagleplc
set -e

APP_DIR="${APP_DIR:-/home/easteag1/easteagleplc}"
VENV_DIR="${VENV_DIR:-/home/easteag1/virtualenv/easteagleplc/3.9}"
SITE_URL="${SITE_URL:-https://www.easteagleplc.com}"
CSS_MARKER="${CSS_MARKER:-nav-drawer-list}"

cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

echo "==> Virtualenv: $VENV_DIR"
echo "==> App dir:    $APP_DIR"

# Only reinstall packages on first setup (INSTALL_DEPS=1 ./deploy.sh)
if [[ "${INSTALL_DEPS:-}" == "1" ]]; then
  echo "==> Installing requirements..."
  pip install -r requirements.txt
  if [[ "${DB_ENGINE:-}" == "mysql" ]]; then
    pip install -r requirements-mysql.txt
  fi
fi

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Refreshing static files (CSS/JS/images)..."
echo "    Source: static/css/style.css"
if [[ -f static/css/style.css ]]; then
  echo "    Source size: $(wc -c < static/css/style.css | tr -d ' ') bytes"
fi
python manage.py collectstatic --noinput --clear
if [[ -f staticfiles/css/style.css ]]; then
  echo "    Deployed: staticfiles/css/style.css ($(wc -c < staticfiles/css/style.css | tr -d ' ') bytes)"
else
  echo "    WARNING: staticfiles/css/style.css not found after collectstatic"
fi

mkdir -p media/blog media/team tmp
chmod 755 media media/blog media/team tmp 2>/dev/null || true
chmod 644 passenger_wsgi.py manage.py .htaccess 2>/dev/null || true

echo "==> Restarting app..."
touch tmp/restart.txt

echo ""
echo "==> Testing $SITE_URL ..."
cache_bust="?v=$(date +%s)"
failed=0

test_paths=(
  "/"
  "/about/"
  "/blogs/"
  "/contact/"
  "/static/css/style.css"
  "/static/js/script.js"
  "/admin/"
)

for path in "${test_paths[@]}"; do
  url="${SITE_URL}${path}"
  if [[ "$path" == /static/* ]]; then
    url="${url}${cache_bust}"
  fi
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 \
    -H "Cache-Control: no-cache" -H "Pragma: no-cache" "$url" || echo "000")
  if [[ "$path" == "/admin/" ]]; then
    if [[ "$code" == "200" || "$code" == "302" ]]; then
      status="OK"
    else
      status="FAIL"
      failed=1
    fi
  elif [[ "$code" == "200" ]]; then
    status="OK"
  else
    status="FAIL"
    failed=1
  fi
  echo "  $status  HTTP $code  ${path}"
done

echo ""
echo "==> Verifying live CSS is updated..."
live_css=$(curl -s --max-time 20 \
  -H "Cache-Control: no-cache" -H "Pragma: no-cache" \
  "${SITE_URL}/static/css/style.css${cache_bust}" || true)

if [[ -n "$live_css" ]] && echo "$live_css" | grep -q "$CSS_MARKER"; then
  echo "  OK   Live CSS contains latest styles ($CSS_MARKER)"
else
  echo "  FAIL Live CSS missing '$CSS_MARKER' — static may be cached"
  echo "       Run: ./update_static.sh"
  echo "       Then hard-refresh browser (Ctrl+Shift+R / clear cache on phone)"
  failed=1
fi

if [[ $failed -eq 1 ]]; then
  echo ""
  echo "Some tests failed. Try:"
  echo "  python manage.py collectstatic --noinput --clear"
  echo "  touch tmp/restart.txt"
  echo "  cPanel → Setup Python App → easteagleplc → Restart"
  exit 1
fi

echo ""
echo "Deploy complete. CSS/JS refreshed. Visit $SITE_URL"
echo "On phone: close the browser tab and reopen, or clear cache, to see new CSS."
