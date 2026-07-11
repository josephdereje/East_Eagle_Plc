"""
Database models for blog posts, contact messages, home ads, and email subscriptions.
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
    image_url = models.URLField(blank=True, help_text='Optional cover image URL.')
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
