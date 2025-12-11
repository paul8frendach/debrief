from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0025_factsource_remove_surveyquestion_context_stats_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyquestion',
            name='context_stats',
            field=models.TextField(blank=True, help_text='Bullet points with key statistics'),
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='learn_more',
            field=models.TextField(blank=True, help_text='Deeper explanation and background'),
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='sources',
            field=models.TextField(blank=True, help_text='Comma-separated URLs to credible sources'),
        ),
    ]
