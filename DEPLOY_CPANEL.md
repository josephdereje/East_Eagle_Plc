# Deploy East Eagle PLC to cPanel

**Application name:** `easteagleplc`

This guide deploys the Django site to cPanel using **Setup Python App** (Passenger).

## What you need

- cPanel hosting with **Python 3.10+** support
- Your domain already created in cPanel (e.g. `easteagle.com`)
- SSH or **Terminal** access in cPanel (recommended)

---

## Step 1 — Upload the project

**Option A — Git (recommended)**

1. In cPanel → **Git Version Control** → Clone:
   ```
   https://github.com/josephdereje/East_Eagle_Plc.git
   ```
2. Clone into a folder **outside** `public_html`, named **`easteagleplc`**:
   ```
   /home/youruser/easteagleplc
   ```

**Option B — ZIP upload**

1. Zip the project on your Mac (exclude `.venv`, `db.sqlite3`, `__pycache__`)
2. cPanel → **File Manager** → upload to `/home/youruser/easteagleplc`
3. Extract the ZIP

Your folder should contain:
```
easteagleplc/
├── manage.py
├── passenger_wsgi.py
├── requirements.txt
├── east_eagle/
├── website/
└── static/
```

---

## Step 2 — Create Python application

1. cPanel → **Setup Python App** → **Create Application**
2. Use these settings:

| Field | Value |
|-------|-------|
| Application name | `easteagleplc` |
| Python version | 3.10 or 3.11 |
| Application root | `easteagleplc` |
| Application URL | your domain (or `/`) |
| Application startup file | `passenger_wsgi.py` |
| Application entry point | `application` |

3. Click **Create**

cPanel creates a virtualenv like:
```
/home/youruser/virtualenv/easteagleplc/3.11/
```

---

## Step 3 — Set environment variables

In **Setup Python App** → your app → **Environment variables**, add:

```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=paste-a-long-random-key-here
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SITE_URL=https://yourdomain.com
```

Copy other values from `.env.example` (email, database, etc.).

> Generate a secret key locally:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## Step 4 — Install packages & prepare database

Open **cPanel Terminal** (or SSH) and run:

```bash
cd ~/easteagleplc

# Activate the virtualenv cPanel created (path may vary slightly)
source ~/virtualenv/easteagleplc/3.11/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py loaddata sample_blogs sample_team sample_home_ads
python manage.py createsuperuser
```

---

## Step 5 — Point your domain to the app

1. cPanel → **Domains** → select your domain
2. Set **Document Root** to the Python app folder, or use the URL mapping from Setup Python App
3. If cPanel created a `public_html` symlink, follow your host’s Django docs

Update `.htaccess` paths if needed (replace `USERNAME` with your cPanel username):

```apache
PassengerAppRoot /home/USERNAME/easteagleplc
PassengerPython /home/USERNAME/virtualenv/easteagleplc/3.11/bin/python3.11
```

---

## Step 6 — Enable SSL (HTTPS)

1. cPanel → **SSL/TLS Status** → run **AutoSSL** for your domain
2. After SSL is active, keep these env vars:
   ```
   DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   SITE_URL=https://yourdomain.com
   ```

---

## Step 7 — Restart the app

cPanel → **Setup Python App** → **Restart**

Visit:
- **Website:** `https://yourdomain.com/`
- **Admin:** `https://yourdomain.com/admin/`

---

## Upload team photos (after deploy)

1. Go to `https://yourdomain.com/admin/`
2. Login with the superuser you created
3. **Team Members** → edit each person → upload photo → Save

Photos are stored in `media/team/` on the server.

---

## Optional — MySQL instead of SQLite

1. cPanel → **MySQL Databases** → create database + user
2. Add env vars:
   ```
   DB_ENGINE=mysql
   DB_NAME=youruser_easteagle
   DB_USER=youruser_easteagle
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   ```
3. Run `python manage.py migrate` again

---

## Email on cPanel

Use your hosting email SMTP:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| 500 error | Check `stderr.log` in the app folder; verify env vars and `pip install` |
| Static files missing | Run `python manage.py collectstatic --noinput` and restart app |
| Admin login fails | Run `createsuperuser` again on the server |
| CSRF error on forms | Add your `https://` domain to `DJANGO_CSRF_TRUSTED_ORIGINS` |
| Team photos not showing | Ensure `media/` folder exists and is writable (`chmod 755 media`) |
| Wrong site showing | Restart Python app; confirm domain points to correct folder |

---

## Quick deploy script (run on server)

```bash
#!/bin/bash
cd ~/easteagleplc
source ~/virtualenv/easteagleplc/3.11/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt 2>/dev/null || true
echo "Deploy complete — restart app in cPanel if needed"
```

Save as `deploy.sh`, then: `chmod +x deploy.sh && ./deploy.sh`
