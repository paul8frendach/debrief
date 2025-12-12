from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from cards.youtube_utils import extract_video_id, get_youtube_transcript, summarize_transcript
from cards.article_utils import fetch_article_text, summarize_article, is_valid_url
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Conversation, Card, Argument, Source, Follow, Notification, SavedCard, UserSettings, DirectMessage, FriendRequest, NotebookEntry, NotebookNote, TopicSurvey, SurveyQuestion, QuestionOption, PolicyFact, FactSource
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
        
        # Send email notifications to friends if card is public
        if card.visibility == 'public':
            from .emails import send_friend_card_notification
            followers = User.objects.filter(following__following=request.user)
            if followers.exists():
                send_friend_card_notification(card, followers)
        
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
    
    # Get or create user settings
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    
    context = {
        'cards': user_cards,
        'total_cards': total_cards,
        'followers_count': followers_count,
        'following_count': following_count,
        'total_saves': total_saves,
        'federal_count': federal_count,
        'state_count': state_count,
        'scope_filter': scope_filter,
        'user_settings': user_settings,
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
    
    # Get public saved cards
    public_saves = SavedCard.objects.filter(
        user=profile_user, 
        visibility='public'
    ).select_related('card', 'card__user').order_by('-saved_at')
    
    # If viewing own profile, also get private saves
    private_saves = []
    if request.user == profile_user:
        private_saves = SavedCard.objects.filter(
            user=profile_user, 
            visibility='private'
        ).select_related('card', 'card__user').order_by('-saved_at')
    
    is_following = False
    friend_request_pending = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
        
        # Check if there's a pending friend request
        friend_request_pending = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=profile_user,
            status='pending'
        ).exists()
    
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    
    # Check if user allows messages
    allows_messages = True
    if request.user.is_authenticated:
        settings, created = UserSettings.objects.get_or_create(user=profile_user)
        allows_messages = settings.allow_messages
    
    # Get follower/following counts
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    
    # Check if friends
    is_friends = False
    if request.user.is_authenticated:
        is_friends = (
            Follow.objects.filter(follower=request.user, following=profile_user).exists() and
            Follow.objects.filter(follower=profile_user, following=request.user).exists()
        )
    
    context = {
        'profile_user': profile_user,
        'user_cards': user_cards,
        'cards': user_cards,
        'public_saved_cards': public_saves,
        'private_saved_cards': [save.card for save in private_saves],
        'public_saves': public_saves,
        'private_saves': private_saves,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_friends': is_friends,
        'friend_request_pending': friend_request_pending,
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
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def save_card(request, card_id):
    """Save/bookmark a card with visibility option"""
    card = get_object_or_404(Card, id=card_id)
    
    if card.user == request.user:
        messages.error(request, "You can't save your own card!")
        return redirect('card_detail', card_id=card.id)
    
    # Check if already saved
    existing_save = SavedCard.objects.filter(user=request.user, card=card).first()
    
    if request.method == 'POST':
        visibility = request.POST.get('visibility', 'public')
        
        if existing_save:
            # Update visibility if already saved
            existing_save.visibility = visibility
            existing_save.save()
            messages.success(request, f"Card visibility updated to {visibility}!")
        else:
            # Create new save
            SavedCard.objects.create(user=request.user, card=card, visibility=visibility)
            Notification.objects.create(
                recipient=card.user,
                sender=request.user,
                notification_type='like',
                card=card,
                message=f"{request.user.username} saved your card: {card.title}"
            )
            messages.success(request, f"Card saved to your {visibility} collection!")
        
        return redirect('card_detail', card_id=card.id)
    
    # If GET request, just create with default public visibility
    if not existing_save:
        SavedCard.objects.create(user=request.user, card=card, visibility='public')
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
    
    return redirect('card_detail', card_id=card.id)


@login_required
def unsave_card(request, card_id):
    """Remove a saved card"""
    card = get_object_or_404(Card, id=card_id)
    SavedCard.objects.filter(user=request.user, card=card).delete()
    messages.success(request, "Card removed from your saved collection!")
    
    return redirect(request.META.get('HTTP_REFERER', 'saved_cards'))


@login_required
def saved_cards(request):
    """View all saved cards with visibility filter"""
    visibility_filter = request.GET.get('visibility', 'all')
    
    saves = SavedCard.objects.filter(user=request.user).select_related('card', 'card__user')
    
    if visibility_filter == 'public':
        saves = saves.filter(visibility='public')
    elif visibility_filter == 'private':
        saves = saves.filter(visibility='private')
    
    public_count = SavedCard.objects.filter(user=request.user, visibility='public').count()
    private_count = SavedCard.objects.filter(user=request.user, visibility='private').count()
    
    context = {
        'saved_cards': [save.card for save in saves],
        'saves': saves,
        'visibility_filter': visibility_filter,
        'public_count': public_count,
        'private_count': private_count,
    }
    
    return render(request, 'cards/saved_cards.html', context)


@login_required
@login_required
def get_unread_message_count(request):
    """API endpoint to get unread message count"""
    from django.db.models import Q
    
    # Count unread messages in all conversations
    count = DirectMessage.objects.filter(
        recipient=request.user, 
        is_read=False
    ).count()
    
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

@login_required
def share_card_message(request, card_id):
    """Share a card via direct message - creates a new conversation"""
    from django.urls import reverse
    from django.db.models import Q
    
    card = get_object_or_404(Card, id=card_id)
    
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        message_text = request.POST.get('message')
        
        try:
            recipient = User.objects.get(username=recipient_username)
            
            # Check if recipient allows messages
            settings, created = UserSettings.objects.get_or_create(user=recipient)
            if not settings.allow_messages:
                messages.error(request, f"{recipient.username} has disabled direct messages.")
                return HttpResponseRedirect(reverse('card_detail', args=[card.id]))
            
            # Find or create conversation about this card
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
            
            # Create message in conversation
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
                message=f"{request.user.username} shared a card with you: {card.title}"
            )
            
            # Send email notification
            from .emails import send_card_shared_notification
            send_card_shared_notification(conversation, card, request.user, recipient)
            
            messages.success(request, f"Card shared with {recipient.username}!")
            return HttpResponseRedirect(reverse('conversation_detail', args=[conversation.id]))
            
        except User.DoesNotExist:
            messages.error(request, "User not found!")
            return HttpResponseRedirect(reverse('card_detail', args=[card.id]))
    
    return HttpResponseRedirect(reverse('card_detail', args=[card.id]))

@login_required
def send_friend_request(request, user_id):
    """Send a friend request to another user"""
    from django.urls import reverse
    from .emails import send_friend_request_email
    
    to_user = get_object_or_404(User, id=user_id)
    
    if to_user == request.user:
        messages.error(request, "You cannot send a friend request to yourself!")
        return redirect('explore')
    
    # Check if already following
    if Follow.objects.filter(follower=request.user, following=to_user).exists():
        messages.info(request, f"You are already friends with {to_user.username}!")
        return redirect('user_profile', username=to_user.username)
    
    # Check if request already exists
    existing_request = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=to_user,
        status='pending'
    ).first()
    
    if existing_request:
        messages.info(request, "Friend request already sent!")
        return redirect('user_profile', username=to_user.username)
    
    # Create friend request
    friend_request = FriendRequest.objects.create(
        from_user=request.user,
        to_user=to_user
    )
    
    # Create notification
    Notification.objects.create(
        recipient=to_user,
        sender=request.user,
        notification_type='follow',
        message=f"{request.user.username} sent you a friend request"
    )
    
    # Send email notification
    send_friend_request_email(friend_request)
    
    messages.success(request, f"Friend request sent to {to_user.username}!")
    return redirect('user_profile', username=to_user.username)


@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    if friend_request.status == 'pending':
        # Update request status
        friend_request.status = 'accepted'
        friend_request.save()
        
        # Create mutual follow relationships
        Follow.objects.get_or_create(follower=request.user, following=friend_request.from_user)
        Follow.objects.get_or_create(follower=friend_request.from_user, following=request.user)
        
        # Create notification for requester
        Notification.objects.create(
            recipient=friend_request.from_user,
            sender=request.user,
            notification_type='follow',
            message=f"{request.user.username} accepted your friend request"
        )
        
        # Send email notification to requester
        from .emails import send_friend_accepted_email
        send_friend_accepted_email(friend_request)
        
        messages.success(request, f"You are now friends with {friend_request.from_user.username}!")
    
    return redirect('notifications')


@login_required
def reject_friend_request(request, request_id):
    """Reject a friend request"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    if friend_request.status == 'pending':
        friend_request.status = 'rejected'
        friend_request.save()
        
        messages.success(request, "Friend request declined.")
    
    return redirect('notifications')


@login_required
def pending_friend_requests(request):
    """View all pending friend requests"""
    incoming_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user')
    
    outgoing_requests = FriendRequest.objects.filter(
        from_user=request.user,
        status='pending'
    ).select_related('to_user')
    
    context = {
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
    }
    
    return render(request, 'cards/friend_requests.html', context)

@login_required
def get_friend_request_count(request):
    """API endpoint to get pending friend request count"""
    count = FriendRequest.objects.filter(to_user=request.user, status='pending').count()
    return JsonResponse({'count': count})


@login_required
def find_friends(request):
    """Search for users to add as friends"""
    query = request.GET.get('q', '').strip()
    
    # Get users you're already following
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    # Get pending friend requests (both sent and received)
    pending_sent_ids = FriendRequest.objects.filter(
        from_user=request.user, 
        status='pending'
    ).values_list('to_user_id', flat=True)
    
    pending_received_ids = FriendRequest.objects.filter(
        to_user=request.user, 
        status='pending'
    ).values_list('from_user_id', flat=True)
    
    # Combine all excluded IDs
    excluded_ids = set(following_ids) | set(pending_sent_ids) | set(pending_received_ids) | {request.user.id}
    
    if query:
        # Search for users by username
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id__in=excluded_ids)[:20]
    else:
        # Show suggested users (most active or popular)
        users = User.objects.exclude(id__in=excluded_ids).annotate(
            card_count=Count('cards')
        ).order_by('-card_count')[:20]
    
    context = {
        'users': users,
        'search_query': query,
    }
    
    return render(request, 'cards/find_friends.html', context)


# Legacy redirect views for old messaging URLs
def redirect_to_conversations(request):
    """Redirect old inbox/sent URLs to conversations"""
    from django.shortcuts import redirect
    return redirect('conversations_list')

def redirect_compose_to_conversations(request, recipient_username=None):
    """Redirect old compose URLs to conversations"""
    from django.shortcuts import redirect
    return redirect('conversations_list')



@login_required
def user_settings(request):
    """User settings page with auto-save toggles"""
    
    user_settings_obj, created = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        print(f"DEBUG - Full POST data: {request.POST}")
        form_type = request.POST.get('form_type')
        print(f"DEBUG - form_type: '{form_type}'")
        
        # Handle toggle auto-save via AJAX
        if form_type == 'toggle':
            field = request.POST.get('field')
            value = request.POST.get('value') == 'true'
            
            if hasattr(user_settings_obj, field):
                setattr(user_settings_obj, field, value)
                user_settings_obj.save()
                return JsonResponse({'success': True})
            
            return JsonResponse({'success': False}, status=400)
        
        # Handle profile form submission
        elif form_type == 'profile':
            # Debug: Print what we're receiving
            print(f"DEBUG - POST data: {request.POST}")
            print(f"DEBUG - Bio: '{request.POST.get('bio')}'")
            print(f"DEBUG - Mobile: '{request.POST.get('mobile_number')}'")
            print(f"DEBUG - State: '{request.POST.get('home_state')}'")
            
            if request.FILES.get('profile_picture'):
                user_settings_obj.profile_picture = request.FILES['profile_picture']
            
            # Update fields - save empty strings as None for optional fields
            bio = request.POST.get('bio', '').strip()
            user_settings_obj.bio = bio if bio else None
            
            mobile = request.POST.get('mobile_number', '').strip()
            user_settings_obj.mobile_number = mobile if mobile else None
            
            home_state = request.POST.get('home_state', '').strip()
            user_settings_obj.home_state = home_state if home_state else None
            
            birthdate = request.POST.get('birthdate', '').strip()
            if birthdate:
                user_settings_obj.birthdate = birthdate
            else:
                user_settings_obj.birthdate = None
            
            user_settings_obj.save()
            
            # Debug: Verify it saved
            user_settings_obj.refresh_from_db()
            print(f"DEBUG - After save - Bio: '{user_settings_obj.bio}'")
            print(f"DEBUG - After save - Mobile: '{user_settings_obj.mobile_number}'")
            print(f"DEBUG - After save - State: '{user_settings_obj.home_state}'")
            
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('user_settings')
    
    # Get state choices
    state_choices = [
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
        ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'District of Columbia'),
    ]
    
    context = {
        'user_settings': user_settings_obj,
        'state_choices': state_choices,
    }
    
    return render(request, 'cards/settings.html', context)


@login_required
def card_history(request, card_id):
    """View version history of a card"""
    card = get_object_or_404(Card, id=card_id)
    
    # Only card owner can see history
    if card.user != request.user:
        messages.error(request, "You can only view history of your own cards.")
        return redirect('card_detail', card_id=card.id)
    
    versions = card.versions.all()
    
    context = {
        'card': card,
        'versions': versions,
    }
    
    return render(request, 'cards/card_history.html', context)


def commons_cards(request):
    """View all cards from Debrief Commons"""
    try:
        commons_user = User.objects.get(username='DebriefCommons')
        cards = Card.objects.filter(user=commons_user, visibility='public').order_by('-created_at')
        
        context = {
            'cards': cards,
            'commons_user': commons_user,
        }
        
        return render(request, 'cards/commons.html', context)
    except User.DoesNotExist:
        messages.error(request, "Debrief Commons not set up yet.")
        return redirect('index')


@login_required
def notebook(request):
    """User's personal research notebook"""
    topic_filter = request.GET.get('topic', '')
    stance_filter = request.GET.get('stance', '')
    type_filter = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    entries = NotebookEntry.objects.filter(user=request.user)
    
    if topic_filter:
        entries = entries.filter(topic=topic_filter)
    if stance_filter:
        entries = entries.filter(stance=stance_filter)
    if type_filter:
        entries = entries.filter(entry_type=type_filter)
    if search_query:
        from django.db.models import Q
        entries = entries.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Get counts by topic for sidebar
    topic_counts = {}
    for topic_code, topic_name in NotebookEntry.NOTEBOOK_TOPICS:
        count = NotebookEntry.objects.filter(user=request.user, topic=topic_code).count()
        if count > 0:
            topic_counts[topic_code] = {'name': topic_name, 'count': count}
    
    context = {
        'entries': entries,
        'topic_filter': topic_filter,
        'stance_filter': stance_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'topic_counts': topic_counts,
        'topics': NotebookEntry.NOTEBOOK_TOPICS,
    }
    
    return render(request, 'cards/notebook.html', context)


@login_required
def add_notebook_entry(request):
    """Add a new notebook entry"""
    # Get pre-filled data from bookmarklet
    prefill_url = request.GET.get('url', '')
    prefill_title = request.GET.get('title', '')
    prefill_selection = request.GET.get('selection', '')
    from_popup = request.GET.get('popup', '')
    
    # Determine entry type from URL
    entry_type = 'article'
    if 'youtube.com' in prefill_url or 'youtu.be' in prefill_url:
        entry_type = 'youtube'
    
    # Auto-save if coming from bookmarklet with URL and title
    if from_popup and prefill_url and prefill_title and request.method == 'GET':
        # Auto-create the entry
        # Try to get content summary based on type
        description = prefill_selection if prefill_selection else ''
        
        if entry_type == 'youtube':
            video_id = extract_video_id(prefill_url)
            if video_id:
                transcript = get_youtube_transcript(video_id)
                if transcript:
                    summary = summarize_transcript(transcript, max_length=500)
                    description = f"📝 Auto-summary: {summary}\n\n{description}" if description else f"📝 Auto-summary: {summary}"
                    print(f"✅ Successfully extracted transcript for {video_id}")
                else:
                    no_transcript_msg = "⏳ No transcript available yet. This could be because:\n• Video was recently uploaded (captions take time to generate)\n• Creator disabled captions\n• Live stream hasn't ended yet\n\nTry using the 'Regenerate Summary' button later!"
                    description = f"{no_transcript_msg}\n\n{description}" if description else no_transcript_msg
        
        elif entry_type == 'article' and is_valid_url(prefill_url):
            # Try to fetch and summarize article
            article_text = fetch_article_text(prefill_url)
            if article_text:
                summary = summarize_article(article_text, max_sentences=5)
                if summary:
                    description = f"📝 Auto-summary: {summary}\n\n{description}" if description else f"📝 Auto-summary: {summary}"
                    print(f"✅ Successfully summarized article from {prefill_url}")
                else:
                    description = f"⚠️ Could not generate summary for this article.\n\n{description}" if description else "⚠️ Could not generate summary for this article."
            else:
                description = f"⚠️ Could not extract article content. Site may be protected or require login.\n\n{description}" if description else "⚠️ Could not extract article content."
        
        if not description:
            description = 'Quick saved from browser'
        
        entry = NotebookEntry.objects.create(
            user=request.user,
            entry_type=entry_type,
            title=prefill_title,
            content=prefill_url,
            description=description,
            topic='general',  # General Research - user can change later
            stance='neutral',
            tags='quick-save',
        )
        messages.success(request, "📝 Saved to notebook!")
        return render(request, 'cards/close_popup.html', {'entry': entry})
    
    if request.method == 'POST':
        entry = NotebookEntry.objects.create(
            user=request.user,
            entry_type=request.POST.get('entry_type'),
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            description=request.POST.get('description', ''),
            topic=request.POST.get('topic'),
            stance=request.POST.get('stance', 'neutral'),
            tags=request.POST.get('tags', ''),
        )
        messages.success(request, "📝 Entry added to your notebook!")
        
        # If opened in popup, close it
        if request.GET.get('popup'):
            return render(request, 'cards/close_popup.html', {'entry': entry})
        
        return redirect('notebook')
    
    context = {
        'topics': NotebookEntry.NOTEBOOK_TOPICS,
        'prefill_url': prefill_url,
        'prefill_title': prefill_title,
        'prefill_selection': prefill_selection,
        'prefill_type': entry_type,
    }
    return render(request, 'cards/add_notebook_entry.html', context)


@login_required
def delete_notebook_entry(request, entry_id):
    """Delete a notebook entry"""
    entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
    entry.delete()
    messages.success(request, "Entry deleted from notebook.")
    return redirect('notebook')


def quick_save(request):
    """Quick save bookmarklet instructions page"""
    return render(request, 'cards/quick_save.html')


@login_required
def notebook_entry_detail(request, entry_id):
    """View detailed notebook entry"""
    entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
    
    # Extract YouTube video ID if it's a YouTube link
    youtube_id = None
    if entry.entry_type == 'youtube' or 'youtube.com' in entry.content or 'youtu.be' in entry.content:
        import re
        # Match various YouTube URL formats (handles &t= and other params)
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',  # watch?v=ID&...
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',  # youtu.be/ID
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',  # embed/ID
        ]
        for pattern in patterns:
            match = re.search(pattern, entry.content)
            if match:
                youtube_id = match.group(1)
                break
    
    # Parse auto-summary from description
    auto_summary = None
    remaining_description = entry.description
    
    if entry.description and '📝 Auto-summary:' in entry.description:
        parts = entry.description.split('📝 Auto-summary:', 1)
        if len(parts) > 1:
            # Extract the summary (everything after the marker until double newline or end)
            summary_part = parts[1]
            if '\n\n' in summary_part:
                auto_summary = summary_part.split('\n\n', 1)[0].strip()
                remaining_description = summary_part.split('\n\n', 1)[1].strip() if len(summary_part.split('\n\n', 1)) > 1 else ''
            else:
                auto_summary = summary_part.strip()
                remaining_description = ''
    
    # Remove transcript unavailable message from personal notes
    if remaining_description and '⏳ No transcript available yet' in remaining_description:
        # Remove the entire message
        lines = remaining_description.split('\n')
        filtered_lines = []
        skip = False
        for line in lines:
            if '⏳ No transcript available yet' in line:
                skip = True
            elif skip and "Try using the 'Regenerate Summary' button later!" in line:
                skip = False
                continue
            elif not skip:
                filtered_lines.append(line)
        remaining_description = '\n'.join(filtered_lines).strip()
    
    # Parse tags
    tags = [tag.strip() for tag in entry.tags.split(',') if tag.strip()] if entry.tags else []
    
    # Get individual notes
    notes = entry.notes.all()
    
    context = {
        'entry': entry,
        'auto_summary': auto_summary,
        'remaining_description': remaining_description,
        'tags': tags,
        'topics': NotebookEntry.NOTEBOOK_TOPICS,
        'notes': notes,
        'youtube_id': youtube_id,
    }
    
    return render(request, 'cards/notebook_entry_detail_enhanced.html', context)


@login_required
def regenerate_summary(request, entry_id):
    """Regenerate summary for YouTube video or article"""
    entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
    
    if entry.entry_type not in ['youtube', 'article']:
        messages.error(request, "Can only regenerate summaries for YouTube videos and articles.")
        return redirect('notebook_entry_detail', entry_id=entry.id)
    
    success = False
    
    if entry.entry_type == 'youtube':
        video_id = extract_video_id(entry.content)
        if not video_id:
            messages.error(request, "Could not extract video ID from URL.")
            return redirect('notebook_entry_detail', entry_id=entry.id)
        
        # Try to get transcript
        transcript = get_youtube_transcript(video_id)
        
        if transcript:
            summary = summarize_transcript(transcript, max_length=500)
            success = True
        else:
            messages.error(request, "⏳ Transcript still not available. Try again later!")
            return redirect('notebook_entry_detail', entry_id=entry.id)
    
    elif entry.entry_type == 'article':
        # Try to fetch and summarize article
        article_text = fetch_article_text(entry.content)
        if article_text:
            summary = summarize_article(article_text, max_sentences=5)
            if summary:
                success = True
            else:
                messages.error(request, "Could not generate summary for this article.")
                return redirect('notebook_entry_detail', entry_id=entry.id)
        else:
            messages.error(request, "⚠️ Could not extract article content. Site may be protected.")
            return redirect('notebook_entry_detail', entry_id=entry.id)
    
    if success:
        # Update description - replace old summary or error messages
        description = entry.description or ''
        
        # Remove old auto-summary if exists
        if '📝 Auto-summary:' in description:
            parts = description.split('📝 Auto-summary:', 1)
            if len(parts) > 1 and '\n\n' in parts[1]:
                description = parts[1].split('\n\n', 1)[1] if len(parts[1].split('\n\n', 1)) > 1 else ''
            else:
                description = parts[0]
        
        # Remove error messages
        if '⏳ No transcript available yet' in description or '⚠️ Could not' in description:
            parts = description.split('\n\n', 1)
            description = parts[1] if len(parts) > 1 else ''
        
        # Add new summary
        entry.description = f"📝 Auto-summary: {summary}\n\n{description}".strip()
        entry.save()
        
        messages.success(request, "✅ Summary generated successfully!")
    
    return redirect('notebook_entry_detail', entry_id=entry.id)


@login_required
def update_entry_topic(request, entry_id):
    """Update the topic of a notebook entry"""
    entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        new_topic = request.POST.get('topic')
        if new_topic:
            entry.topic = new_topic
            entry.save()
            messages.success(request, f"✅ Topic updated to {dict(NotebookEntry.NOTEBOOK_TOPICS).get(new_topic, new_topic)}!")
    
    return redirect('notebook_entry_detail', entry_id=entry.id)


@login_required
def update_entry_notes(request, entry_id):
    """Update personal notes for a notebook entry"""
    entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        new_notes = request.POST.get('notes', '').strip()
        
        # Preserve auto-summary if it exists
        if entry.description and '📝 Auto-summary:' in entry.description:
            # Extract the summary
            parts = entry.description.split('📝 Auto-summary:', 1)
            if len(parts) > 1:
                summary_part = parts[1]
                if '\n\n' in summary_part:
                    auto_summary = summary_part.split('\n\n', 1)[0].strip()
                else:
                    auto_summary = summary_part.strip()
                
                # Combine summary with new notes
                if new_notes:
                    entry.description = f"📝 Auto-summary: {auto_summary}\n\n{new_notes}"
                else:
                    entry.description = f"📝 Auto-summary: {auto_summary}"
            else:
                entry.description = new_notes
        else:
            # No auto-summary, just save the notes
            entry.description = new_notes
        
        entry.save()
        messages.success(request, "✅ Notes saved successfully!")
    
    return redirect('notebook_entry_detail', entry_id=entry.id)


@login_required
def add_notebook_note(request, entry_id):
    """Add an individual note to a notebook entry"""
    entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        note_text = request.POST.get('note_text', '').strip()
        note_content = request.POST.get('content', '').strip()  # From AJAX
        timestamp = request.POST.get('timestamp', '').strip()
        
        # Use whichever field has content
        text = note_text or note_content
        
        if text:
            note = NotebookNote.objects.create(
                entry=entry,
                text=text,
                timestamp=timestamp if timestamp else ''
            )
            
            # Return JSON for AJAX requests
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and not note_text:
                return JsonResponse({
                    'success': True,
                    'note_id': note.id,
                    'timestamp': note.timestamp or '',
                    'text': note.text,
                    'created_at': note.created_at.strftime('%b %d, %Y %I:%M %p')
                })
            
            messages.success(request, "✅ Note added!")
        else:
            # Return error for AJAX
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and not note_text:
                return JsonResponse({'success': False, 'error': 'Note cannot be empty'})
            messages.error(request, "Note cannot be empty.")
    
    return redirect('notebook_entry_detail', entry_id=entry.id)


@login_required
def delete_notebook_note(request, note_id):
    """Delete an individual note"""
    note = get_object_or_404(NotebookNote, id=note_id, entry__user=request.user)
    entry_id = note.entry.id
    note.delete()
    messages.success(request, "🗑️ Note deleted!")
    return redirect('notebook_entry_detail', entry_id=entry_id)


@login_required
def edit_notebook_note(request, note_id):
    """Edit an individual note"""
    note = get_object_or_404(NotebookNote, id=note_id, entry__user=request.user)
    
    if request.method == 'POST':
        note_text = request.POST.get('note_text', '').strip()
        if note_text:
            note.text = note_text
            note.save()
            messages.success(request, "✅ Note updated!")
        else:
            messages.error(request, "Note cannot be empty.")
    
    return redirect('notebook_entry_detail', entry_id=note.entry.id)


@login_required
def card_wizard(request):
    """Guided argument card creation wizard"""
    if request.method == 'POST':
        # Extract wizard data
        title = request.POST.get('title')
        topic = request.POST.get('topic')
        scope = request.POST.get('scope')
        stance = request.POST.get('stance')
        hypothesis = request.POST.get('hypothesis')
        conclusion = request.POST.get('conclusion')
        alternative = request.POST.get('alternative', '')
        
        # Create the card
        card = Card.objects.create(
            user=request.user,
            title=title,
            topic=topic,
            scope=scope,
            hypothesis=hypothesis,
            conclusion=conclusion,
            stance=stance,
            visibility='public'
        )
        
        # Add supporting arguments
        supporting_args = request.POST.getlist('supporting_args[]')
        for i, arg_text in enumerate(supporting_args, 1):
            if arg_text.strip():
                Argument.objects.create(
                    card=card,
                    type='pro',
                    summary=arg_text.strip(),
                    order=i
                )
        
        # Add opposing arguments
        opposing_args = request.POST.getlist('opposing_args[]')
        for i, arg_text in enumerate(opposing_args, 1):
            if arg_text.strip():
                Argument.objects.create(
                    card=card,
                    type='con',
                    summary=arg_text.strip(),
                    order=i
                )
        
        # Add alternative as a note in conclusion if provided
        if alternative.strip():
            card.conclusion = f"{conclusion}\n\nAlternative Solution: {alternative}"
            card.save()
        
        messages.success(request, "🎉 Argument card created successfully!")
        return redirect('card_detail', card_id=card.id)
    
    context = {
        'topics': Card.TOPIC_CHOICES,
    }
    return render(request, 'cards/card_wizard.html', context)


@login_required
def synthesize_public_figure_card(request):
    """Create a card synthesizing a public figure's argument"""
    # Only allow Commons user or admins to synthesize
    if not (request.user.username == 'DebriefCommons' or request.user.is_staff):
        messages.error(request, "Only Debrief Commons can synthesize public figure arguments.")
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        # Extract data
        title = request.POST.get('title')
        topic = request.POST.get('topic')
        scope = request.POST.get('scope')
        hypothesis = request.POST.get('hypothesis')
        conclusion = request.POST.get('conclusion')
        stance = request.POST.get('stance')
        
        # Public figure info
        original_source = request.POST.get('original_source')  # e.g., "Joe Rogan"
        source_url = request.POST.get('source_url')  # e.g., link to podcast
        
        # Create card as DebriefCommons user
        commons_user = User.objects.get(username='DebriefCommons')
        
        card = Card.objects.create(
            user=commons_user,
            title=title,
            topic=topic,
            scope=scope,
            hypothesis=hypothesis,
            conclusion=conclusion,
            stance=stance,
            visibility='public',
            source_type='public_figure',
            original_source=original_source,
            source_url=source_url,
            synthesized_by=request.user
        )
        
        # Add arguments
        supporting_args = request.POST.getlist('supporting_args[]')
        for i, arg_text in enumerate(supporting_args, 1):
            if arg_text.strip():
                Argument.objects.create(
                    card=card,
                    argument_type='supporting',
                    text=arg_text.strip(),
                    order=i
                )
        
        opposing_args = request.POST.getlist('opposing_args[]')
        for i, arg_text in enumerate(opposing_args, 1):
            if arg_text.strip():
                Argument.objects.create(
                    card=card,
                    argument_type='opposing',
                    text=arg_text.strip(),
                    order=i
                )
        
        messages.success(request, f"✅ Synthesized argument card for {original_source}!")
        return redirect('commons_cards')
    
    context = {
        'topics': Card.TOPIC_CHOICES,
    }
    return render(request, 'cards/synthesize_figure_card.html', context)


@login_required
def topic_survey(request, topic):
    """Interactive survey for a specific topic"""
    try:
        survey = TopicSurvey.objects.get(topic=topic, is_active=True)
    except TopicSurvey.DoesNotExist:
        messages.error(request, "Survey not available for this topic yet.")
        return redirect('create_card_wizard')
    
    questions = survey.questions.prefetch_related('options').all()
    
    context = {
        'survey': survey,
        'questions': questions,
        'topic_display': dict(Card.TOPIC_CHOICES).get(topic, topic),
    }
    
    return render(request, 'cards/topic_survey.html', context)


@login_required
def survey_list(request):
    """List all available topic surveys grouped by scope"""
    # Get scope filter from query params
    scope_filter = request.GET.get('scope', '')
    
    surveys = TopicSurvey.objects.filter(is_active=True).prefetch_related('questions')
    
    # Group by whether topics are typically federal or state
    federal_topics = ['immigration', 'foreign_policy', 'defense', 'healthcare', 'tax_policy', 
                      'social_security', 'gun_control', 'trade', 'climate_change']
    state_topics = ['education', 'criminal_justice', 'drug_policy', 'voting_rights', 
                    'housing', 'transportation', 'abortion']
    
    if scope_filter == 'federal':
        surveys = surveys.filter(topic__in=federal_topics)
    elif scope_filter == 'state':
        surveys = surveys.filter(topic__in=state_topics)
    
    # Separate surveys by typical scope
    federal_surveys = surveys.filter(topic__in=federal_topics)
    state_surveys = surveys.filter(topic__in=state_topics)
    
    context = {
        'surveys': surveys,
        'federal_surveys': federal_surveys,
        'state_surveys': state_surveys,
        'scope_filter': scope_filter,
    }
    
    return render(request, 'cards/survey_list.html', context)


def process_survey(request, topic):
    """Process survey responses and generate card preview"""
    if request.method != 'POST':
        return redirect('topic_survey', topic=topic)
    
    try:
        survey = TopicSurvey.objects.get(topic=topic)
    except TopicSurvey.DoesNotExist:
        messages.error(request, "Survey not found.")
        return redirect('survey_list')
    
    # Collect responses by type
    collected = {
        'stance': None,
        'scope': 'federal',
        'hypothesis': [],
        'supporting': [],
        'opposing': [],
        'conclusion': [],
    }
    
    for question in survey.questions.all():
        option_ids = request.POST.getlist(f'question_{question.id}')
        
        for option_id in option_ids:
            if option_id:
                option = QuestionOption.objects.get(id=option_id)
                maps_to = question.maps_to
                
                if maps_to in ['stance', 'scope']:
                    collected[maps_to] = option.card_value
                else:
                    collected[maps_to].append(option.card_value)
    
    # Combine hypothesis statements
    hypothesis_text = ' '.join(collected['hypothesis']) if collected['hypothesis'] else 'Immigration policy reform is needed.'
    
    # Combine conclusion statements
    conclusion_text = ' '.join(collected['conclusion']) if collected['conclusion'] else 'We need comprehensive immigration reform.'
    
    # Generate title based on topic and stance
    topic_name = dict(Card.TOPIC_CHOICES).get(topic, topic)
    
    # Store in session for preview
    request.session['draft_card'] = {
        'title': f"My Position on {topic_name} Reform",
        'topic': topic,
        'scope': collected['scope'],
        'stance': collected['stance'] or 'for',
        'hypothesis': hypothesis_text,
        'conclusion': conclusion_text,
        'supporting_args': collected['supporting'] if collected['supporting'] else [],
        'opposing_args': collected['opposing'] if collected['opposing'] else [],
    }
    
    return redirect('survey_card_preview')


@login_required
def edit_survey_card(request):
    """Edit the AI-generated card before publishing"""
    draft = request.session.get('draft_card')
    
    if not draft:
        messages.error(request, "No draft card found. Please take the survey first.")
        return redirect('create_card_wizard')
    
    if request.method == 'POST':
        # Create the card
        card = Card.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            topic=draft['topic'],
            scope=request.POST.get('scope'),
            hypothesis=request.POST.get('hypothesis'),
            conclusion=request.POST.get('conclusion'),
            stance=request.POST.get('stance'),
            visibility='public'
        )
        
        # Add supporting arguments
        supporting_args = request.POST.getlist('supporting_args[]')
        for i, arg_text in enumerate(supporting_args, 1):
            if arg_text.strip():
                Argument.objects.create(
                    card=card,
                    type='pro',
                    summary=arg_text.strip(),
                    order=i
                )
        
        # Add opposing arguments
        opposing_args = request.POST.getlist('opposing_args[]')
        for i, arg_text in enumerate(opposing_args, 1):
            if arg_text.strip():
                Argument.objects.create(
                    card=card,
                    type='con',
                    summary=arg_text.strip(),
                    order=i
                )
        
        # Clear session
        del request.session['draft_card']
        
        messages.success(request, "🎉 Argument card published!")
        return redirect('card_detail', card_id=card.id)
    
    context = {
        'draft': draft,
        'topics': Card.TOPIC_CHOICES,
    }
    
    return render(request, 'cards/edit_survey_card.html', context)


@login_required
def survey_card_preview(request):
    """Show preview of survey-generated card"""
    draft = request.session.get('draft_card')
    
    if not draft:
        messages.error(request, "No draft card found. Please take a survey first.")
        return redirect('survey_list')
    
    topic_name = dict(Card.TOPIC_CHOICES).get(draft['topic'], draft['topic'])
    
    context = {
        'draft': draft,
        'topic_display': topic_name,
    }
    
    return render(request, 'cards/survey_card_preview.html', context)


@login_required
def publish_survey_card(request):
    """Publish the survey-generated card without editing"""
    if request.method != 'POST':
        return redirect('survey_list')
    
    draft = request.session.get('draft_card')
    
    if not draft:
        messages.error(request, "No draft card found.")
        return redirect('survey_list')
    
    # Create the card
    card = Card.objects.create(
        user=request.user,
        title=draft['title'],
        topic=draft['topic'],
        scope=draft['scope'],
        hypothesis=draft['hypothesis'],
        conclusion=draft['conclusion'],
        stance=draft['stance'],
        visibility='public'
    )
    
    # Add supporting arguments
    for i, arg_text in enumerate(draft.get('supporting_args', []), 1):
        if arg_text:
            Argument.objects.create(
                card=card,
                type='pro',
                summary=arg_text,
                order=i
            )
    
    # Add opposing arguments
    for i, arg_text in enumerate(draft.get('opposing_args', []), 1):
        if arg_text:
            Argument.objects.create(
                card=card,
                type='con',
                summary=arg_text,
                order=i
            )
    
    # Clear session
    del request.session['draft_card']
    
    messages.success(request, "🎉 Your argument card has been published!")
    return redirect('card_detail', card_id=card.id)


@login_required
def discard_survey_card(request):
    """Discard the draft and start over"""
    if request.method == 'POST':
        if 'draft_card' in request.session:
            del request.session['draft_card']
        messages.info(request, "Draft discarded. Take another survey to create a new card!")
    
    return redirect('survey_list')


@login_required
def search_facts(request):
    """Search for facts related to a query"""
    query = request.GET.get('q', '')
    topic = request.GET.get('topic', '')
    
    if not query:
        return JsonResponse({'results': []})
    
    from .fact_apis import FactFetcher
    fetcher = FactFetcher()
    
    results = []
    
    # Search FactCheck.org
    factcheck_results = fetcher.search_fact_check_org(query)
    results.extend(factcheck_results)
    
    # Search Pew Research
    pew_results = fetcher.search_pew_research(query)
    for item in pew_results:
        results.append({
            'title': item['title'],
            'url': item['url'],
            'source': 'Pew Research Center'
        })
    
    # Get Wikipedia context
    wiki_summary = fetcher.fetch_wikipedia_summary(query)
    if wiki_summary:
        results.insert(0, {
            'title': f'Overview: {query}',
            'excerpt': wiki_summary,
            'url': f'https://en.wikipedia.org/wiki/{query.replace(" ", "_")}',
            'source': 'Wikipedia'
        })
    
    # Search database facts
    db_facts = PolicyFact.objects.filter(
        fact_text__icontains=query
    )
    if topic:
        db_facts = db_facts.filter(topic=topic)
    
    for fact in db_facts[:5]:
        results.append({
            'title': fact.fact_text[:100],
            'url': fact.source_url,
            'source': fact.source_name,
            'date': fact.date_published.strftime('%Y-%m-%d') if fact.date_published else None
        })
    
    return JsonResponse({'results': results[:10]})


@login_required
def enhanced_fact_search(request):
    """AI-enhanced fact search with Ground News integration"""
    query = request.GET.get('q', '')
    topic = request.GET.get('topic', '')
    question_id = request.GET.get('question_id', '')
    
    if not query:
        return JsonResponse({'results': [], 'suggestions': {}})
    
    from .fact_apis import FactFetcher
    from django.db.models import Q, Count, Case, When, IntegerField
    
    results = []
    suggestions = {}
    
    # Get facts already shown in context to avoid duplicates
    shown_facts = []
    if question_id:
        try:
            question = SurveyQuestion.objects.get(id=question_id)
            if question.context_stats:
                shown_facts = [line.strip() for line in question.context_stats.split('\n') if line.strip()]
        except:
            pass
    
    # Split query into words for smart matching
    words = [w.lower() for w in query.split() if len(w) > 2]
    
    # Build query - match ANY word
    db_query = Q()
    for word in words:
        db_query |= Q(fact_text__icontains=word)
    
    # Get database facts
    db_facts = PolicyFact.objects.filter(db_query)
    if topic:
        db_facts = db_facts.filter(topic=topic)
    
    # Score by relevance - count how many query words match
    db_facts = db_facts.annotate(
        match_score=Count(
            Case(
                *[When(fact_text__icontains=word, then=1) for word in words],
                output_field=IntegerField()
            )
        )
    ).order_by('-match_score', '-relevance_score')[:10]
    
    # Filter out facts already shown
    for fact in db_facts:
        fact_preview = fact.fact_text[:80]
        is_duplicate = any(fact_preview in shown for shown in shown_facts)
        
        if not is_duplicate:
            results.append({
                'title': fact.fact_text,
                'url': fact.source_url,
                'source': fact.source_name,
                'date': fact.date_published.strftime('%Y-%m-%d') if fact.date_published else None,
                'type': 'fact',
                'excerpt': '',
                'ai_recommended': fact.match_score >= len(words) / 2,  # Matches 50%+ of query words
                'ai_explanation': f'Matches {fact.match_score} of {len(words)} search terms' if fact.match_score > 1 else ''
            })
    
    # Only fetch external sources if we need more results
    if len(results) < 5:
        from .fact_apis import DuckDuckGoSearch
        
        # Try DuckDuckGo for current information
        try:
            ddg = DuckDuckGoSearch()
            # Make query more specific for better results
            search_query = f"{query} statistics research study"
            ddg_results = ddg.search(search_query, max_results=3)
            
            for result in ddg_results:
                # Filter for credible sources
                credible_domains = ['gov', 'edu', '.org', 'reuters', 'apnews', 'pewresearch']
                is_credible = any(domain in result['url'].lower() for domain in credible_domains)
                
                if is_credible:
                    results.append({
                        'title': result['title'],
                        'url': result['url'],
                        'source': result['url'].split('/')[2] if '/' in result['url'] else 'Web',
                        'excerpt': result['excerpt'],
                        'type': 'web-search',
                        'ai_recommended': is_credible,
                        'ai_explanation': 'Current information from credible source'
                    })
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
        
        fetcher = FactFetcher()
        
        # FactCheck.org - great for controversial claims
        try:
            factcheck_results = fetcher.search_fact_check_org(query)
            for result in factcheck_results[:3]:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'source': 'FactCheck.org',
                    'excerpt': result.get('excerpt', ''),
                    'type': 'fact-check',
                    'ai_recommended': True,
                    'ai_explanation': 'Independent fact-checking of claims'
                })
        except Exception as e:
            print(f"FactCheck error: {e}")
        
        # Pew Research - for statistics and studies
        try:
            pew_results = fetcher.search_pew_research(query)
            for item in pew_results[:2]:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'source': 'Pew Research Center',
                    'type': 'study',
                    'excerpt': '',
                    'ai_recommended': True,
                    'ai_explanation': 'Nonpartisan research and polling'
                })
        except Exception as e:
            print(f"Pew Research error: {e}")
    
    # Add Wikipedia only if very few results
    if len(results) < 2:
        try:
            fetcher = FactFetcher()
            wiki_summary = fetcher.fetch_wikipedia_summary(query)
            if wiki_summary:
                results.append({
                    'title': f'Overview: {query}',
                    'excerpt': wiki_summary,
                    'url': f'https://en.wikipedia.org/wiki/{query.replace(" ", "_")}',
                    'source': 'Wikipedia',
                    'type': 'overview',
                    'ai_recommended': False
                })
        except Exception as e:
            print(f"Wikipedia error: {e}")
    
    # Generate AI suggestions for better searches
    if len(results) < 2 or len(query) < 10:
        suggestions = {
            'better_queries': generate_better_queries(query, topic),
            'research_tips': [
                f'Try searching for specific statistics about {topic}',
                'Look for sources with recent data (last 2-3 years)',
                'Compare perspectives from different political viewpoints'
            ],
            'key_terms': extract_key_terms(query, topic)
        }
    
    # Filter to only show AI-recommended results (top 3)
    recommended_results = [r for r in results if r.get('ai_recommended', False)]
    
    # If we have recommended results, only show those (max 3)
    if recommended_results:
        final_results = recommended_results[:3]
    else:
        # Fallback: show top 3 results even if not AI-recommended
        final_results = results[:3]
    
    return JsonResponse({
        'results': final_results,
        'suggestions': suggestions,
        'query_enhanced': len(suggestions) > 0,
        'total_found': len(results)  # Let them know how many we found
    })

def generate_better_queries(query, topic):
    """Generate better search queries based on user input"""
    queries = []
    
    # Topic-specific suggestions
    if topic == 'immigration':
        if 'crime' in query.lower():
            queries = [
                'immigrant crime rates statistics',
                'undocumented immigrants criminal activity data',
                'immigration and public safety research'
            ]
        elif 'economic' in query.lower() or 'job' in query.lower():
            queries = [
                'economic impact of immigration',
                'immigrant workforce contributions',
                'immigration effect on wages'
            ]
        elif 'border' in query.lower():
            queries = [
                'border security effectiveness',
                'border crossing statistics',
                'immigration enforcement costs'
            ]
        else:
            queries = [
                f'{topic} statistics',
                f'{topic} research studies',
                f'{topic} economic impact'
            ]
    
    return queries[:3]

def extract_key_terms(query, topic):
    """Extract key terms to help user understand topic"""
    terms = {
        'immigration': ['undocumented', 'visa', 'asylum', 'deportation', 'border security', 'naturalization'],
        'healthcare': ['single-payer', 'medicare', 'medicaid', 'ACA', 'insurance mandate'],
        'economy': ['GDP', 'unemployment', 'inflation', 'deficit', 'trade balance']
    }
    
    return terms.get(topic, [])[:4]


def fact_finder(request):
    """Standalone fact finder tool in Commons"""
    # Get all available topics from Card choices
    federal_topics = [
        ('immigration', 'Immigration Policy'),
        ('foreign_policy', 'Foreign Policy'),
        ('defense', 'Military & Defense'),
        ('healthcare', 'Healthcare Reform'),
        ('tax_policy', 'Tax Policy'),
        ('social_security', 'Social Security'),
        ('gun_control', 'Gun Control'),
        ('trade', 'Trade Policy'),
        ('climate_change', 'Climate Change Policy'),
    ]
    
    state_topics = [
        ('education', 'Education Funding'),
        ('criminal_justice', 'Criminal Justice Reform'),
        ('drug_policy', 'Drug Policy'),
        ('voting_rights', 'Voting Rights'),
        ('housing', 'Housing Policy'),
        ('transportation', 'Transportation'),
        ('abortion', 'Abortion Access'),
        ('police_reform', 'Police Reform'),
    ]
    
    context = {
        'federal_topics': federal_topics,
        'state_topics': state_topics,
    }
    
    return render(request, 'cards/fact_finder.html', context)


@login_required
def notebook_quick_save_api(request):
    """API endpoint to quick save to notebook from fact finder or bookmarklet"""
    if request.method == 'POST':
        url = request.POST.get('url', '')
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        topic = request.POST.get('topic', 'general')
        source = request.POST.get('source', 'quick-save')
        
        if not url:
            return JsonResponse({'success': False, 'error': 'URL required'})
        
        # Determine entry type based on URL
        entry_type = 'article'
        if 'youtube.com' in url or 'youtu.be' in url:
            entry_type = 'video'
        
        # Create notebook entry
        try:
            entry = NotebookEntry.objects.create(
                user=request.user,
                title=title or url,
                content=url,  # URL goes in content field
                description=description or '',  # Will be updated with summary
                topic=topic,
                entry_type=entry_type,
                stance='neutral',  # Default stance
                tags=f'{source},{topic}' if source != 'quick-save' else topic
            )
            
            # Auto-summarize only if explicitly requested
            auto_summarize = request.POST.get('auto_summarize', 'false') == 'true'
            if entry_type == 'article' and not description and auto_summarize:
                try:
                    from .article_utils import ArticleSummarizer
                    summarizer = ArticleSummarizer()
                    summary = summarizer.summarize_article(url)
                    
                    if summary:
                        entry.description = f"📝 Auto-summary:\n{summary}"
                        entry.save()
                except Exception as e:
                    print(f"Summarization failed: {e}")
                    # Continue anyway - entry is saved without summary
            
            return JsonResponse({
                'success': True,
                'entry_id': entry.id,
                'notebook_url': f'/notebook/?topic={topic}',
                'message': f'Saved to notebook under {topic}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'POST required'})


@login_required
def share_to_squad(request, entry_id):
    """Share a notebook entry to squad digest"""
    if request.method == 'POST':
        entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
        description = request.POST.get('description', '')
        
        # Check if already shared
        from .models import SquadDigest
        existing = SquadDigest.objects.filter(
            shared_by=request.user,
            notebook_entry=entry
        ).first()
        
        if existing:
            return JsonResponse({'success': False, 'error': 'Already shared to squad'})
        
        # Create squad digest entry
        digest = SquadDigest.objects.create(
            shared_by=request.user,
            notebook_entry=entry,
            description=description
        )
        
        # Notify all friends
        from django.db.models import Q
        friendships = FriendRequest.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user),
            status='accepted'
        )
        
        friend_count = 0
        for friendship in friendships:
            friend = friendship.to_user if friendship.from_user == request.user else friendship.from_user
            Notification.objects.create(
                recipient=friend,
                sender=request.user,
                notification_type='squad_share',
                message=f"{request.user.username} shared a video to Squad Digest: {entry.title}"
            )
            friend_count += 1
        
        return JsonResponse({
            'success': True,
            'digest_id': digest.id,
            'message': f'Shared to {friend_count} friends'
        })
    
    return JsonResponse({'success': False, 'error': 'POST required'})


@login_required
def squad_digest(request):
    """View squad digest - shared content from friends"""
    from django.db.models import Q
    from .models import SquadDigest
    
    # Get user's friends
    friendships = FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    )
    
    friend_ids = []
    for friendship in friendships:
        friend = friendship.to_user if friendship.from_user == request.user else friendship.from_user
        friend_ids.append(friend.id)
    
    # Get digests shared by friends + user's own shares
    digests = SquadDigest.objects.filter(
        Q(shared_by__id__in=friend_ids) | Q(shared_by=request.user)
    ).select_related('shared_by', 'notebook_entry').prefetch_related('squad_notes')
    
    # Extract YouTube IDs for each digest
    import re
    for digest in digests:
        if digest.notebook_entry.entry_type == 'youtube':
            patterns = [
                r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
                r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
                r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
            ]
            youtube_id = None
            for pattern in patterns:
                match = re.search(pattern, digest.notebook_entry.content)
                if match:
                    youtube_id = match.group(1)
                    break
            digest.youtube_id = youtube_id
            print(f"DEBUG: Set youtube_id={youtube_id} for {digest.notebook_entry.title}")
    
    context = {
        'digests': digests,
        'friend_count': len(friend_ids),
    }
    
    return render(request, 'cards/squad_digest.html', context)




@login_required
def squad_digest_detail(request, digest_id):
    """View detailed squad digest with full notes"""
    from .models import SquadDigest
    digest = get_object_or_404(SquadDigest, id=digest_id)
    
    # Extract YouTube ID
    import re
    youtube_id = None
    if digest.notebook_entry.entry_type == 'youtube':
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, digest.notebook_entry.content)
            if match:
                youtube_id = match.group(1)
                break
    
    notes = digest.squad_notes.all().order_by('created_at')
    
    context = {
        'digest': digest,
        'youtube_id': youtube_id,
        'notes': notes,
    }
    
    return render(request, 'cards/squad_digest_detail.html', context)


@login_required  
def add_squad_note(request, digest_id):
    """Add a note to squad digest content"""
    if request.method == 'POST':
        from .models import SquadDigest, SquadDigestNote
        digest = get_object_or_404(SquadDigest, id=digest_id)
        text = request.POST.get('text', '').strip()
        timestamp = request.POST.get('timestamp', '').strip()
        
        if text:
            note = SquadDigestNote.objects.create(
                digest=digest,
                user=request.user,
                text=text,
                timestamp=timestamp
            )
            
            # Notify the person who shared it (if not yourself)
            if digest.shared_by != request.user:
                Notification.objects.create(
                    recipient=digest.shared_by,
                    sender=request.user,
                    notification_type='squad_note',
                    message=f"{request.user.username} added a note to your shared video"
                )
            
            return JsonResponse({
                'success': True,
                'note': {
                    'id': note.id,
                    'user': request.user.username,
                    'text': note.text,
                    'timestamp': note.timestamp,
                    'created_at': note.created_at.strftime('%b %d, %Y %I:%M %p')
                }
            })
        
        return JsonResponse({'success': False, 'error': 'Text required'})
    
    return JsonResponse({'success': False, 'error': 'POST required'})



@login_required
def delete_squad_digest(request, digest_id):
    """Delete a squad digest post (only if you shared it)"""
    if request.method == 'POST':
        from .models import SquadDigest
        digest = get_object_or_404(SquadDigest, id=digest_id, shared_by=request.user)
        digest.delete()
        return JsonResponse({'success': True, 'message': 'Removed from Squad Digest'})
    return JsonResponse({'success': False, 'error': 'POST required'})


@login_required
def generate_summary(request, entry_id):
    """Generate or regenerate AI summary for article"""
    if request.method == 'POST':
        entry = get_object_or_404(NotebookEntry, id=entry_id, user=request.user)
        
        if entry.entry_type != 'article':
            return JsonResponse({'success': False, 'error': 'Can only summarize articles'})
        
        # Check if API key exists
        import os
        if not os.environ.get('ANTHROPIC_API_KEY'):
            return JsonResponse({'success': False, 'error': 'AI summarization not configured. Please add ANTHROPIC_API_KEY to environment variables.'})
        
        try:
            from .article_utils import ArticleSummarizer
            summarizer = ArticleSummarizer()
            summary = summarizer.summarize_article(entry.content)
            
            if summary:
                # Update description with new summary
                entry.description = f"📝 Auto-summary:\n{summary}"
                entry.save()
                
                return JsonResponse({
                    'success': True,
                    'summary': summary
                })
            else:
                return JsonResponse({'success': False, 'error': 'Could not generate summary - article may not be accessible'})
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Summary generation error: {error_detail}")
            return JsonResponse({'success': False, 'error': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': 'POST required'})

