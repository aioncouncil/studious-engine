from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class HappinessMetrics(models.Model):
    """Model for tracking the player's happiness metrics."""
    # Soul metrics
    wisdom = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    courage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    temperance = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    justice = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Body metrics
    strength = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    wealth = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    beauty = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    health = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Environment metrics
    resources = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    friendships = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    honors = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    glory = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        abstract = True
    
    @property
    def soul_average(self):
        """Calculate average soul happiness."""
        return (self.wisdom + self.courage + self.temperance + self.justice) / 4
    
    @property
    def body_average(self):
        """Calculate average body happiness."""
        return (self.strength + self.wealth + self.beauty + self.health) / 4
    
    @property
    def environment_average(self):
        """Calculate average environment happiness."""
        return (self.resources + self.friendships + self.honors + self.glory) / 4
    
    @property
    def total_happiness(self):
        """Calculate total happiness score."""
        return (self.soul_average + self.body_average + self.environment_average) / 3


class PlayerProfile(models.Model):
    """Extended profile for game users."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    
    # Basic player info
    rank = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    experience_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Last known location (for GPS tracking)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class PlayerHappiness(HappinessMetrics):
    """Player's happiness metrics."""
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE, related_name="happiness")

    def __str__(self):
        return f"{self.player.user.username}'s Happiness"
