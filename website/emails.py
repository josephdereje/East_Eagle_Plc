"""
Email helpers for subscriptions, blog newsletters, and contact notifications.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def _send_html_email(subject, template_name, context, recipient_list):
    """Render an HTML email template and send to recipients."""
    html_message = render_to_string(template_name, context)
    plain_message = render_to_string(template_name.replace('.html', '.txt'), context)

    return send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def send_subscription_welcome(subscription):
    """Send welcome email after a client subscribes."""
    context = {
        'name': subscription.name or 'Subscriber',
        'email': subscription.email,
        'site_name': 'East Eagle Trading PLC',
    }
    return _send_html_email(
        subject='Welcome to East Eagle Trading PLC Newsletter',
        template_name='website/emails/subscription_welcome.html',
        context=context,
        recipient_list=[subscription.email],
    )


def send_blog_newsletter(blog_post, subscribers):
    """Send a published blog post to all active subscribers."""
    if not subscribers:
        return 0

    context = {
        'post': blog_post,
        'site_name': 'East Eagle Trading PLC',
        'blog_url': f'{settings.SITE_URL}/blogs/{blog_post.slug}/',
    }
    subject = f'New from East Eagle: {blog_post.title}'
    html_message = render_to_string('website/emails/blog_newsletter.html', context)
    plain_message = render_to_string('website/emails/blog_newsletter.txt', context)

    sent = 0
    for sub in subscribers:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.email],
            html_message=html_message,
            fail_silently=True,
        )
        sent += 1
    return sent


def send_contact_notification(contact_message):
    """Notify admin when a client submits the contact form."""
    context = {
        'message': contact_message,
        'site_name': 'East Eagle Trading PLC',
    }
    return _send_html_email(
        subject=f'New Contact Request: {contact_message.subject}',
        template_name='website/emails/contact_notification.html',
        context=context,
        recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
    )


def send_contact_confirmation(contact_message):
    """Confirm to the client that their contact message was received."""
    context = {
        'name': contact_message.name,
        'subject': contact_message.subject,
        'site_name': 'East Eagle Trading PLC',
    }
    return _send_html_email(
        subject='We received your message — East Eagle Trading PLC',
        template_name='website/emails/contact_confirmation.html',
        context=context,
        recipient_list=[contact_message.email],
    )
