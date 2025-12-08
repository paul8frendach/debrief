from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    """Main card model for organizing arguments"""
    
    SCOPE_CHOICES = [
        ('federal', 'Federal'),
        ('state', 'State'),
    ]
    
    TOPIC_CHOICES = [
        # Federal Topics
        ('immigration_policy', 'Immigration Policy'),
        ('healthcare_reform', 'Healthcare Reform'),
        ('gun_control', 'Gun Control'),
        ('abortion_rights', 'Abortion Rights'),
        ('climate_change_policy', 'Climate Change Policy'),
        ('tax_policy', 'Tax Policy'),
        ('social_security', 'Social Security'),
        ('medicare_medicaid', 'Medicare/Medicaid'),
        ('foreign_policy', 'Foreign Policy'),
        ('military_spending', 'Military Spending'),
        ('education_funding', 'Education Funding'),
        ('infrastructure', 'Infrastructure'),
        ('criminal_justice_reform', 'Criminal Justice Reform'),
        ('drug_policy', 'Drug Policy'),
        ('labor_laws', 'Labor Laws'),
        ('minimum_wage', 'Minimum Wage'),
        ('trade_policy', 'Trade Policy'),
        ('national_security', 'National Security'),
        ('voting_rights', 'Voting Rights'),
        ('campaign_finance', 'Campaign Finance'),
        
        # State Topics
        ('state_income_tax', 'State Income Tax'),
        ('property_tax', 'Property Tax'),
        ('state_education_funding', 'State Education Funding'),
        ('marijuana_legalization', 'Marijuana Legalization'),
        ('death_penalty', 'Death Penalty'),
        ('state_healthcare', 'State Healthcare'),
        ('gun_regulations', 'Gun Regulations'),
        ('abortion_access', 'Abortion Access'),
        ('voting_laws', 'Voting Laws'),
        ('police_reform', 'Police Reform'),
        ('prison_reform', 'Prison Reform'),
        ('environmental_regulations', 'Environmental Regulations'),
        ('state_minimum_wage', 'State Minimum Wage'),
        ('workers_rights', 'Workers Rights'),
        ('housing_policy', 'Housing Policy'),
        ('transportation', 'Transportation'),
        ('public_safety', 'Public Safety'),
        ('zoning_laws', 'Zoning Laws'),
        ('state_budgets', 'State Budgets'),
        ('redistricting', 'Redistricting'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='federal')
    topic = models.CharField(max_length=100, choices=TOPIC_CHOICES)
    subcategory = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=300)
    stance = models.CharField(max_length=100)
    hypothesis = models.TextField()
    conclusion = models.TextField()
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Argument(models.Model):
    """Pro or Con argument for a card"""
    TYPE_CHOICES = [
        ('pro', 'Pro'),
        ('con', 'Con'),
    ]
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='arguments')
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    summary = models.TextField()
    detail = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.summary[:50]}"


class Source(models.Model):
    """Source/citation for an argument"""
    argument = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name='sources')
    title = models.CharField(max_length=300)
    url = models.URLField(blank=True)
    author = models.CharField(max_length=200, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.title


class Follow(models.Model):
    """User follow relationships"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"




class FriendRequest(models.Model):
    """Friend requests between users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"


class Notification(models.Model):
    """User notifications for follows, comments, etc."""
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
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='saves')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
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
    email_on_friend_request = models.BooleanField(default=True)
    email_on_friend_card = models.BooleanField(default=True)
    email_on_message = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s settings"




class Conversation(models.Model):
    """A conversation thread between two users, optionally about a specific card"""
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p2')
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        # Ensure unique conversation per card between two users
        unique_together = [['participant1', 'participant2', 'card']]
    
    def __str__(self):
        card_info = f" about {self.card.title}" if self.card else ""
        return f"{self.participant1.username} & {self.participant2.username}{card_info}"
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        return self.participant2 if user == self.participant1 else self.participant1
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by('-created_at').first()
    
    def unread_count_for_user(self, user):
        """Get count of unread messages for a specific user"""
        return self.messages.filter(recipient=user, is_read=False).count()


class DirectMessage(models.Model):
    """Individual messages within a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
    
    def get_status(self):
        if self.is_read and self.read_at:
            return 'seen'
        return 'delivered' 