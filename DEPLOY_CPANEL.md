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

Static/CSS/JS only:

```bash
cd /home/easteag1/easteagleplc
git pull origin main
./update_static.sh
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

## Step 3 — Deploy (env already set in cPanel)

Environment variables and Python packages are already configured in cPanel.  
For routine updates you only need to **pull code**, **source the venv**, **update static**, **restart**, and **test**.

### One command (recommended)

```bash
cd /home/easteag1/easteagleplc
git pull origin main
chmod +x deploy.sh update_static.sh
./deploy.sh
```

`deploy.sh` does:
1. `source /home/easteag1/virtualenv/easteagleplc/3.9/bin/activate`
2. `python manage.py migrate --noinput`
3. `python manage.py collectstatic --noinput`
4. `touch tmp/restart.txt`
5. Smoke-test pages + static files on `https://www.easteagleplc.com`

### Static files only (CSS/JS/images changed)

```bash
cd /home/easteag1/easteagleplc
source /home/easteag1/virtualenv/easteagleplc/3.9/bin/activate
chmod +x update_static.sh
./update_static.sh
```

Or run manually:

```bash
cd /home/easteag1/easteagleplc
source /home/easteag1/virtualenv/easteagleplc/3.9/bin/activate
python manage.py collectstatic --noinput
touch tmp/restart.txt
curl -s -o /dev/null -w "CSS: %{http_code}\n" https://www.easteagleplc.com/static/css/style.css
curl -s -o /dev/null -w "JS:  %{http_code}\n" https://www.easteagleplc.com/static/js/script.js
```

### First-time setup only (install packages + sample data)

```bash
cd /home/easteag1/easteagleplc
source /home/easteag1/virtualenv/easteagleplc/3.9/bin/activate
INSTALL_DEPS=1 ./deploy.sh
python manage.py loaddata sample_blogs sample_team sample_home_ads
python manage.py createsuperuser
```

---

## Step 4 — Restart & test

`deploy.sh` and `update_static.sh` both run `touch tmp/restart.txt` automatically.

Manual restart if needed:

```bash
cd /home/easteag1/easteagleplc
touch tmp/restart.txt
```

Or: cPanel → **Setup Python App** → `easteagleplc` → **Restart**.

Tests run automatically in `./deploy.sh`. Override site URL:

```bash
SITE_URL=https://www.easteagleplc.com ./deploy.sh
```
- **Website:** `https://www.easteagleplc.com/`
- **Admin:** `https://www.easteagleplc.com/admin/`

---

## Fix “Site can’t be reached” (DNS & SSL)

If some visitors cannot open the site, check these in **cPanel**:

### 1. DNS records

**Zone Editor** → `easteagleplc.com`:

| Type | Name | Value |
|------|------|-------|
| A | `@` | Your server IP (e.g. `91.204.209.28`) |
| CNAME | `www` | `easteagleplc.com` |

Use your hosting provider’s nameservers (cPanel → **Domains**). Broken custom nameservers cause “site can’t be reached” for many users.

### 2. SSL certificate (important)

The wildcard cert `*.easteagleplc.com` covers **www** only — **not** `easteagleplc.com` without www.

cPanel → **SSL/TLS Status** → **Run AutoSSL** and ensure the certificate lists **both**:
- `easteagleplc.com`
- `www.easteagleplc.com`

Until apex SSL is fixed, `.htaccess` redirects **http** visitors to `https://www.easteagleplc.com`. Users who type `https://easteagleplc.com` still need the apex cert from AutoSSL.

### 3. Redeploy after git pull

```bash
cd /home/easteag1/easteagleplc
git pull origin main
./deploy.sh
```

Checks: `/` `/about/` `/blogs/` `/contact/` `/static/css/style.css` `/static/js/script.js` `/admin/`

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
| `no such column: website_blogpost.image` on `/blogs/` | Run `python manage.py migrate --noinput` then `touch tmp/restart.txt` |
| Blog page shows Django debug error page | Set `DJANGO_DEBUG=False` in cPanel env vars, then restart |
| **403 Forbidden** (LiteSpeed page) | Restart Python app in cPanel; run `./deploy.sh`; check **Setup Python App** is **Running** |
| **Site can't be reached / timeout** | Run AutoSSL for www; share `https://www.easteagleplc.com`; run `touch tmp/restart.txt` |
| App slow or times out after idle | `.htaccess` uses `PassengerMinInstances 1` — pull latest and restart |
