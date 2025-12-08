from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_friend_request_email(friend_request):
    """Send email when user receives a friend request"""
    to_user = friend_request.to_user
    from_user = friend_request.from_user
    
    # Check if user wants email notifications
    if hasattr(to_user, 'settings') and to_user.settings.email_on_friend_request and to_user.email:
        subject = f"New friend request from {from_user.username} on Debrief"
        
        message = f"""
Hi {to_user.username},

{from_user.username} sent you a friend request on Debrief!

Accept or decline the request here:
{settings.SITE_URL}/friend-requests/

Best,
The Debrief Team
"""
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [to_user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send friend request email: {e}")


def send_friend_accepted_email(friend_request):
    """Send email when friend request is accepted"""
    from_user = friend_request.from_user
    to_user = friend_request.to_user
    
    # Notify the original requester
    if hasattr(from_user, 'settings') and from_user.settings.email_on_friend_request and from_user.email:
        subject = f"{to_user.username} accepted your friend request on Debrief"
        
        message = f"""
Hi {from_user.username},

Great news! {to_user.username} accepted your friend request on Debrief.

You can now see each other's cards and send direct messages.

View their profile:
{settings.SITE_URL}/profile/{to_user.username}/

Best,
The Debrief Team
"""
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [from_user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send friend accepted email: {e}")


def send_friend_card_notification(card, followers):
    """Send email to friends when user creates a new card"""
    card_user = card.user
    
    for follower in followers:
        # Check if follower wants email notifications
        if hasattr(follower, 'settings') and follower.settings.email_on_friend_card and follower.email:
            subject = f"{card_user.username} created a new argument card on Debrief"
            
            message = f"""
Hi {follower.username},

Your friend {card_user.username} just created a new argument card: "{card.title}"

Topic: {card.get_topic_display()}
Stance: {card.stance.upper()}

View the card here:
{settings.SITE_URL}/card/{card.id}/

Best,
The Debrief Team
"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [follower.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send card notification email to {follower.username}: {e}")


def send_card_saved_notification(saved_card):
    """Send email when someone saves your card"""
    card = saved_card.card
    card_owner = card.user
    saver = saved_card.user
    
    # Check if card owner wants notifications
    if hasattr(card_owner, 'settings') and card_owner.settings.email_notifications and card_owner.email:
        visibility_text = "publicly" if saved_card.visibility == "public" else "privately"
        
        subject = f"{saver.username} saved your card on Debrief"
        
        message = f"""
Hi {card_owner.username},

{saver.username} saved your argument card {visibility_text}: "{card.title}"

View your card:
{settings.SITE_URL}/card/{card.id}/

Best,
The Debrief Team
"""
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [card_owner.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send card saved email: {e}")


def send_message_notification(conversation, message_text, sender, recipient):
    """Send email when user receives a direct message"""
    
    # Check if user wants email notifications
    if hasattr(recipient, 'settings') and recipient.settings.email_on_message and recipient.email:
        card_info = ""
        if conversation.card:
            card_info = f"\n\nAbout the card: {conversation.card.title}"
        
        subject = f"New message from {sender.username} on Debrief"
        
        message_email = f"""
Hi {recipient.username},

{sender.username} sent you a message on Debrief!{card_info}

Message preview: {message_text[:100]}{'...' if len(message_text) > 100 else ''}

View and reply here:
{settings.SITE_URL}/conversations/{conversation.id}/

Best,
The Debrief Team
"""
        
        try:
            send_mail(
                subject,
                message_email,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send message notification email: {e}")


def send_card_shared_notification(conversation, card, sender, recipient):
    """Send email when someone shares a card with you"""
    
    # Check if user wants email notifications
    if hasattr(recipient, 'settings') and recipient.settings.email_on_message and recipient.email:
        subject = f"{sender.username} shared an argument card with you on Debrief"
        
        message = f"""
Hi {recipient.username},

{sender.username} shared an argument card with you: "{card.title}"

Topic: {card.get_topic_display()}
Stance: {card.stance.upper()}

View the card and reply here:
{settings.SITE_URL}/conversations/{conversation.id}/

Best,
The Debrief Team
"""
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send card shared email: {e}")
            