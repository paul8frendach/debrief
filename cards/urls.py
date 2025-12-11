from django.urls import path
from . import views
from cards import messaging_views

urlpatterns = [
    # Main views
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    path('commons/', views.commons_cards, name='commons'),
    path('commons/synthesize/', views.synthesize_public_figure_card, name='synthesize_figure_card'),
    path('topic/<str:topic>/', views.topic_cards, name='topic_cards'),
    path('friends/', views.friends_feed, name='friends_feed'),
    
    # Card views
    path('card/<int:card_id>/', views.card_detail, name='card_detail'),
    path('create/', views.create_card, name='create_card'),
    path('create/wizard/', views.card_wizard, name='create_card_wizard'),
    path('surveys/', views.survey_list, name='survey_list'),
    path('survey/preview/', views.survey_card_preview, name='survey_card_preview'),
    path('survey/publish/', views.publish_survey_card, name='publish_survey_card'),
    path('survey/discard/', views.discard_survey_card, name='discard_survey_card'),
    path('api/search-facts/', views.search_facts, name='search_facts'),
    path('api/enhanced-fact-search/', views.enhanced_fact_search, name='enhanced_fact_search'),
    path('survey/edit/', views.edit_survey_card, name='edit_survey_card'),
    path('survey/<str:topic>/', views.topic_survey, name='topic_survey'),
    path('survey/<str:topic>/process/', views.process_survey, name='process_survey'),
    path('create-with-forms/', views.create_card_with_forms, name='create_card_forms'),
    path('card/<int:card_id>/edit-forms/', views.edit_card_with_forms, name='edit_card_forms'),
    path('card/<int:card_id>/history/', views.card_history, name='card_history'),
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
    # Friend Requests
    path('friend-request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friend-requests/', views.pending_friend_requests, name='friend_requests'),
    path('find-friends/', views.find_friends, name='find_friends'),

    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notification-count/', views.get_notification_count, name='notification_count'),
    
    # Save/Bookmark cards
    path('card/<int:card_id>/save/', views.save_card, name='save_card'),
    path('card/<int:card_id>/unsave/', views.unsave_card, name='unsave_card'),
    path('saved/', views.saved_cards, name='saved_cards'),
    path('card/<int:card_id>/share-message/', views.share_card_message, name='share_card_message'),
    path('card/<int:card_id>/savers/', views.card_savers, name='card_savers'),
    
    # Direct Messages
    
    # User Settings
    path('settings/', views.user_settings, name='user_settings'),
    path('notebook/', views.notebook, name='notebook'),
    path('quick-save/', views.quick_save, name='quick_save'),
    path('notebook/add/', views.add_notebook_entry, name='add_notebook_entry'),
    path('notebook/<int:entry_id>/delete/', views.delete_notebook_entry, name='delete_notebook_entry'),
    path('notebook/<int:entry_id>/', views.notebook_entry_detail, name='notebook_entry_detail'),
    path('notebook/<int:entry_id>/regenerate/', views.regenerate_summary, name='regenerate_summary'),
    path('notebook/<int:entry_id>/update-topic/', views.update_entry_topic, name='update_entry_topic'),
    path('notebook/<int:entry_id>/update-notes/', views.update_entry_notes, name='update_entry_notes'),
    path('notebook/<int:entry_id>/add-note/', views.add_notebook_note, name='add_notebook_note'),
    path('notebook/note/<int:note_id>/edit/', views.edit_notebook_note, name='edit_notebook_note'),
    path('notebook/note/<int:note_id>/delete/', views.delete_notebook_note, name='delete_notebook_note'),

    # Messages (New Conversation System)
    path('conversations/', messaging_views.conversations_list, name='conversations_list'),
    path('conversations/<int:conversation_id>/', messaging_views.conversation_detail, name='conversation_detail'),
    path('conversations/start/', messaging_views.start_conversation, name='start_conversation'),
    path('conversations/<int:conversation_id>/delete/', messaging_views.delete_conversation, name='delete_conversation'),
    
    # Legacy redirects for old messaging URLs
    path('inbox/', views.redirect_to_conversations),
    path('sent/', views.redirect_to_conversations),
    path('compose/', views.redirect_compose_to_conversations),
    path('compose/<str:recipient_username>/', views.redirect_compose_to_conversations),

    # API Endpoints
    path('api/notification-count/', views.get_notification_count, name='notification_count'),
    path('api/message-count/', views.get_unread_message_count, name='message_count'),
    path('api/friend-request-count/', views.get_friend_request_count, name='friend_request_count'),
    path('api/search-friends/', views.search_friends, name='search_friends'),
]
