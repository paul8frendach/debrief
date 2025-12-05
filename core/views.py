from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Card, Argument, Source, DirectMessage

# ------------------------------
# CARD VIEWS
# ------------------------------

@login_required
def card_list(request):
    cards = Card.objects.filter(visibility='public') | Card.objects.filter(user=request.user)
    return render(request, 'cards/card_list.html', {'cards': cards})

@login_required
def card_detail(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    return render(request, 'cards/card_detail.html', {'card': card})

@login_required
def create_card(request):
    if request.method == 'POST':
        card = Card.objects.create(
            user=request.user,
            topic=request.POST.get('topic'),
            subcategory=request.POST.get('subcategory', ''),
            title=request.POST.get('title', ''),
            stance=request.POST.get('stance', ''),
            hypothesis=request.POST.get('hypothesis', ''),
            conclusion=request.POST.get('conclusion', ''),
            visibility=request.POST.get('visibility', 'private')
        )
        return redirect('card_detail', card_id=card.id)
    return render(request, 'cards/create_card.html')

@login_required
def update_card(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    if request.method == 'POST':
        card.topic = request.POST.get('topic', card.topic)
        card.subcategory = request.POST.get('subcategory', card.subcategory)
        card.title = request.POST.get('title', card.title)
        card.stance = request.POST.get('stance', card.stance)
        card.hypothesis = request.POST.get('hypothesis', card.hypothesis)
        card.conclusion = request.POST.get('conclusion', card.conclusion)
        card.visibility = request.POST.get('visibility', card.visibility)
        card.save()
        return redirect('card_detail', card_id=card.id)
    return render(request, 'cards/update_card.html', {'card': card})

@login_required
def delete_card(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    card.delete()
    return redirect('card_list')


# ------------------------------
# ARGUMENT VIEWS
# ------------------------------

@login_required
def add_argument(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    if request.method == 'POST':
        Argument.objects.create(
            card=card,
            type=request.POST.get('type'),
            summary=request.POST.get('summary', ''),
            detail=request.POST.get('detail', ''),
            order=request.POST.get('order', 0)
        )
        return redirect('card_detail', card_id=card.id)
    return render(request, 'cards/add_argument.html', {'card': card})

@login_required
def delete_argument(request, argument_id):
    argument = get_object_or_404(Argument, id=argument_id, card__user=request.user)
    card_id = argument.card.id
    argument.delete()
    return redirect('card_detail', card_id=card_id)


# ------------------------------
# SOURCE VIEWS
# ------------------------------

@login_required
def add_source(request, argument_id):
    argument = get_object_or_404(Argument, id=argument_id, card__user=request.user)
    if request.method == 'POST':
        Source.objects.create(
            argument=argument,
            url=request.POST.get('url', ''),
            title=request.POST.get('title', '')
        )
        return redirect('card_detail', card_id=argument.card.id)
    return render(request, 'cards/add_source.html', {'argument': argument})

@login_required
def delete_source(request, source_id):
    source = get_object_or_404(Source, id=source_id, argument__card__user=request.user)
    card_id = source.argument.card.id
    source.delete()
    return redirect('card_detail', card_id=card_id)


# ------------------------------
# MESSAGING VIEWS
# ------------------------------

@login_required
def compose_message(request, username=None):
    recipient_user = None
    if username:
        recipient_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        subject = request.POST.get('subject', '')
        message_body = request.POST.get('message', '')

        recipient = get_object_or_404(User, username=recipient_username)
        DirectMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            message=message_body
        )
        return redirect('inbox')

    return render(request, 'cards/compose_message.html', {'recipient_user': recipient_user})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(DirectMessage, id=message_id)
    if message.sender == request.user or message.recipient == request.user:
        message.delete()
    return redirect('inbox')

@login_required
def get_unread_message_count(request):
    count = DirectMessage.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


# ------------------------------
# DASHBOARD / PROFILE
# ------------------------------

@login_required
def dashboard(request):
    user_cards = Card.objects.filter(user=request.user)
    unread_count = DirectMessage.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'cards/dashboard.html', {'cards': user_cards, 'unread_count': unread_count})

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_cards = Card.objects.filter(user=profile_user)
    return render(request, 'cards/user_profile.html', {'profile_user': profile_user, 'cards': user_cards})


