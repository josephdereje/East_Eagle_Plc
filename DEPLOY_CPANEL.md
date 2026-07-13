# Deploy East Eagle PLC to cPanel

**cPanel username:** `easteag1`  
**Application name:** `easteagleplc`  
**App directory:** `/home/easteag1/easteagleplc`  
**Virtualenv:** `/home/easteag1/virtualenv/easteagleplc/3.9/`

---

## Python app settings (cPanel)

| Field | Value |
|-------|-------|
| Application name | `easteagleplc` |
| Application root | `easteagleplc` |
| Full path | `/home/easteag1/easteagleplc` |
| Application startup file | `passenger_wsgi.py` |
| Application entry point | `application` |
| Python version | 3.9 |

---

## Step 1 — Pull code from GitHub

The folder `/home/easteag1/easteagleplc` already exists (created by cPanel).  
**Do not clone** — pull into the existing folder:

```bash
cd /home/easteag1/easteagleplc

# Remove broken git if copy failed earlier
rm -rf .git

git init
git remote add origin https://github.com/josephdereje/East_Eagle_Plc.git
git fetch origin
git checkout -b main
git reset --hard origin/main
```

If remote already exists:
```bash
cd /home/easteag1/easteagleplc
git remote set-url origin https://github.com/josephdereje/East_Eagle_Plc.git
git fetch origin
git reset --hard origin/main
```

Future updates:
```bash
cd /home/easteag1/easteagleplc
git pull origin main
./deploy.sh
```

---

## Step 2 — Set environment variables

cPanel → **Setup Python App** → `easteagleplc` → **Environment variables**:

```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=paste-a-long-random-key-here
DJANGO_ALLOWED_HOSTS=easteagleplc.com,www.easteagleplc.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://easteagleplc.com,https://www.easteagleplc.com
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
SITE_URL=https://www.easteagleplc.com

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.easteagleplc.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=info@easteagleplc.com
EMAIL_HOST_PASSWORD=your-cpanel-email-password
DEFAULT_FROM_EMAIL=East Eagle Trading PLC <info@easteagleplc.com>
ADMIN_NOTIFICATION_EMAIL=info@easteagleplc.com
```

Create the mailbox first: cPanel → **Email Accounts** → add `info@easteagleplc.com`, then use that password for `EMAIL_HOST_PASSWORD`.

---

## Step 3 — Install & deploy

```bash
cd /home/easteag1/easteagleplc
source /home/easteag1/virtualenv/easteagleplc/3.9/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py loaddata sample_blogs sample_team sample_home_ads
python manage.py createsuperuser
```

**SQLite (default):** `pip install -r requirements.txt` is enough — do **not** install `requirements-mysql.txt`.

**MySQL only:** set `DB_ENGINE=mysql` in cPanel, then run `pip install -r requirements-mysql.txt` (may fail on shared hosting).

Or use the deploy script:
```bash
cd /home/easteag1/easteagleplc
chmod +x deploy.sh
./deploy.sh
python manage.py loaddata sample_blogs sample_team sample_home_ads
python manage.py createsuperuser
```

---

## Step 4 — Restart app

Either use cPanel → **Setup Python App** → `easteagleplc` → **Restart**, or run:

```bash
cd /home/easteag1/easteagleplc
touch tmp/restart.txt
```

Passenger restarts the app on the next request when `tmp/restart.txt` is touched.
(There is no `touch.py` file — the command is `touch tmp/restart.txt`.)

Visit:
- **Website:** `https://easteagleplc.com/`
- **Admin:** `https://easteagleplc.com/admin/`

---

## `.htaccess` (already configured)

```apache
PassengerAppRoot /home/easteag1/easteagleplc
PassengerPython /home/easteag1/virtualenv/easteagleplc/3.9/bin/python3.9
```

---

## Permission fix (if git pull fails)

```bash
chown -R easteag1:easteag1 /home/easteag1/easteagleplc
chmod -R u+rwX /home/easteag1/easteagleplc
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `destination path already exists` | Use `git pull` in `/home/easteag1/easteagleplc`, don't clone |
| `Permission denied` on `.git` | Run chown/chmod above, then `rm -rf .git` and pull again |
| 500 error | Check logs in app folder; verify env vars |
| `mysqlclient` build failed | Use SQLite (default) — run `pip install -r requirements.txt` only; skip `requirements-mysql.txt` |
| Static files missing | `python manage.py collectstatic --noinput` + restart |
