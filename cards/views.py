from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Card, Argument, Source, Follow, Notification, SavedCard, UserSettings, DirectMessage
from .forms import CardForm, ArgumentForm, SourceForm, ArgumentFormSet
from datetime import timedelta
from django.utils import timezone


def index(request):
    """Homepage showing public cards"""
    cards = Card.objects.filter(visibility='public').order_by('-created_at')[:10]
    return render(request, 'cards/index.html', {'cards': cards})


def card_detail(request, card_id):
    """Detail view for a single card"""
    card = get_object_or_404(Card, id=card_id)
    
    # Check permissions for private/friends cards
    if card.visibility == 'private' and card.user != request.user:
        messages.error(request, "This card is private.")
        return redirect('index')
    
    if card.visibility == 'friends':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to view this card.")
            return redirect('account_login')
        
        is_following = Follow.objects.filter(
            follower=request.user,
            following=card.user
        ).exists()
        
        if not is_following and card.user != request.user:
            messages.error(request, "This card is only visible to friends.")
            return redirect('index')
    
    pros = card.arguments.filter(type='pro')
    cons = card.arguments.filter(type='con')
    
    # Check if current user has saved this card
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedCard.objects.filter(user=request.user, card=card).exists()
    
    return render(request, 'cards/card_detail.html', {
        'card': card,
        'pros': pros,
        'cons': cons,
        'is_saved': is_saved,
    })


@login_required
def create_card(request):
    """Create a new card with enhanced argument structure"""
    if request.method == 'POST':
        # Create the card
        card = Card.objects.create(
            user=request.user,
            scope=request.POST.get('scope', 'federal'),
            topic=request.POST['topic'],
            subcategory=request.POST.get('subcategory', ''),
            title=request.POST['card_name'],
            stance=request.POST.get('stance', 'Analyzing'),
            hypothesis=request.POST['hypothesis'],
            conclusion=request.POST['conclusion'],
            visibility=request.POST.get('visibility', 'private')
        )
        
        # Add pros with enhanced structure
        pro_names = request.POST.getlist('pro_name[]')
        pro_summaries = request.POST.getlist('pro_summary[]')
        pro_sources = request.POST.getlist('pro_sources[]')
        
        for i, summary in enumerate(pro_summaries):
            if summary.strip():
                name = pro_names[i] if i < len(pro_names) else 'Supporting Point'
                sources = pro_sources[i] if i < len(pro_sources) else ''
                
                full_summary = f"{name}: {summary}" if name else summary
                
                Argument.objects.create(
                    card=card,
                    type='pro',
                    summary=full_summary,
                    detail=f"Sources: {sources}" if sources else "",
                    order=i
                )
        
        # Add cons with enhanced structure
        con_names = request.POST.getlist('con_name[]')
        con_summaries = request.POST.getlist('con_summary[]')
        con_sources = request.POST.getlist('con_sources[]')
        
        for i, summary in enumerate(con_summaries):
            if summary.strip():
                name = con_names[i] if i < len(con_names) else 'Opposing Point'
                sources = con_sources[i] if i < len(con_sources) else ''
                
                full_summary = f"{name}: {summary}" if name else summary
                
                Argument.objects.create(
                    card=card,
                    type='con',
                    summary=full_summary,
                    detail=f"Sources: {sources}" if sources else "",
                    order=i
                )
        
        messages.success(request, 'Argument card created successfully!')
        return redirect('card_detail', card_id=card.id)
    
    # GET request - show form
    return render(request, 'cards/create_card.html', {
        'topics': Card.TOPIC_CHOICES
    })


@login_required
def create_card_with_forms(request):
    """Create a new card using Django Forms"""
    if request.method == 'POST':
        form = CardForm(request.POST)
        
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            
            # Add pros
            pro_summaries = request.POST.getlist('pro_summary[]')
            pro_details = request.POST.getlist('pro_detail[]')
            for i, summary in enumerate(pro_summaries):
                if summary.strip():
                    Argument.objects.create(
                        card=card,
                        type='pro',
                        summary=summary,
                        detail=pro_details[i] if i < len(pro_details) else '',
                        order=i
                    )
            
            # Add cons
            con_summaries = request.POST.getlist('con_summary[]')
            con_details = request.POST.getlist('con_detail[]')
            for i, summary in enumerate(con_summaries):
                if summary.strip():
                    Argument.objects.create(
                        card=card,
                        type='con',
                        summary=summary,
                        detail=con_details[i] if i < len(con_details) else '',
                        order=i
                    )
            
            messages.success(request, 'Card created successfully!')
            return redirect('card_detail', card_id=card.id)
    else:
        form = CardForm()
    
    return render(request, 'cards/create_card_forms.html', {
        'form': form,
    })


@login_required
def edit_card_with_forms(request, card_id):
    """Edit an existing card using Django Forms"""
    card = get_object_or_404(Card, id=card_id)
    
    if card.user != request.user:
        messages.error(request, "You don't have permission to edit this card.")
        return redirect('card_detail', card_id=card.id)
    
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Card updated successfully!')
            return redirect('card_detail', card_id=card.id)
    else:
        form = CardForm(instance=card)
    
    pros = card.arguments.filter(type='pro')
    cons = card.arguments.filter(type='con')
    
    return render(request, 'cards/edit_card_forms.html', {
        'form': form,
        'card': card,
        'pros': pros,
        'cons': cons,
    })


@login_required
def add_argument_with_forms(request, card_id):
    """Add an argument to a card using Django Forms"""
    card = get_object_or_404(Card, id=card_id)
    
    if request.method == 'POST':
        form = ArgumentForm(request.POST)
        
        if form.is_valid():
            argument = form.save(commit=False)
            argument.card = card
            argument.save()
            
            messages.success(request, f'{argument.get_type_display()} argument added successfully!')
            return redirect('card_detail', card_id=card.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ArgumentForm()
    
    return render(request, 'cards/add_argument.html', {
        'form': form,
        'card': card,
    })


@login_required
def edit_argument_with_forms(request, argument_id):
    """Edit an existing argument using Django Forms"""
    argument = get_object_or_404(Argument, id=argument_id)
    card = argument.card
    
    if card.user != request.user:
        messages.error(request, "You don't have permission to edit this argument.")
        return redirect('card_detail', card_id=card.id)
    
    if request.method == 'POST':
        form = ArgumentForm(request.POST, instance=argument)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Argument updated successfully!')
            return redirect('card_detail', card_id=card.id)
    else:
        form = ArgumentForm(instance=argument)
    
    return render(request, 'cards/edit_argument.html', {
        'form': form,
        'argument': argument,
        'card': card,
    })


@login_required
def delete_argument(request, argument_id):
    """Delete an argument"""
    argument = get_object_or_404(Argument, id=argument_id)
    card = argument.card
    
    if card.user != request.user:
        messages.error(request, "You don't have permission to delete this argument.")
        return redirect('card_detail', card_id=card.id)
    
    if request.method == 'POST':
        argument.delete()
        messages.success(request, 'Argument deleted successfully!')
        return redirect('card_detail', card_id=card.id)
    
    return render(request, 'cards/confirm_delete_argument.html', {
        'argument': argument,
        'card': card,
    })


@login_required
def add_source_with_forms(request, argument_id):
    """Add a source to an argument using Django Forms"""
    argument = get_object_or_404(Argument, id=argument_id)
    card = argument.card
    
    if card.user != request.user:
        messages.error(request, "You don't have permission to add sources to this argument.")
        return redirect('card_detail', card_id=card.id)
    
    if request.method == 'POST':
        form = SourceForm(request.POST)
        
        if form.is_valid():
            source = form.save(commit=False)
            source.argument = argument
            source.save()
            
            messages.success(request, 'Source added successfully!')
            return redirect('card_detail', card_id=card.id)
    else:
        form = SourceForm()
    
    return render(request, 'cards/add_source.html', {
        'form': form,
        'argument': argument,
        'card': card,
    })


@login_required
def user_dashboard(request):
    """Display user's own cards with stats and filters"""
    # Get filter parameter
    scope_filter = request.GET.get('scope', 'all')
    
    # Base queryset
    user_cards = Card.objects.filter(user=request.user)
    
    # Apply scope filter
    if scope_filter == 'federal':
        user_cards = user_cards.filter(scope='federal')
    elif scope_filter == 'state':
        user_cards = user_cards.filter(scope='state')
    
    user_cards = user_cards.order_by('-created_at')
    
    # Calculate stats
    total_cards = Card.objects.filter(user=request.user).count()
    followers_count = request.user.followers.count()
    following_count = request.user.following.count()
    total_saves = SavedCard.objects.filter(card__user=request.user).count()
    
    # Count by scope
    federal_count = Card.objects.filter(user=request.user, scope='federal').count()
    state_count = Card.objects.filter(user=request.user, scope='state').count()
    
    context = {
        'cards': user_cards,
        'total_cards': total_cards,
        'followers_count': followers_count,
        'following_count': following_count,
        'total_saves': total_saves,
        'federal_count': federal_count,
        'state_count': state_count,
        'scope_filter': scope_filter,
    }
    
    return render(request, 'cards/user_dashboard.html', context)


@login_required
def delete_card(request, card_id):
    """Delete a card"""
    card = get_object_or_404(Card, id=card_id)
    
    if card.user != request.user:
        messages.error(request, "You don't have permission to delete this card.")
        return redirect('card_detail', card_id=card.id)
    
    if request.method == 'POST':
        card.delete()
        messages.success(request, 'Card deleted successfully!')
        return redirect('user_dashboard')
    
    return render(request, 'cards/confirm_delete_card.html', {
        'card': card,
    })


@login_required
def create_card_with_formset(request):
    """Create a card with inline argument formsets"""
    if request.method == 'POST':
        card_form = CardForm(request.POST)
        argument_formset = ArgumentFormSet(request.POST)
        
        if card_form.is_valid() and argument_formset.is_valid():
            card = card_form.save(commit=False)
            card.user = request.user
            card.save()
            
            arguments = argument_formset.save(commit=False)
            for argument in arguments:
                argument.card = card
                argument.save()
            
            messages.success(request, 'Card created successfully with all arguments!')
            return redirect('card_detail', card_id=card.id)
    else:
        card_form = CardForm()
        argument_formset = ArgumentFormSet()
    
    return render(request, 'cards/create_card_formset.html', {
        'card_form': card_form,
        'argument_formset': argument_formset,
    })


@login_required
def follow_user(request, user_id):
    """Follow a user"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    if user_to_follow == request.user:
        messages.error(request, "You cannot follow yourself!")
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    
    if created:
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notification_type='follow',
            message=f"{request.user.username} started following you"
        )
    
    messages.success(request, f"You are now following {user_to_follow.username}!")
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def unfollow_user(request, user_id):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    messages.success(request, f"You unfollowed {user_to_unfollow.username}.")
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def user_profile(request, username):
    """View a user's profile"""
    profile_user = get_object_or_404(User, username=username)
    user_cards = Card.objects.filter(user=profile_user, visibility='public').order_by('-created_at')
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
    
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    
    # Check if user allows messages
    allows_messages = True
    if request.user.is_authenticated:
        settings, created = UserSettings.objects.get_or_create(user=profile_user)
        allows_messages = settings.allow_messages
    
    context = {
        'profile_user': profile_user,
        'cards': user_cards,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'allows_messages': allows_messages,
    }
    
    return render(request, 'cards/user_profile.html', context)


def explore(request):
    """Explore page showing recent cards and active users with search"""
    from django.db.models import Count, Q
    
    search_query = request.GET.get('q', '').strip()
    
    if search_query:
        recent_cards = Card.objects.filter(
            Q(visibility='public') &
            (Q(title__icontains=search_query) | 
             Q(hypothesis__icontains=search_query) |
             Q(subcategory__icontains=search_query) |
             Q(user__username__icontains=search_query))
        ).order_by('-created_at')[:12]
        
        active_users = User.objects.filter(
            username__icontains=search_query
        ).annotate(
            card_count=Count('cards')
        ).order_by('-card_count')[:8]
        
        popular_users = User.objects.filter(
            username__icontains=search_query
        ).annotate(
            follower_count=Count('followers')
        ).order_by('-follower_count')[:8]
    else:
        recent_cards = Card.objects.filter(visibility='public').order_by('-created_at')[:12]
        
        active_users = User.objects.annotate(
            card_count=Count('cards')
        ).filter(card_count__gt=0).order_by('-card_count')[:8]
        
        popular_users = User.objects.annotate(
            follower_count=Count('followers')
        ).filter(follower_count__gt=0).order_by('-follower_count')[:8]
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trending_topics = Card.objects.filter(
        visibility='public',
        created_at__gte=thirty_days_ago
    ).values('topic').annotate(
        card_count=Count('id')
    ).order_by('-card_count')[:3]
    
    trending_topics_data = []
    for topic_data in trending_topics:
        topic_code = topic_data['topic']
        topic_display = dict(Card.TOPIC_CHOICES).get(topic_code, topic_code)
        trending_topics_data.append({
            'code': topic_code,
            'display': topic_display,
            'count': topic_data['card_count']
        })
    
    context = {
        'recent_cards': recent_cards,
        'active_users': active_users,
        'popular_users': popular_users,
        'search_query': search_query,
        'trending_topics': trending_topics_data,
    }
    
    return render(request, 'cards/explore.html', context)


@login_required
def friends_feed(request):
    """Feed showing cards from users you follow"""
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    
    from django.db.models import Q
    friends_cards = Card.objects.filter(
        Q(user__in=following_users) & 
        (Q(visibility='public') | Q(visibility='friends'))
    ).order_by('-created_at')[:20]
    
    context = {
        'cards': friends_cards,
        'following_count': len(following_users),
    }
    
    return render(request, 'cards/friends_feed.html', context)


def topic_cards(request, topic):
    """View all cards for a specific topic"""
    topic_choices = dict(Card.TOPIC_CHOICES)
    if topic not in topic_choices:
        messages.error(request, "Invalid topic.")
        return redirect('explore')
    
    topic_display = topic_choices[topic]
    cards = Card.objects.filter(
        visibility='public',
        topic=topic
    ).order_by('-created_at')
    
    context = {
        'topic': topic,
        'topic_display': topic_display,
        'cards': cards,
    }
    
    return render(request, 'cards/topic_cards.html', context)


@login_required
def notifications(request):
    """View all notifications"""
    user_notifications = Notification.objects.filter(recipient=request.user)
    unread_count = user_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': user_notifications[:50],
        'unread_count': unread_count,
    }
    
    return render(request, 'cards/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.card:
        return redirect('card_detail', card_id=notification.card.id)
    
    return redirect('notifications')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read!')
    return redirect('notifications')


@login_required
def get_notification_count(request):
    """API endpoint to get unread notification count"""
    from django.http import JsonResponse
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def save_card(request, card_id):
    """Save/bookmark a card"""
    card = get_object_or_404(Card, id=card_id)
    
    if card.user == request.user:
        messages.error(request, "You can't save your own card!")
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    
    saved, created = SavedCard.objects.get_or_create(user=request.user, card=card)
    
    if created:
        Notification.objects.create(
            recipient=card.user,
            sender=request.user,
            notification_type='like',
            card=card,
            message=f"{request.user.username} saved your card: {card.title}"
        )
        messages.success(request, "Card saved to your collection!")
    else:
        messages.info(request, "You already saved this card!")
    
    return redirect(request.META.get('HTTP_REFERER', 'card_detail', card_id=card.id))


@login_required
def unsave_card(request, card_id):
    """Remove a saved card"""
    card = get_object_or_404(Card, id=card_id)
    SavedCard.objects.filter(user=request.user, card=card).delete()
    messages.success(request, "Card removed from your saved collection!")
    
    return redirect(request.META.get('HTTP_REFERER', 'saved_cards'))


@login_required
def saved_cards(request):
    """View all saved cards"""
    saves = SavedCard.objects.filter(user=request.user).select_related('card', 'card__user')
    
    context = {
        'saved_cards': [save.card for save in saves],
    }
    
    return render(request, 'cards/saved_cards.html', context)


@login_required
def inbox(request):
    """View all received messages"""
    messages_received = DirectMessage.objects.filter(recipient=request.user).select_related('sender')
    unread_count = messages_received.filter(is_read=False).count()
    
    context = {
        'messages': messages_received[:50],
        'unread_count': unread_count,
    }
    
    return render(request, 'cards/inbox.html', context)


@login_required
def sent_messages(request):
    """View all sent messages"""
    messages_sent = DirectMessage.objects.filter(sender=request.user).select_related('recipient')
    
    context = {
        'messages': messages_sent[:50],
    }
    
    return render(request, 'cards/sent_messages.html', context)


@login_required
def compose_message(request, username=None):
    """Compose and send a message"""
    recipient_user = None
    if username:
        recipient_user = get_object_or_404(User, username=username)
        
        settings, created = UserSettings.objects.get_or_create(user=recipient_user)
        if not settings.allow_messages:
            messages.error(request, f"{recipient_user.username} has disabled direct messages.")
            return redirect('user_profile', username=username)
    
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message')
        
        try:
            recipient = User.objects.get(username=recipient_username)
            
            settings, created = UserSettings.objects.get_or_create(user=recipient)
            if not settings.allow_messages:
                messages.error(request, f"{recipient.username} has disabled direct messages.")
                return redirect('compose_message')
            
            if recipient == request.user:
                messages.error(request, "You can't send messages to yourself!")
                return redirect('compose_message')
            
            DirectMessage.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                message=message_text
            )
            
            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type='comment',
                message=f"{request.user.username} sent you a message: {subject or 'New message'}"
            )
            
            messages.success(request, f"Message sent to {recipient.username}!")
            return redirect('sent_messages')
            
        except User.DoesNotExist:
            messages.error(request, "User not found!")
    
    context = {
        'recipient_user': recipient_user,
    }
    
    return render(request, 'cards/compose_message.html', context)


@login_required
def view_message(request, message_id):
    """View a single message"""
    message = get_object_or_404(DirectMessage, id=message_id)
    
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, "You don't have permission to view this message.")
        return redirect('inbox')
    
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    context = {
        'message': message,
    }
    
    return render(request, 'cards/view_message.html', context)


@login_required
def delete_message(request, message_id):
    """Delete a message"""
    message = get_object_or_404(DirectMessage, id=message_id)
    
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, "You don't have permission to delete this message.")
        return redirect('inbox')
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, "Message deleted!")
        return redirect('inbox')
    
    return render(request, 'cards/confirm_delete_message.html', {'message': message})


@login_required
def user_settings(request):
    """User privacy and settings"""
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        settings.allow_messages = request.POST.get('allow_messages') == 'on'
        settings.email_notifications = request.POST.get('email_notifications') == 'on'
        settings.save()
        
        messages.success(request, "Settings updated!")
        return redirect('user_settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'cards/user_settings.html', context)


@login_required
def get_unread_message_count(request):
    """API endpoint to get unread message count"""
    from django.http import JsonResponse
    count = DirectMessage.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def card_savers(request, card_id):
    """View users who saved a specific card"""
    card = get_object_or_404(Card, id=card_id)
    
    # Only card owner can see who saved it
    if card.user != request.user:
        messages.error(request, "You don't have permission to view this.")
        return redirect('card_detail', card_id=card.id)
    
    savers = SavedCard.objects.filter(card=card).select_related('user').order_by('-saved_at')
    
    context = {
        'card': card,
        'savers': savers,
    }
    
    return render(request, 'cards/card_savers.html', context)


@login_required
def card_savers(request, card_id):
    """View users who saved a specific card"""
    card = get_object_or_404(Card, id=card_id)
    
    # Only card owner can see who saved it
    if card.user != request.user:
        messages.error(request, "You don't have permission to view this.")
        return redirect('card_detail', card_id=card.id)
    
    savers = SavedCard.objects.filter(card=card).select_related('user').order_by('-saved_at')
    
    context = {
        'card': card,
        'savers': savers,
    }
    
    return render(request, 'cards/card_savers.html', context)


@login_required
def card_savers(request, card_id):
    """View users who saved a specific card"""
    card = get_object_or_404(Card, id=card_id)
    
    # Only card owner can see who saved it
    if card.user != request.user:
        messages.error(request, "You don't have permission to view this.")
        return redirect('card_detail', card_id=card.id)
    
    savers = SavedCard.objects.filter(card=card).select_related('user').order_by('-saved_at')
    
    context = {
        'card': card,
        'savers': savers,
    }
    
    return render(request, 'cards/card_savers.html', context)

@login_required
def search_friends(request):
    """API endpoint to search friends for messaging"""
    from django.http import JsonResponse
    from django.db.models import Q
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'friends': []})
    
    # Get users that current user follows
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    # Search within followed users
    friends = User.objects.filter(
        Q(id__in=following_ids) &
        Q(username__icontains=query)
    )[:10]
    
    # Get their message settings
    results = []
    for friend in friends:
        settings, created = UserSettings.objects.get_or_create(user=friend)
        results.append({
            'username': friend.username,
            'allows_messages': settings.allow_messages
        })
    
    return JsonResponse({'friends': results})