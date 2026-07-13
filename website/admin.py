"""
Admin interface for East Eagle Trading PLC website management.
Manage: Home Ads (slider), Blog Posts, Team Members, Contact Messages, Email Subscriptions.
"""
from django.contrib import admin
from django.utils.html import format_html

from .emails import send_blog_newsletter
from .models import BlogPost, ContactMessage, EmailSubscription, HomeAd, TeamMember


# Customise admin branding
admin.site.site_header = 'East Eagle Trading PLC — Admin'
admin.site.site_title = 'East Eagle Admin'
admin.site.index_title = 'Website Management Dashboard'


@admin.register(HomeAd)
class HomeAdAdmin(admin.ModelAdmin):
    """Manage homepage slider slides (services & promotional ads)."""

    list_display = ('title', 'category', 'display_order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('display_order', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Slide Content', {
            'fields': ('title', 'subtitle', 'description', 'image_url'),
            'description': 'Content shown on the homepage slider.',
        }),
        ('Call to Action', {
            'fields': ('link_url', 'link_text'),
        }),
        ('Settings', {
            'fields': ('category', 'display_order', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Upload team photos and manage leadership profiles shown on About."""

    list_display = ('name', 'role', 'department', 'display_order', 'is_active', 'photo_preview')
    list_filter = ('is_active', 'department')
    search_fields = ('name', 'role', 'department', 'bio')
    list_editable = ('display_order', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'photo_preview')
    fieldsets = (
        ('Profile', {
            'fields': ('name', 'role', 'department', 'bio', 'initials'),
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview'),
            'description': 'Upload a portrait. If empty, initials are shown instead.',
        }),
        ('Links', {
            'fields': ('email', 'linkedin_url'),
            'classes': ('collapse',),
        }),
        ('Display', {
            'fields': ('display_order', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Photo')
    def photo_preview(self, obj):
        if obj.pk and obj.photo:
            return format_html(
                '<img src="{}" alt="{}" style="width:64px;height:64px;object-fit:cover;border-radius:50%;" />',
                obj.photo.url,
                obj.name,
            )
        return '—'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Manage blog posts. Publishing sends newsletter to all subscribers."""

    list_display = ('title', 'author', 'is_published', 'newsletter_sent', 'created_at')
    list_filter = ('is_published', 'newsletter_sent', 'created_at')
    search_fields = ('title', 'content', 'author')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    readonly_fields = ('newsletter_sent', 'created_at', 'updated_at')
    actions = ['send_newsletter_action', 'reset_newsletter_flag']

    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'author', 'image_url'),
        }),
        ('Publishing', {
            'fields': ('is_published', 'newsletter_sent'),
            'description': 'When you publish a post, subscribers receive an email automatically.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.action(description='Send newsletter email to all subscribers')
    def send_newsletter_action(self, request, queryset):
        subscribers = EmailSubscription.objects.filter(is_active=True)
        total_sent = 0
        for post in queryset.filter(is_published=True):
            sent = send_blog_newsletter(post, subscribers)
            BlogPost.objects.filter(pk=post.pk).update(newsletter_sent=True)
            total_sent += sent
        self.message_user(request, f'Newsletter sent to {total_sent} subscriber(s).')

    @admin.action(description='Reset newsletter sent flag (allows re-send)')
    def reset_newsletter_flag(self, request, queryset):
        queryset.update(newsletter_sent=False)
        self.message_user(request, 'Newsletter flag reset for selected posts.')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """View contact form submissions from clients."""

    list_display = ('name', 'email', 'subject', 'is_read', 'admin_notified', 'created_at')
    list_filter = ('is_read', 'admin_notified', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'admin_notified', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(EmailSubscription)
class EmailSubscriptionAdmin(admin.ModelAdmin):
    """Manage newsletter subscribers who receive blog updates."""

    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    list_editable = ('is_active',)
    readonly_fields = ('subscribed_at',)
    actions = ['deactivate_subscribers']

    @admin.action(description='Deactivate selected subscribers')
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} subscriber(s) deactivated.')
