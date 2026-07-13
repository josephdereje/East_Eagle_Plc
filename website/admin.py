"""
Admin interface for East Eagle Trading PLC website management.
Manage: Home Ads (slider), Blog Posts, Team Members, Contact Messages, Email Subscriptions.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

from .emails import send_blog_newsletter
from .models import BlogPost, ContactMessage, EmailSubscription, HomeAd, TeamMember


# Customise admin branding
admin.site.site_header = 'East Eagle Trading PLC'
admin.site.site_title = 'East Eagle Admin'
admin.site.index_title = ''
admin.site.enable_nav_sidebar = False


def _admin_dashboard_stats():
    active_slides = HomeAd.objects.filter(is_active=True).order_by('display_order', '-created_at')[:5]
    return {
        'active_slides': active_slides.count(),
        'total_slides': min(HomeAd.objects.filter(is_active=True).count(), 5),
        'published_posts': BlogPost.objects.filter(is_published=True).count(),
        'total_posts': BlogPost.objects.count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'total_messages': ContactMessage.objects.count(),
        'active_subscribers': EmailSubscription.objects.filter(is_active=True).count(),
        'active_team': TeamMember.objects.filter(is_active=True).count(),
    }


_original_admin_index = AdminSite.index


def _custom_admin_index(self, request, extra_context=None):
    extra_context = extra_context or {}
    extra_context['stats'] = _admin_dashboard_stats()
    extra_context['recent_messages'] = ContactMessage.objects.order_by('-created_at')[:5]
    return _original_admin_index(self, request, extra_context)


AdminSite.index = _custom_admin_index

# Hide default auth clutter — use CLI for user management
try:
    from django.contrib.auth.models import Group
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(HomeAd)
class HomeAdAdmin(admin.ModelAdmin):
    """Manage homepage slider slides (services & promotional ads)."""

    list_display = ('title', 'category', 'display_order', 'is_active', 'slide_preview', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('display_order', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'slide_preview_large')
    fieldsets = (
        ('Slide Content', {
            'fields': ('title', 'subtitle', 'description', 'image_url', 'slide_preview_large'),
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

    @admin.display(description='Preview')
    def slide_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" alt="{}" class="ee-slide-preview" />',
                obj.image_url,
                obj.title,
            )
        return '—'

    @admin.display(description='Slide preview')
    def slide_preview_large(self, obj):
        if obj.pk and obj.image_url:
            return format_html(
                '<img src="{}" alt="{}" class="ee-slide-preview-lg" />',
                obj.image_url,
                obj.title,
            )
        return 'Save with an image URL to see preview.'


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
