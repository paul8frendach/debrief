from django.db import migrations
from django.db.models import Q


def migrate_messages_to_conversations(apps, schema_editor):
    """Create conversations for existing direct messages"""
    DirectMessage = apps.get_model('cards', 'DirectMessage')
    Conversation = apps.get_model('cards', 'Conversation')
    
    # Get all existing messages
    messages = DirectMessage.objects.all().order_by('created_at')
    
    # Group messages by sender/recipient pairs
    conversation_map = {}
    
    for message in messages:
        # Create a key for this pair (sorted to ensure consistency)
        users = tuple(sorted([message.sender_id, message.recipient_id]))
        key = (users, None)  # No card for legacy messages
        
        if key not in conversation_map:
            # Create new conversation
            conversation = Conversation.objects.create(
                participant1_id=users[0],
                participant2_id=users[1],
                card=None
            )
            conversation_map[key] = conversation
        
        # Assign message to conversation
        message.conversation = conversation_map[key]
        message.save(update_fields=['conversation'])


def reverse_migration(apps, schema_editor):
    """Reverse the migration if needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0011_alter_directmessage_options_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_messages_to_conversations, reverse_migration),
    ]