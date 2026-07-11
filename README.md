# East Eagle Trading PLC — Website

Futuristic animated landing page with Django backend for blog and contact management.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate

# 3. Create an admin account
python manage.py createsuperuser

# 4. (Optional) Load sample blog posts
python manage.py loaddata sample_blogs

# 5. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

## Admin Panel — http://127.0.0.1:8001/admin/

Create a superuser: `python manage.py createsuperuser`

| Section | What you can manage |
|---------|---------------------|
| **Home Ads** | Homepage slider slides (services & promotions) |
| **Blog Posts** | Create/edit/publish articles — subscribers get emailed automatically |
| **Contact Messages** | View client contact form submissions (with email) |
| **Email Subscriptions** | View/manage newsletter subscribers |

### Blog Newsletter
- When you **publish** a blog post (`is_published` checked), all active subscribers receive an email automatically.
- Use admin action **"Send newsletter email to all subscribers"** to manually re-send.
- Use **"Reset newsletter sent flag"** to allow re-sending.

### Contact Form Emails
- Client submits contact form → admin gets notification email + client gets confirmation email.
- In development, emails print to the **terminal console**.

### Email Configuration (Production)
Edit `east_eagle/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
ADMIN_NOTIFICATION_EMAIL = 'your-admin@email.com'
SITE_URL = 'https://yourdomain.com'
```

## Pages

| Page | URL | Method |
|------|-----|--------|
| Landing Page | `/` | GET |
| Blog Listing | `/blogs/` | GET |
| Blog Detail | `/blogs/<slug>/` | GET |
| Contact | `/contact/` | GET + POST |
| Admin Panel | `/admin/` | GET + POST |

## Admin Features

- **Blog Posts** — Create, edit, publish/unpublish articles
- **Contact Messages** — View submissions from the contact form, mark as read

## Project Structure

```
East_Eagle_Plc/
├── manage.py
├── requirements.txt
├── east_eagle/          # Django project settings
├── website/             # Main app (models, views, templates)
│   ├── models.py        # BlogPost, ContactMessage
│   ├── views.py         # GET/POST handlers
│   ├── forms.py         # Contact form
│   ├── admin.py         # Admin interface
│   └── templates/       # HTML templates
└── static/
    ├── css/style.css    # Brand styles + animations
    ├── js/script.js     # Particle, scroll, counter animations
    └── images/logo.svg  # Company logo
```

## Brand Colors

- Gold Primary: `#D4AF37`
- Charcoal: `#2C343B`
- Navy: `#1B2A41`
- Black: `#000000`
