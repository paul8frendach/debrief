from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0012_migrate_messages_to_conversations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directmessage',
            name='conversation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='cards.conversation'),
        ),
    ]