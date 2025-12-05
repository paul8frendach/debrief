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
        return f"From {self.sender.username} to {self.recipient.username}"