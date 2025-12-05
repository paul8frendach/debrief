from django.contrib import admin
from .models import Card, Argument, Source, Follow, Notification, SavedCard, UserSettings, DirectMessage


class ArgumentInline(admin.TabularInline):
    model = Argument
    extra = 1


class SourceInline(admin.TabularInline):
    model = Source
    extra = 1


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'scope', 'topic', 'visibility', 'created_at']
    list_filter = ['scope', 'topic', 'visibility', 'created_at']
    search_fields = ['title', 'hypothesis', 'user__username']
    inlines = [ArgumentInline]


@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    list_display = ['summary', 'card', 'type', 'order']
    list_filter = ['type']
    search_fields = ['summary', 'detail']
    inlines = [SourceInline]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'argument', 'url', 'author']
    search_fields = ['title', 'url', 'author']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'message', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username', 'message']


@admin.register(SavedCard)
class SavedCardAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'card__title']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'allow_messages', 'email_notifications']
    list_filter = ['allow_messages', 'email_notifications']
    search_fields = ['user__username']


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'subject', 'message']