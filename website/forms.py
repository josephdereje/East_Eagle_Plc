"""
Forms for client-facing POST endpoints.
"""
from django import forms

from .models import ContactMessage, EmailSubscription


class ContactForm(forms.ModelForm):
    """Contact form validated on POST before saving to database."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your@email.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+251 ...',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'How can we help?',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Tell us about your project or inquiry...',
                'rows': 5,
                'required': True,
            }),
        }


class SubscribeForm(forms.ModelForm):
    """Newsletter subscription form — POST to receive blog updates by email."""

    class Meta:
        model = EmailSubscription
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input subscribe-input',
                'placeholder': 'your@email.com',
                'required': True,
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input subscribe-input',
                'placeholder': 'Your name (optional)',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        existing = EmailSubscription.objects.filter(email=email).first()
        if existing and existing.is_active:
            raise forms.ValidationError('This email is already subscribed.')
        return email
