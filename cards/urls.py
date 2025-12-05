from django.urls import path
from . import views

urlpatterns = [
    # Main views
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    path('topic/<str:topic>/', views.topic_cards, name='topic_cards'),
    path('friends/', views.friends_feed, name='friends_feed'),
    
    # Card views
    path('card/<int:card_id>/', views.card_detail, name='card_detail'),
    path('create/', views.create_card, name='create_card'),
    path('create-with-forms/', views.create_card_with_forms, name='create_card_forms'),
    path('card/<int:card_id>/edit-forms/', views.edit_card_with_forms, name='edit_card_forms'),
    path('card/<int:card_id>/delete/', views.delete_card, name='delete_card'),
    path('create-with-formset/', views.create_card_with_formset, name='create_card_formset'),
    
    # Argument views
    path('card/<int:card_id>/add-argument/', views.add_argument_with_forms, name='add_argument'),
    path('argument/<int:argument_id>/edit/', views.edit_argument_with_forms, name='edit_argument'),
    path('argument/<int:argument_id>/delete/', views.delete_argument, name='delete_argument'),
    
    # Source views
    path('argument/<int:argument_id>/add-source/', views.add_source_with_forms, name='add_source'),
    
    # User dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # Follow system
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notification-count/', views.get_notification_count, name='notification_count'),
    
    # Save/Bookmark cards
    path('card/<int:card_id>/save/', views.save_card, name='save_card'),
    path('card/<int:card_id>/unsave/', views.unsave_card, name='unsave_card'),
    path('saved/', views.saved_cards, name='saved_cards'),
    path('card/<int:card_id>/savers/', views.card_savers, name='card_savers'),
    
    # Direct Messages
    path('inbox/', views.inbox, name='inbox'),
    path('messages/sent/', views.sent_messages, name='sent_messages'),
    path('messages/compose/', views.compose_message, name='compose_message'),
    path('messages/compose/<str:username>/', views.compose_message, name='compose_message_to'),
    path('messages/<int:message_id>/', views.view_message, name='view_message'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('api/message-count/', views.get_unread_message_count, name='message_count'),
    path('api/search-friends/', views.search_friends, name='search_friends'),
    
    # User Settings
    path('settings/', views.user_settings, name='user_settings'),
]