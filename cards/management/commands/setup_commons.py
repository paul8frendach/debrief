from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cards.models import UserSettings

class Command(BaseCommand):
    help = 'Create or get the Debrief Commons account'

    def handle(self, *args, **kwargs):
        # Create or get the commons user
        commons_user, created = User.objects.get_or_create(
            username='DebriefCommons',
            defaults={
                'email': 'commons@debrief.com',
                'first_name': 'Debrief',
                'is_staff': True,
            }
        )
        
        if created:
            commons_user.set_password('debrief_commons_2024')
            commons_user.save()
            self.stdout.write(self.style.SUCCESS('✅ Created Debrief Commons account'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Debrief Commons account already exists'))
        
        # Create user settings
        settings, _ = UserSettings.objects.get_or_create(
            user=commons_user,
            defaults={'allow_messages': False}
        )
        
        self.stdout.write(self.style.SUCCESS(f'Username: DebriefCommons'))
        self.stdout.write(self.style.SUCCESS(f'Password: debrief_commons_2024'))
