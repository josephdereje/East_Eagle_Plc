"""
Django signals — auto-send emails on subscription, contact, and blog publish.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .emails import (
    send_blog_newsletter,
    send_contact_confirmation,
    send_contact_notification,
    send_subscription_welcome,
)
from .models import BlogPost, ContactMessage, EmailSubscription


@receiver(post_save, sender=EmailSubscription)
def on_subscription_created(sender, instance, created, **kwargs):
    """Send welcome email when a new subscriber signs up."""
    if created and instance.is_active:
        send_subscription_welcome(instance)


@receiver(post_save, sender=ContactMessage)
def on_contact_message_created(sender, instance, created, **kwargs):
    """Notify admin and confirm receipt when a contact form is submitted."""
    if created:
        send_contact_notification(instance)
        send_contact_confirmation(instance)
        ContactMessage.objects.filter(pk=instance.pk).update(admin_notified=True)


@receiver(post_save, sender=BlogPost)
def on_blog_post_saved(sender, instance, created, **kwargs):
    """
    When a blog post is published and newsletter not yet sent,
    email all active subscribers automatically.
    """
    if instance.is_published and not instance.newsletter_sent:
        subscribers = EmailSubscription.objects.filter(is_active=True)
        if subscribers.exists():
            send_blog_newsletter(instance, subscribers)
            BlogPost.objects.filter(pk=instance.pk).update(newsletter_sent=True)
