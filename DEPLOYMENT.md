# Debrief Deployment Guide

## Latest Features (Dec 2024)
- 🚀 Squad Digest - Collaborative video watching with notes
- 🟢 Online status indicators
- ✅ Simplified signup (no email verification)
- 📝 Timestamped notes on videos
- 🗑️ Delete squad posts
- 👥 Redesigned Friends hub

## Render Environment Variables
Required:
- SECRET_KEY
- DATABASE_URL (auto-set)
- ALLOWED_HOSTS=.onrender.com
- DEBUG=False

Optional:
- ANTHROPIC_API_KEY (for AI summarization)

## Post-Deployment Steps
1. Run migrations: `python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Create UserProfiles for existing users (in shell):
```python
   from django.contrib.auth.models import User
   from cards.models import UserProfile
   for user in User.objects.all():
       UserProfile.objects.get_or_create(user=user)
```

## URLs to Test
- / - Homepage
- /signup/ - New user signup
- /friends/ - Friends hub
- /squad-digest/ - Squad Digest feed
- /notebook/ - Personal notebook
- /commons/ - Tools & features
