# Defining models directly in this file
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import HappinessMetrics
import uuid
from django.utils import timezone

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

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
    
    # Description
    description = models.TextField(blank=True)
    
    # Location information
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Physical representation
    # These fields would store the real-world GPS coordinates for the zone
    city_latitude = models.FloatField(null=True, blank=True)
    city_longitude = models.FloatField(null=True, blank=True)
    country_latitude = models.FloatField(null=True, blank=True)
    country_longitude = models.FloatField(null=True, blank=True)
    
    # Moderation status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Zone {self.sector.number}.{self.zone_number} - {self.zone_type}"
    
    class Meta:
        unique_together = [['sector', 'zone_number']]
        ordering = ['sector', 'zone_number']


class ZoneHappiness(HappinessMetrics):
    """Zone happiness metrics."""
    zone = models.OneToOneField(Zone, on_delete=models.CASCADE, related_name="happiness")
    
    def __str__(self):
        return f"Happiness Metrics for {self.zone}"


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


class ZoneHierarchy(models.Model):
    """
    Defines hierarchical relationships between zones.
    Allows for nested governance structures and zone networks.
    """
    RELATIONSHIP_TYPE_CHOICES = [
        ('parent_child', 'Parent-Child'), 
        ('alliance', 'Alliance'),
        ('network', 'Network'),
        ('satellite', 'Satellite'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="child_relationships")
    child_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="parent_relationships")
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPE_CHOICES)
    
    # Relationship properties
    influence_weight = models.FloatField(default=1.0, 
                                        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
                                        help_text="How much influence flows through this relationship")
    resource_sharing_percentage = models.FloatField(default=0.0, 
                                                  validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                                  help_text="Percentage of resources shared between zones")
    
    # Relationship status
    is_active = models.BooleanField(default=True)
    formation_date = models.DateTimeField(auto_now_add=True)
    dissolution_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.parent_zone} → {self.child_zone} ({self.get_relationship_type_display()})"
    
    class Meta:
        unique_together = [['parent_zone', 'child_zone', 'relationship_type']]
        verbose_name_plural = "Zone Hierarchies"


class ZoneMembership(models.Model):
    """
    Tracks a player's membership in zones beyond simple contributions.
    Includes roles, permissions, and membership history.
    """
    MEMBERSHIP_TYPE_CHOICES = [
        ('resident', 'Resident'),
        ('citizen', 'Citizen'),
        ('contributor', 'Contributor'),
        ('leader', 'Leader'),
        ('founder', 'Founder'),
        ('visitor', 'Visitor'),
    ]
    
    MEMBERSHIP_STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('banned', 'Banned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="zone_memberships")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="memberships")
    
    # Membership details
    membership_type = models.CharField(max_length=15, choices=MEMBERSHIP_TYPE_CHOICES, default='visitor')
    status = models.CharField(max_length=10, choices=MEMBERSHIP_STATUS_CHOICES, default='pending')
    
    # Permissions and benefits
    has_voting_rights = models.BooleanField(default=False)
    resource_access_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    reputation_score = models.IntegerField(default=0, validators=[MinValueValidator(-100), MaxValueValidator(100)])
    
    # Time tracking
    join_date = models.DateTimeField(default=timezone.now)
    last_active_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField(null=True, blank=True)
    
    # Administrative
    approved_by = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name="approved_memberships")
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.player} - {self.zone} ({self.get_membership_type_display()})"
    
    class Meta:
        unique_together = [['player', 'zone']]
        verbose_name_plural = "Zone Memberships"
        
    def is_current(self):
        """Check if membership is currently valid."""
        if self.expiration_date and self.expiration_date < timezone.now():
            return False
        return self.status == 'active'


class ZoneResources(models.Model):
    """
    Tracks the resources available in a zone.
    These can be natural resources, manufactured goods, or intellectual capital.
    """
    RESOURCE_CATEGORY_CHOICES = [
        ('natural', 'Natural Resource'),
        ('manufactured', 'Manufactured Good'),
        ('intellectual', 'Intellectual Capital'),
        ('social', 'Social Capital'),
        ('financial', 'Financial Resource'),
    ]
    
    SCARCITY_LEVEL_CHOICES = [
        (1, 'Abundant'),
        (2, 'Common'),
        (3, 'Uncommon'),
        (4, 'Rare'),
        (5, 'Extremely Rare'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="resources")
    
    # Resource details
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=15, choices=RESOURCE_CATEGORY_CHOICES)
    
    # Quantity and availability
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_capacity = models.IntegerField(validators=[MinValueValidator(1)])
    regeneration_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    scarcity_level = models.IntegerField(choices=SCARCITY_LEVEL_CHOICES, default=2)
    
    # Economic properties
    base_value = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    current_market_value = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    is_tradable = models.BooleanField(default=True)
    
    # Access control
    is_public = models.BooleanField(default=True)
    minimum_rank_to_access = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    
    # Geographic details
    latitude = models.FloatField(null=True, blank=True, help_text="Geographic location of resource")
    longitude = models.FloatField(null=True, blank=True, help_text="Geographic location of resource")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} in {self.zone}"
    
    class Meta:
        verbose_name_plural = "Zone Resources"
        ordering = ['zone', 'name']
    
    @property
    def is_depleted(self):
        """Check if the resource is depleted."""
        return self.quantity <= 0
    
    @property
    def percentage_available(self):
        """Return the percentage of resource available compared to max capacity."""
        if self.max_capacity <= 0:
            return 0
        return (self.quantity / self.max_capacity) * 100


class ResourceFlow(models.Model):
    """
    Tracks the flow of resources between zones.
    This includes trades, gifts, and resource reallocations.
    """
    FLOW_TYPE_CHOICES = [
        ('trade', 'Trade'),
        ('donation', 'Donation'),
        ('tax', 'Tax Collection'),
        ('subsidy', 'Subsidy'),
        ('reallocation', 'Reallocation'),
        ('production', 'Production Output'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source and destination
    source_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="outgoing_flows")
    destination_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="incoming_flows")
    
    # Flow properties
    resource = models.ForeignKey(ZoneResources, on_delete=models.CASCADE, related_name="flows")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    flow_type = models.CharField(max_length=15, choices=FLOW_TYPE_CHOICES)
    
    # Status tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Timing
    initiated_at = models.DateTimeField(auto_now_add=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Economic details
    value = models.IntegerField(validators=[MinValueValidator(0)])
    tax_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Participants
    initiated_by = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, 
                                  null=True, related_name="initiated_flows")
    approved_by = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name="approved_flows")
    
    # Notes and conditions
    notes = models.TextField(blank=True)
    conditions = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.flow_type}: {self.quantity} {self.resource.name} from {self.source_zone} to {self.destination_zone}"
    
    class Meta:
        verbose_name_plural = "Resource Flows"
        ordering = ['-initiated_at']
    
    def calculate_tax(self):
        """Calculate the tax amount for this resource flow."""
        return int(self.value * self.tax_rate)
    
    def mark_completed(self, completion_time=None):
        """Mark the resource flow as completed."""
        self.status = 'completed'
        self.completed_at = completion_time or timezone.now()
        self.save()


class ZoneActivity(models.Model):
    """
    Records activities happening within zones.
    These can be events, projects, initiatives, or gatherings.
    """
    ACTIVITY_TYPE_CHOICES = [
        ('event', 'Community Event'),
        ('project', 'Community Project'),
        ('initiative', 'Zone Initiative'),
        ('gathering', 'Zone Gathering'),
        ('competition', 'Zone Competition'),
        ('celebration', 'Zone Celebration'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('recurring', 'Recurring'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="activities")
    
    # Activity details
    name = models.CharField(max_length=255)
    description = models.TextField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    
    # Status and progress
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planned')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    recurrence_pattern = models.JSONField(default=dict, blank=True)
    
    # Resources and rewards
    required_resources = models.JSONField(default=dict, blank=True)
    happiness_impact = models.IntegerField(default=0)
    resource_generation = models.JSONField(default=dict, blank=True)
    
    # Participants
    organizer = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, 
                               null=True, related_name="organized_activities")
    max_participants = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    participants = models.ManyToManyField('core.PlayerProfile', blank=True, related_name="participated_activities")
    
    # Physical location within zone
    location_description = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_activity_type_display()}) in {self.zone}"
    
    class Meta:
        verbose_name_plural = "Zone Activities"
        ordering = ['-start_date']
    
    @property
    def is_active(self):
        """Check if activity is currently active."""
        now = timezone.now()
        return (self.status == 'in_progress' and 
                self.start_date <= now and 
                (self.end_date is None or self.end_date >= now))
    
    def get_participant_count(self):
        """Get the current number of participants."""
        return self.participants.count()


class ZoneRaid(models.Model):
    """
    Models raids between zones, where players from one zone target another
    for resources, territory, or influence.
    """
    RAID_TYPE_CHOICES = [
        ('resource', 'Resource Raid'),
        ('territory', 'Territory Raid'),
        ('influence', 'Influence Raid'),
        ('knowledge', 'Knowledge Raid'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Participating zones
    attacking_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="outgoing_raids")
    defending_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="incoming_raids")
    
    # Raid details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    raid_type = models.CharField(max_length=15, choices=RAID_TYPE_CHOICES)
    
    # Status and progress
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planned')
    
    # Timing
    planned_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Raid mechanics
    target_resources = models.ManyToManyField(ZoneResources, blank=True, related_name="targeted_in_raids")
    attacking_strength = models.IntegerField(validators=[MinValueValidator(1)])
    defending_strength = models.IntegerField(validators=[MinValueValidator(0)])
    success_probability = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Outcomes
    resources_gained = models.JSONField(default=dict, blank=True)
    damage_inflicted = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    influence_change = models.IntegerField(default=0)
    
    # Participants
    raid_leader = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, 
                                  null=True, related_name="led_raids")
    attackers = models.ManyToManyField('core.PlayerProfile', blank=True, related_name="participated_attacks")
    defenders = models.ManyToManyField('core.PlayerProfile', blank=True, related_name="participated_defenses")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}: {self.attacking_zone} → {self.defending_zone}"
    
    class Meta:
        verbose_name_plural = "Zone Raids"
        ordering = ['-planned_start']
    
    def calculate_success_probability(self):
        """Calculate the probability of raid success based on strengths."""
        if self.attacking_strength + self.defending_strength == 0:
            return 0.5
        return self.attacking_strength / (self.attacking_strength + self.defending_strength)
    
    def execute_raid(self):
        """Execute the raid and determine outcome."""
        if self.status != 'in_progress':
            return False
        
        # Update success probability
        self.success_probability = self.calculate_success_probability()
        
        # Determine success or failure
        import random
        outcome = random.random()
        
        if outcome <= self.success_probability:
            self.status = 'succeeded'
            # Logic for successful raid
        else:
            self.status = 'failed'
            # Logic for failed raid
        
        self.end_time = timezone.now()
        self.save()
        return True


class ZoneDeficiency(models.Model):
    """
    Tracks resource or capability deficiencies in a zone.
    Used to guide player actions and zone development.
    """
    DEFICIENCY_TYPE_CHOICES = [
        ('resource', 'Resource Shortage'),
        ('skill', 'Skill Gap'),
        ('infrastructure', 'Infrastructure Need'),
        ('leadership', 'Leadership Vacancy'),
        ('population', 'Population Deficiency'),
        ('happiness', 'Happiness Issue'),
    ]
    
    SEVERITY_CHOICES = [
        (1, 'Minor'),
        (2, 'Moderate'),
        (3, 'Significant'),
        (4, 'Severe'),
        (5, 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="deficiencies")
    
    # Deficiency details
    title = models.CharField(max_length=255)
    description = models.TextField()
    deficiency_type = models.CharField(max_length=15, choices=DEFICIENCY_TYPE_CHOICES)
    
    # Measurement
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=2)
    current_value = models.IntegerField(default=0)
    target_value = models.IntegerField(validators=[MinValueValidator(1)])
    percentage_completed = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    # Status and visibility
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Resolution
    resolution_plan = models.TextField(blank=True)
    assigned_to = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name="assigned_deficiencies")
    resolution_deadline = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Incentives
    completion_reward = models.JSONField(default=dict, blank=True)
    happiness_impact = models.IntegerField(default=-10)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()}) in {self.zone}"
    
    class Meta:
        verbose_name_plural = "Zone Deficiencies"
        ordering = ['-severity', 'created_at']
    
    def update_progress(self, new_value):
        """Update the progress towards resolving the deficiency."""
        self.current_value = new_value
        if self.target_value > 0:
            self.percentage_completed = min(100.0, (self.current_value / self.target_value) * 100)
        
        # Check if deficiency is resolved
        if self.current_value >= self.target_value:
            self.is_active = False
            self.resolved_at = timezone.now()
        
        self.save()
    
    @property
    def is_resolved(self):
        """Check if the deficiency has been resolved."""
        return not self.is_active and self.resolved_at is not None
