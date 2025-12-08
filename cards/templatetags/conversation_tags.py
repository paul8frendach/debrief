from django import template

register = template.Library()

@register.simple_tag
def get_other_user(conversation, current_user):
    """Get the other participant in a conversation"""
    if conversation.participant1 == current_user:
        return conversation.participant2
    return conversation.participant1