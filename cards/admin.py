from django.contrib import admin
from .models import Conversation,  Card, Argument, Source, Follow, Notification, SavedCard, UserSettings, DirectMessage, FriendRequest


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
    list_display = ['sender', 'recipient', 'conversation', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'message']

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['participant1', 'participant2', 'card', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participant1__username', 'participant2__username']
