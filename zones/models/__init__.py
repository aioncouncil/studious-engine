# Defining models directly in this file
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import HappinessMetrics

class Sector(models.Model):
    """
    One of the 12 primary sectors of the city.
    Based on the EudaimoniaGo Core Gameplay Breakdown.
    """
    SECTOR_CHOICES = [
        (1, "Instruments"),
        (2, "Defenses"),
        (3, "Materials"),
        (4, "Health"),
        (5, "Ornaments"),
        (6, "Vessels"),
        (7, "Vehicles"),
        (8, "Labor"),
        (9, "Commerce"),
        (10, "Scripts"),
        (11, "Analysis"),
        (12, "Direction"),
    ]
    
    number = models.IntegerField(choices=SECTOR_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Governance
    is_governing = models.BooleanField(default=False)
    governing_start_date = models.DateTimeField(null=True, blank=True)
    governing_end_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Sector {self.number}: {self.name}"
    
    class Meta:
        ordering = ['number']


class Zone(models.Model):
    """
    A zone within a sector. Each sector has 420 zones.
    Each zone has a city (think tank) and country (production tank) portion.
    """
    ZONE_AREA_CHOICES = [
        ('agora', 'Agora (Connection)'),
        ('polis', 'Polis (Ideation)'),
        ('chora', 'Chora (Production)'),
    ]
    
    RANK_CHOICES = [
        (1, 'Rank 1'),
        (2, 'Rank 2'),
        (3, 'Rank 3'),
        (4, 'Rank 4'),
    ]
    
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="zones")
    zone_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(420)])
    zone_type = models.CharField(max_length=255)
    area = models.CharField(max_length=10, choices=ZONE_AREA_CHOICES)
    rank = models.IntegerField(choices=RANK_CHOICES, default=1)
    
    # Physical representation
    # These fields would store the real-world GPS coordinates for the zone
    city_latitude = models.FloatField(null=True, blank=True)
    city_longitude = models.FloatField(null=True, blank=True)
    country_latitude = models.FloatField(null=True, blank=True)
    country_longitude = models.FloatField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Zone {self.zone_number} (Type: {self.zone_type}) in {self.sector}"
    
    class Meta:
        unique_together = [['sector', 'zone_number']]
        ordering = ['sector', 'zone_number']


class ZoneHappiness(HappinessMetrics):
    """Zone happiness metrics."""
    zone = models.OneToOneField(Zone, on_delete=models.CASCADE, related_name="happiness")
    
    def __str__(self):
        return f"Happiness for {self.zone}"


class PlayerZoneContribution(models.Model):
    """Tracks a player's contributions to a specific zone."""
    player = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="zone_contributions")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="player_contributions")
    
    # Contribution metrics
    think_tank_contributions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    production_tank_contributions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    overall_influence = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Leadership status
    is_zone_leader = models.BooleanField(default=False)
    leadership_start_date = models.DateTimeField(null=True, blank=True)
    leadership_end_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.player}'s contribution to {self.zone}"
    
    class Meta:
        unique_together = [['player', 'zone']]
