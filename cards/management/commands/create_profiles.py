from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cards.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfiles for all users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'{status}: {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Done! Processed {User.objects.count()} users'))
