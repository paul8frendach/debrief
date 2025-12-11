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
                ('general', 'General Research'),
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
    
    # Source tracking for Commons cards
    SOURCE_TYPE_CHOICES = [
        ('user', 'User Created'),
        ('commons', 'Debrief Commons'),
        ('public_figure', 'Public Figure (Unverified)'),
        ('verified', 'Verified Public Figure'),
    ]
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default='user')
    original_source = models.CharField(max_length=200, blank=True, null=True, help_text='Name of public figure or source')
    source_url = models.URLField(blank=True, null=True, help_text='Link to original content')
    synthesized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='synthesized_cards', help_text='User who created this synthesis')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'card')
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.card.title}"


class UserSettings(models.Model):
    """User privacy and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # Privacy settings
    allow_messages = models.BooleanField(default=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    email_on_friend_request = models.BooleanField(default=True)
    email_on_friend_card = models.BooleanField(default=True)
    email_on_message = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Profile information
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    STATE_CHOICES = [
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
        ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'District of Columbia'),
    ]
    
    home_state = models.CharField(max_length=2, blank=True, null=True, choices=STATE_CHOICES)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s settings"
    
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            self.user.email,
            self.mobile_number,
            self.home_state,
            self.profile_picture,
            self.bio,
            self.birthdate,
        ]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)
    
    def incomplete_fields(self):
        """Return list of incomplete profile fields"""
        incomplete = []
        if not self.user.email:
            incomplete.append('Email')
        if not self.mobile_number:
            incomplete.append('Mobile Number')
        if not self.home_state:
            incomplete.append('Home State')
        if not self.profile_picture:
            incomplete.append('Profile Picture')
        if not self.bio:
            incomplete.append('Bio')
        if not self.birthdate:
            incomplete.append('Birthdate')
        return incomplete




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

class CardVersion(models.Model):
    """Track changes to argument cards"""
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='versions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    hypothesis = models.TextField(max_length=500)
    conclusion = models.TextField(max_length=500)
    stance = models.CharField(max_length=20)
    version_number = models.IntegerField(default=1)
    change_summary = models.TextField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.card.title} - v{self.version_number}"


class NotebookEntry(models.Model):
    """User's personal research notes and saved links"""
    ENTRY_TYPES = [
        ('youtube', 'YouTube Video'),
        ('article', 'Article/Link'),
        ('note', 'Text Note'),
        ('quote', 'Quote'),
    ]
    
    STANCE_TYPES = [
        ('supporting', 'Supporting'),
        ('opposing', 'Opposing'),
        ('neutral', 'Neutral'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notebook_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()  # URL for links/videos, text for notes
    description = models.TextField(max_length=500, blank=True)
    NOTEBOOK_TOPICS = [
        ('general', 'General Research'),
        ('politics', 'Politics & Government'),
        ('healthcare', 'Healthcare & Medicine'),
        ('economy', 'Economy & Business'),
        ('education', 'Education'),
        ('environment', 'Environment & Climate'),
        ('technology', 'Technology & Science'),
        ('social', 'Social Issues'),
        ('international', 'International Affairs'),
        ('legal', 'Legal & Justice'),
        ('culture', 'Culture & Society'),
        ('other', 'Other'),
    ]
    
    topic = models.CharField(max_length=100, choices=NOTEBOOK_TOPICS)
    stance = models.CharField(max_length=20, choices=STANCE_TYPES, default='neutral')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notebook entries'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def get_youtube_id(self):
        """Extract YouTube video ID from URL"""
        if self.entry_type == 'youtube' and 'youtube.com' in self.content or 'youtu.be' in self.content:
            import re
            pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)'
            match = re.search(pattern, self.content)
            if match:
                return match.group(1)
        return None


class NotebookNote(models.Model):
    """Individual notes/points for a notebook entry"""
    entry = models.ForeignKey(NotebookEntry, on_delete=models.CASCADE, related_name='notes')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Note for {self.entry.title}: {self.text[:50]}"


class TopicSurvey(models.Model):
    """Survey questions for each policy topic"""
    topic = models.CharField(max_length=100, choices=Card.TOPIC_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(help_text='Context or stats about this topic')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Survey: {self.get_topic_display()}"


class SurveyQuestion(models.Model):
    """Individual questions for a topic survey"""
    survey = models.ForeignKey(TopicSurvey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    
    # Map question to card field
    MAPS_TO_CHOICES = [
        ('stance', 'Stance (For/Against)'),
        ('hypothesis', 'Hypothesis'),
        ('supporting', 'Supporting Argument'),
        ('opposing', 'Opposing Argument'),
        ('conclusion', 'Conclusion'),
        ('scope', 'Scope (Federal/State)'),
    ]
    maps_to = models.CharField(max_length=20, choices=MAPS_TO_CHOICES)
    
    # Context and educational content
    context_stats = models.TextField(blank=True, help_text='Bullet points with key statistics')
    learn_more = models.TextField(blank=True, help_text='Deeper explanation and background')
    sources = models.TextField(blank=True, help_text='Comma-separated URLs to credible sources')
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.survey.topic}: {self.question_text[:50]}"


class QuestionOption(models.Model):
    """Multiple choice options for each question"""
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=300)
    order = models.IntegerField(default=0)
    
    # What this option translates to in the card
    card_value = models.TextField(help_text='Text that will be used in the argument card')
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.option_text


# Update SurveyQuestion model with context fields
# (We'll use a migration to add these to existing model)


class PolicyFact(models.Model):
    """Store verifiable facts about policy topics"""
    topic = models.CharField(max_length=50, choices=Card.TOPIC_CHOICES)
    fact_text = models.TextField(help_text='The factual statement')
    source_name = models.CharField(max_length=200, help_text='Source organization')
    source_url = models.URLField()
    date_published = models.DateField(null=True, blank=True)
    last_verified = models.DateTimeField(auto_now=True)
    fact_type = models.CharField(max_length=50, choices=[
        ('statistic', 'Statistic'),
        ('study', 'Academic Study'),
        ('poll', 'Public Opinion Poll'),
        ('law', 'Legal/Policy Info'),
        ('comparison', 'International Comparison'),
    ])
    relevance_score = models.IntegerField(default=50, help_text='1-100, how relevant/important')
    
    class Meta:
        ordering = ['-relevance_score', '-last_verified']
        indexes = [
            models.Index(fields=['topic', '-relevance_score']),
        ]
    
    def __str__(self):
        return f"{self.get_topic_display()}: {self.fact_text[:50]}..."


class FactSource(models.Model):
    """Trusted sources for fact-checking"""
    name = models.CharField(max_length=200)
    base_url = models.URLField()
    api_endpoint = models.URLField(blank=True, help_text='API endpoint if available')
    api_key_required = models.BooleanField(default=False)
    credibility_rating = models.IntegerField(default=80, help_text='1-100')
    source_type = models.CharField(max_length=50, choices=[
        ('government', 'Government Agency'),
        ('academic', 'Academic Institution'),
        ('think_tank', 'Think Tank'),
        ('news', 'News Organization'),
        ('ngo', 'Non-Profit Organization'),
    ])
    topics = models.JSONField(default=list, help_text='List of topics this source covers')
    
    class Meta:
        ordering = ['-credibility_rating']
    
    def __str__(self):
        return self.name
