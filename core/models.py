from django.db import models
from django.contrib.auth.models import User

# --------------------------
# Core Models
# --------------------------
class Card(models.Model):
    """Argument card"""
    TOPIC_CHOICES = [
        ('immigration', 'Immigration'),
        ('healthcare', 'Healthcare'),
        ('gun_rights', 'Gun Rights'),
        ('abortion', 'Abortion'),
        ('climate', 'Climate Change'),
        ('economy', 'Economy & Trade'),
        ('education', 'Education'),
        ('criminal_justice', 'Criminal Justice'),
        ('foreign_policy', 'Foreign Policy'),
        ('taxation', 'Taxation'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES)
    subcategory = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200)
    stance = models.CharField(max_length=100)
    hypothesis = models.CharField(max_length=250)
    conclusion = models.CharField(max_length=250)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"


class Argument(models.Model):
    """Pro or Con point within a card"""
    TYPE_CHOICES = [
        ('pro', 'Pro'),
        ('con', 'Con'),
    ]
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='arguments')
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    summary = models.CharField(max_length=150)
    detail = models.TextField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.type}: {self.summary}"


class Source(models.Model):
    """Source URL for an argument"""
    argument = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name='sources')
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.title or self.url


# --------------------------
# Social / User Interaction
# --------------------------
class Follow(models.Model):
    """User following relationship"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Notification(models.Model):
    """User notifications for follows, comments, likes, etc."""
    NOTIFICATION_TYPES = [
        ('follow', 'New Follower'),
        ('card', 'New Card from Following'),
        ('comment', 'New Comment'),
        ('like', 'New Like'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"


class SavedCard(models.Model):
    """Users can save/bookmark cards"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='saves')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'card')
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.card.title}"


class UserSettings(models.Model):
    """User privacy and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    allow_messages = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s settings"


# --------------------------
# Direct Messaging
# --------------------------
class DirectMessage(models.Model):
    """Direct messages between users"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} - {self.subject or 'No subject'}"
