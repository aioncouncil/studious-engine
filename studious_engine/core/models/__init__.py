from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

# Import the Art System models
from .art import Art, ArtParts, ArtStage, ArtTaxonomy
from .art.tech_tree import TechTree
from .art.user_progress import ArtMastery, UserArtStageProgress, UserTechTreeProgress, PracticeSession

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class HappinessMetrics(models.Model):
    """Model for tracking the player's happiness metrics."""
    # Soul metrics
    wisdom = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    courage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    temperance = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    justice = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Body metrics
    strength = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    health = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    beauty = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    endurance = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Overall scores
    happiness = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    good_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    prosperity_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # History tracking
    virtue_history = models.JSONField(default=dict, blank=True)
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def calculate_happiness(self):
        """Calculate happiness scores from individual virtues."""
        self.good_score = (self.wisdom + self.courage + self.temperance + self.justice) / 4
        self.prosperity_score = (self.strength + self.health + self.beauty + self.endurance) / 4
        self.happiness = (self.good_score + self.prosperity_score) / 2
        self.last_calculated = timezone.now()
        return self.happiness
    
    def save(self, *args, **kwargs):
        """Calculate happiness scores before saving."""
        self.calculate_happiness()
        super().save(*args, **kwargs)


class PlayerProfile(models.Model):
    """Extended profile for game users."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    
    # Basic player info
    rank = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    experience_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Economic layer (Atlantis Go)
    ECONOMIC_LAYER_CHOICES = [
        ('port', 'Port'),
        ('laws', 'Laws'),
        ('republic', 'Republic'),
    ]
    economic_layer = models.CharField(
        max_length=10, 
        choices=ECONOMIC_LAYER_CHOICES,
        default='port'
    )
    
    # Profile data
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    title = models.CharField(max_length=100, default="Campus Explorer", blank=True)
    bio = models.TextField(blank=True, null=True)
    
    # Last known location (for GPS tracking) - will be moved to UserLocation in future
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # New Atlantis Go fields
    tutorial_progress = models.JSONField(default=dict, blank=True)
    device_settings = models.JSONField(default=dict, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def level(self):
        """Calculate player level based on experience points."""
        # Basic leveling formula - can be adjusted
        base_xp = 100
        if self.experience_points < base_xp:
            return 1
        return min(int((self.experience_points / base_xp) ** 0.4) + 1, 100)  # Cap at level 100


class PlayerHappiness(HappinessMetrics):
    """Player's happiness metrics."""
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE, related_name="happiness")

    def __str__(self):
        return f"{self.player.user.username}'s Happiness"


class UserPreferences(models.Model):
    """Model for storing user preferences."""
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE, related_name="preferences")
    
    # Preference fields
    interface_settings = models.JSONField(default=dict, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    privacy_settings = models.JSONField(default=dict, blank=True)
    ai_guide_settings = models.JSONField(default=dict, blank=True)
    language_preference = models.CharField(max_length=10, default='en')
    accessibility_options = models.JSONField(default=dict, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.player.user.username}'s Preferences"
    
    @classmethod
    def get_default_interface_settings(cls):
        """Default interface settings."""
        return {
            'theme': 'light',
            'fontSize': 'medium',
            'animations': True,
            'compactMode': False,
        }
    
    @classmethod
    def get_default_notification_preferences(cls):
        """Default notification preferences."""
        return {
            'experiences': True,
            'messages': True,
            'zoneUpdates': True,
            'artDiscovery': True,
            'achievements': True,
            'email': False,
            'push': True,
        }
    
    @classmethod
    def get_default_privacy_settings(cls):
        """Default privacy settings."""
        return {
            'profileVisibility': 'public',
            'locationSharing': 'friends',
            'activityVisibility': 'public',
            'artCollectionVisibility': 'public',
        }
    
    @classmethod
    def get_default_ai_guide_settings(cls):
        """Default AI guide settings."""
        return {
            'enabled': True,
            'proactiveHints': True,
            'conversationHistory': True,
            'voiceEnabled': False,
            'personalityType': 'balanced',
        }
    
    def save(self, *args, **kwargs):
        """Set default values for JSON fields if empty."""
        if not self.interface_settings:
            self.interface_settings = self.get_default_interface_settings()
        if not self.notification_preferences:
            self.notification_preferences = self.get_default_notification_preferences()
        if not self.privacy_settings:
            self.privacy_settings = self.get_default_privacy_settings()
        if not self.ai_guide_settings:
            self.ai_guide_settings = self.get_default_ai_guide_settings()
        if not self.accessibility_options:
            self.accessibility_options = {}
            
        super().save(*args, **kwargs)


class UserLocation(models.Model):
    """Model for tracking user location."""
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE, related_name="location")
    
    # Location data
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Will be linked to Zone model once that's implemented
    current_zone = models.ForeignKey(
        'zones.Zone', 
        on_delete=models.SET_NULL,
        related_name="current_players",
        null=True, blank=True
    )
    previous_zones = models.JSONField(default=list, blank=True)  # Store array of zone IDs
    accuracy_meters = models.FloatField(default=0)
    device_id = models.CharField(max_length=255, blank=True)
    
    # Tracking
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player.user.username}'s Location"
    
    def update_location(self, latitude, longitude, accuracy=None, device_id=None):
        """Update user location and track zone changes."""
        self.latitude = latitude
        self.longitude = longitude
        
        if accuracy:
            self.accuracy_meters = accuracy
        if device_id:
            self.device_id = device_id
            
        # Find current zone based on coordinates
        # Zone detection logic will be implemented later
        
        # Track previous zone if changed
        if self.current_zone and str(self.current_zone.id) not in self.previous_zones:
            zones = self.previous_zones.copy() if self.previous_zones else []
            zones.append(str(self.current_zone.id))
            # Keep only the 10 most recent zones
            self.previous_zones = zones[-10:]
            
        self.last_updated = timezone.now()
        self.save()


class MarketItem(models.Model):
    """Model representing items in the Unified Market System."""
    # Item details
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='market_items/', null=True, blank=True)
    
    # Economic model details
    LAYER_CHOICES = [
        ('outer', 'Port City (Outer Layer)'),
        ('middle', 'Laws Model (Middle Layer)'),
        ('inner', 'Republic Model (Inner Layer)')
    ]
    economic_layer = models.CharField(max_length=10, choices=LAYER_CHOICES, default='outer')
    
    # Price can be in credits or merit-based or contribution-based
    price = models.CharField(max_length=100, blank=True, null=True)
    price_type = models.CharField(max_length=50, default='credits', 
                                 choices=[('credits', 'Credits'), 
                                         ('merit', 'Merit-Based'), 
                                         ('contribution', 'Contribution-Based')])
    
    # Categories
    CATEGORY_CHOICES = [
        ('physical', 'Physical Goods'),
        ('service', 'Services'),
        ('digital', 'Digital Assets'),
        ('investment', 'Investments'),
        ('skill', 'Skills & Knowledge'),
        ('experience', 'Experiences'),
        ('collaboration', 'Collaborative Opportunities'),
        ('resource', 'Resource Sharing')
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Availability
    is_available = models.BooleanField(default=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # Access requirements - which classes or ranks can access this item
    min_rank_required = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Featured and recommendation status
    is_featured = models.BooleanField(default=False)
    recommendation_score = models.FloatField(default=0)
    
    # Atlantis Go additions
    seller_id = models.UUIDField(null=True, blank=True)
    SELLER_TYPE_CHOICES = [
        ('user', 'User'),
        ('zone', 'Zone'),
        ('team', 'Team'),
        ('system', 'System')
    ]
    seller_type = models.CharField(max_length=10, choices=SELLER_TYPE_CHOICES, default='system')
    reference_id = models.UUIDField(null=True, blank=True)  # ID of the referenced entity (item, resource, art, etc.)
    
    def __str__(self):
        return self.name
    
    @property
    def is_outer_layer(self):
        return self.economic_layer == 'outer'
    
    @property
    def is_middle_layer(self):
        return self.economic_layer == 'middle'
    
    @property
    def is_inner_layer(self):
        return self.economic_layer == 'inner'


class Wishlist(models.Model):
    """Model for storing user wishlisted/favorited market items."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    item = models.ForeignKey(MarketItem, on_delete=models.CASCADE, related_name="wishlist_users")
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'item')  # Prevent duplicate wishlist entries
    
    def __str__(self):
        return f"{self.user.username}'s wishlist: {self.item.name}"


class Artifact(models.Model):
    """
    Represents a digital or physical artifact created during experiences or innovation processes.
    Artifacts can be collected, shared, and used as evidence of learning or creation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Creator and ownership
    creator = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="created_artifacts")
    collaborators = models.ManyToManyField(PlayerProfile, blank=True, related_name="collaborated_artifacts")
    
    # Artifact categorization
    ARTIFACT_TYPE_CHOICES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('model', '3D Model'),
        ('code', 'Code'),
        ('design', 'Design'),
        ('physical', 'Physical Object'),
        ('other', 'Other')
    ]
    artifact_type = models.CharField(max_length=15, choices=ARTIFACT_TYPE_CHOICES)
    
    # Content and media
    media_url = models.URLField(blank=True)
    media_file = models.FileField(upload_to='artifacts/', blank=True, null=True)
    content = models.TextField(blank=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Relationships
    related_art = models.ForeignKey('core.Art', on_delete=models.SET_NULL, null=True, blank=True, related_name="art_artifacts")
    related_experience = models.ForeignKey('experiences.Experience', on_delete=models.SET_NULL, null=True, blank=True, related_name="experience_artifacts")
    
    # Visibility and sharing
    is_public = models.BooleanField(default=False)
    
    # Validation and quality
    is_validated = models.BooleanField(default=False)
    validator = models.ForeignKey(PlayerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="validated_artifacts")
    validation_date = models.DateTimeField(null=True, blank=True)
    quality_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_artifact_type_display()})"
    
    def validate(self, validator, quality_rating=None):
        """Mark the artifact as validated by a specific user."""
        self.is_validated = True
        self.validator = validator
        self.validation_date = timezone.now()
        if quality_rating:
            self.quality_rating = quality_rating
        self.save()
        
    class Meta:
        ordering = ['-created_at']


class MediaAsset(models.Model):
    """
    Represents a media asset that can be attached to various entities in the system.
    This provides a unified way to handle media across the application.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Asset details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Media content
    file = models.FileField(upload_to='media_assets/')
    thumbnail = models.ImageField(upload_to='media_assets/thumbnails/', null=True, blank=True)
    
    # Media type
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('other', 'Other')
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    
    # Metadata
    file_size = models.IntegerField(default=0)  # Size in bytes
    duration = models.IntegerField(null=True, blank=True)  # Duration in seconds for audio/video
    dimensions = models.CharField(max_length=50, blank=True)  # Format: "WIDTHxHEIGHT" for images/videos
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Creator and ownership
    creator = models.ForeignKey(PlayerProfile, on_delete=models.SET_NULL, null=True, related_name="created_media")
    
    # Permissions
    is_public = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"
    
    def get_url(self):
        """Get the URL for this media asset."""
        if self.file:
            return self.file.url
        return None
    
    class Meta:
        ordering = ['-created_at']
