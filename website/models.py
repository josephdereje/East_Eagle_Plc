"""
Database models for blog posts, contact messages, home ads, team members, and email subscriptions.
"""
from django.db import models
from django.utils.text import slugify


class HomeAd(models.Model):
    """Homepage slider slide — services showcase or promotional ads (admin-managed)."""

    CATEGORY_CHOICES = [
        ('service', 'Service'),
        ('promotion', 'Promotion / Ad'),
    ]

    title = models.CharField(max_length=200, help_text='Main headline on the slide.')
    subtitle = models.CharField(max_length=200, blank=True, help_text='Short tagline below the title.')
    description = models.TextField(blank=True, help_text='Optional caption text on the slide.')
    image_url = models.URLField(help_text='Background image URL for the slide.')
    link_url = models.CharField(max_length=300, blank=True, help_text='Optional CTA link (e.g. /contact/ or #services).')
    link_text = models.CharField(max_length=80, blank=True, default='Learn More', help_text='CTA button label.')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='service')
    display_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Home Ad'
        verbose_name_plural = 'Home Ads'

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    """Blog article managed by admin, displayed to clients via GET."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text='Short summary shown on blog listing.')
    content = models.TextField()
    author = models.CharField(max_length=100, default='East Eagle Team')
    image = models.ImageField(
        upload_to='blog/',
        blank=True,
        null=True,
        help_text='Upload a cover image from your computer.',
    )
    image_url = models.URLField(
        blank=True,
        help_text='Or paste an external image URL. Upload takes priority if both are set.',
    )
    is_published = models.BooleanField(default=False, help_text='Check to publish and notify subscribers.')
    newsletter_sent = models.BooleanField(
        default=False,
        help_text='Automatically set when blog newsletter email is sent to subscribers.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def cover_image(self):
        """Cover image URL — uploaded file takes priority over external URL."""
        if self.image:
            return self.image.url
        return self.image_url or ''

    @property
    def cover_image_absolute(self):
        """Absolute cover image URL for emails and external use."""
        from django.conf import settings

        url = self.cover_image
        if url and url.startswith('/'):
            return f'{settings.SITE_URL.rstrip("/")}{url}'
        return url


class ContactMessage(models.Model):
    """Contact form submission — created via POST, reviewed in admin."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    admin_notified = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f'{self.name} — {self.subject}'


class EmailSubscription(models.Model):
    """Newsletter subscriber — receives blog updates by email."""

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Email Subscription'
        verbose_name_plural = 'Email Subscriptions'

    def __str__(self):
        return self.email


class TeamMember(models.Model):
    """Leadership / team profile — photo and bio managed via Django admin."""

    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, help_text='Job title, e.g. Chief Executive Officer')
    department = models.CharField(max_length=80, blank=True, help_text='Short label, e.g. Managing Director')
    bio = models.TextField(blank=True, help_text='Short description shown on the About page.')
    photo = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True,
        help_text='Upload a square portrait photo (recommended 400×400 or larger).',
    )
    initials = models.CharField(
        max_length=4,
        blank=True,
        help_text='Fallback initials when no photo is uploaded (e.g. CEO).',
    )
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f'{self.name} — {self.role}'

    def save(self, *args, **kwargs):
        if not self.initials and self.name:
            parts = self.name.split()
            if len(parts) >= 2:
                self.initials = (parts[0][0] + parts[-1][0]).upper()
            else:
                self.initials = self.name[:2].upper()
        super().save(*args, **kwargs)
