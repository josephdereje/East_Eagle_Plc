#!/bin/bash
# cPanel deploy — env vars already set in Setup Python App
# App: /home/easteag1/easteagleplc
set -e

APP_DIR="${APP_DIR:-/home/easteag1/easteagleplc}"
VENV_DIR="${VENV_DIR:-/home/easteag1/virtualenv/easteagleplc/3.9}"
SITE_URL="${SITE_URL:-https://www.easteagleplc.com}"

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

echo "==> Updating static files..."
python manage.py collectstatic --noinput

mkdir -p media/blog media/team tmp
chmod 755 media media/blog media/team tmp 2>/dev/null || true
chmod 644 passenger_wsgi.py manage.py .htaccess 2>/dev/null || true

echo "==> Restarting app..."
touch tmp/restart.txt

echo ""
echo "==> Testing $SITE_URL ..."
test_paths=(
  "/"
  "/about/"
  "/blogs/"
  "/contact/"
  "/static/css/style.css"
  "/static/js/script.js"
  "/admin/"
)
failed=0
for path in "${test_paths[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "${SITE_URL}${path}" || echo "000")
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

if [[ $failed -eq 1 ]]; then
  echo ""
  echo "Some tests failed. Try:"
  echo "  touch tmp/restart.txt"
  echo "  cPanel → Setup Python App → easteagleplc → Restart"
  exit 1
fi

echo ""
echo "Deploy complete. Visit $SITE_URL"
