from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Max, Count, Case, When, IntegerField
from .models import Conversation, DirectMessage, Card, UserSettings, Notification


@login_required
def conversations_list(request):
    """List all conversations for the current user"""
    # Get all conversations where user is a participant
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant2', 'card').annotate(
        unread_count=Count(
            Case(
                When(
                    messages__recipient=request.user,
                    messages__is_read=False,
                    then=1
                ),
                output_field=IntegerField()
            )
        )
    ).order_by('-updated_at')
    
    # Get total unread count
    total_unread = sum(conv.unread_count for conv in conversations)
    
    context = {
        'conversations': conversations,
        'total_unread': total_unread,
    }
    
    return render(request, 'cards/conversations.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """View a specific conversation and its messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Ensure user is a participant
    if request.user not in [conversation.participant1, conversation.participant2]:
        messages.error(request, "You don't have access to this conversation.")
        return redirect('conversations_list')
    
    # Get all messages in this conversation
    conversation_messages = conversation.messages.select_related('sender', 'recipient').order_by('created_at')
    
    # Mark messages as read with timestamp
    from django.utils import timezone
    unread_messages = conversation_messages.filter(recipient=request.user, is_read=False)
    for msg in unread_messages:
        msg.is_read = True
        msg.read_at = timezone.now()
        msg.save(update_fields=['is_read', 'read_at'])
    
    # Handle new message submission
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            other_user = conversation.participant2 if request.user == conversation.participant1 else conversation.participant1
            
            DirectMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                recipient=other_user,
                message=message_text
            )
            
            # Update conversation timestamp
            conversation.save()  # This updates updated_at
            
            # Send email notification
            from .emails import send_message_notification
            send_message_notification(conversation, message_text, request.user, other_user)
            
            return redirect('conversation_detail', conversation_id=conversation.id)
    
    # Get all conversations for sidebar
    all_conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant2', 'card').annotate(
        unread_count=Count(
            Case(
                When(
                    messages__recipient=request.user,
                    messages__is_read=False,
                    then=1
                ),
                output_field=IntegerField()
            )
        )
    ).order_by('-updated_at')
    
    other_user = conversation.participant2 if request.user == conversation.participant1 else conversation.participant1
    
    context = {
        'conversation': conversation,
        'messages': conversation_messages,
        'other_user': other_user,
        'all_conversations': all_conversations,
    }
    
    return render(request, 'cards/conversation_detail.html', context)


@login_required
def start_conversation(request):
    """Start a new conversation with a user, optionally about a card"""
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        card_id = request.POST.get('card_id')
        message_text = request.POST.get('message', '').strip()
        
        try:
            recipient = User.objects.get(username=recipient_username)
            
            # Check if recipient allows messages
            settings, created = UserSettings.objects.get_or_create(user=recipient)
            if not settings.allow_messages:
                messages.error(request, f"{recipient.username} has disabled direct messages.")
                return redirect('conversations_list')
            
            # Get card if specified
            card = None
            if card_id:
                card = Card.objects.get(id=card_id)
            
            # Find or create conversation
            # Try both orderings of participants
            conversation = Conversation.objects.filter(
                Q(participant1=request.user, participant2=recipient, card=card) |
                Q(participant1=recipient, participant2=request.user, card=card)
            ).first()
            
            if not conversation:
                conversation = Conversation.objects.create(
                    participant1=request.user,
                    participant2=recipient,
                    card=card
                )
            
            # Create message if provided
            if message_text:
                DirectMessage.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    recipient=recipient,
                    message=message_text
                )
                
                # Create notification
                Notification.objects.create(
                    recipient=recipient,
                    sender=request.user,
                    notification_type='comment',
                    card=card,
                    message=f"{request.user.username} sent you a message"
                )
            
            messages.success(request, f"Conversation started with {recipient.username}!")
            return redirect('conversation_detail', conversation_id=conversation.id)
            
        except User.DoesNotExist:
            messages.error(request, "User not found!")
        except Card.DoesNotExist:
            messages.error(request, "Card not found!")
        
        return redirect('conversations_list')
    
    # GET request - show compose form
    return redirect('conversations_list')


@login_required
def delete_conversation(request, conversation_id):
    """Delete a conversation (for the current user)"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Ensure user is a participant
    if request.user not in [conversation.participant1, conversation.participant2]:
        messages.error(request, "You don't have access to this conversation.")
        return redirect('conversations_list')
    
    # For now, actually delete the conversation
    # In production, you might want to just "hide" it for the user
    conversation.delete()
    
    messages.success(request, "Conversation deleted.")
    return redirect('conversations_list')