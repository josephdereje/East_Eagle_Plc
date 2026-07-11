"""
Views for the East Eagle Trading PLC website.
All pages use GET; contact and subscribe forms use POST.
"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm, SubscribeForm
from .models import BlogPost, EmailSubscription, HomeAd


def index(request):
    """Landing page — GET with active home ad slider slides."""
    home_ads = HomeAd.objects.filter(is_active=True)
    return render(request, 'website/index.html', {'home_ads': home_ads})


def about(request):
    """About page — company background, mission, vision, team, structure."""
    return render(request, 'website/about.html')


def blogs(request):
    """Blog listing — GET published posts."""
    posts = BlogPost.objects.filter(is_published=True)
    subscribe_form = SubscribeForm()
    return render(request, 'website/blogs.html', {
        'posts': posts,
        'subscribe_form': subscribe_form,
    })


def blog_detail(request, slug):
    """Single blog post — GET."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'website/blog_detail.html', {'post': post})


def contact(request):
    """
    Contact page — GET displays form and company info;
    POST saves a new ContactMessage and sends email notifications.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Thank you! Your message has been sent. A confirmation email has been sent to you.',
            )
            return redirect('contact')
        messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = ContactForm()

    return render(request, 'website/contact.html', {'form': form})


def subscribe(request):
    """
    Newsletter subscription — POST only.
    Saves email and sends welcome email via signal.
    """
    if request.method != 'POST':
        return redirect('blogs')

    form = SubscribeForm(request.POST)
    next_url = request.POST.get('next', 'blogs')

    if form.is_valid():
        email = form.cleaned_data['email']
        existing = EmailSubscription.objects.filter(email=email).first()
        if existing and not existing.is_active:
            existing.is_active = True
            existing.name = form.cleaned_data.get('name', '')
            existing.save()
            messages.success(request, 'Welcome back! You have been re-subscribed to our newsletter.')
        else:
            form.save()
            messages.success(
                request,
                'Subscribed! Check your email for a welcome message. You will receive blog updates.',
            )
    else:
        for error in form.errors.get('email', form.non_field_errors()):
            messages.error(request, error)
        if 'email' not in form.errors:
            messages.error(request, 'Please enter a valid email address.')

    return redirect(next_url)
