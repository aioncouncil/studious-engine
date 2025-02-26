# Defining models directly in this file
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Innovation(models.Model):
    """
    Represents an innovation project following the Vitruvian Innovation Loop.
    """
    STAGE_CHOICES = [
        ('initiation', 'Initiation (0%)'),
        ('conception', 'Conception - Order & Arrangement (25%)'),
        ('refinement', 'Refinement - Eurythmy & Symmetry (50%)'),
        ('validation', 'Validation - Propriety (75%)'),
        ('implementation', 'Implementation - Economy (100%)'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Innovation categorization
    sector = models.ForeignKey('zones.Sector', on_delete=models.CASCADE, related_name="innovations")
    zones = models.ManyToManyField('zones.Zone', blank=True, related_name="innovations")
    
    # Current stage
    current_stage = models.CharField(max_length=15, choices=STAGE_CHOICES, default='initiation')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Innovation details for each stage
    # Order (Taxis)
    order_components = models.TextField(verbose_name="Identified Components", blank=True)
    order_metrics = models.TextField(verbose_name="Established Metrics", blank=True)
    
    # Arrangement (Diathesis)
    arrangement_ground_plan = models.TextField(verbose_name="Ground Plan", blank=True)
    arrangement_elevation = models.TextField(verbose_name="Elevation", blank=True)
    arrangement_perspective = models.TextField(verbose_name="Perspective", blank=True)
    
    # Eurythmy
    eurythmy_components = models.TextField(verbose_name="Component Optimizations", blank=True)
    
    # Symmetry
    symmetry_standard = models.TextField(verbose_name="Standard Unit", blank=True)
    symmetry_relations = models.TextField(verbose_name="Component Relations", blank=True)
    
    # Propriety
    propriety_principles = models.TextField(verbose_name="Principles", blank=True)
    propriety_justification = models.TextField(verbose_name="Justification", blank=True)
    
    # Economy
    economy_resources = models.TextField(verbose_name="Resource Management", blank=True)
    economy_implementation = models.TextField(verbose_name="Implementation Plan", blank=True)
    
    # Approval and implementation
    is_approved = models.BooleanField(default=False)
    implementation_date = models.DateTimeField(null=True, blank=True)
    
    # Metrics and impact
    expected_impact = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    actual_impact = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Tech Tree integration
    affects_tech_tree = models.BooleanField(default=False)
    tech_tree_node = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_current_stage_display()})"


class InnovationContribution(models.Model):
    """Tracks a player's contributions to an innovation project."""
    player = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="innovation_contributions")
    innovation = models.ForeignKey(Innovation, on_delete=models.CASCADE, related_name="player_contributions")
    
    # Contribution details
    stage = models.CharField(max_length=15, choices=Innovation.STAGE_CHOICES)
    contribution_description = models.TextField()
    impact_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Rewards
    experience_reward = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    happiness_reward = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Timestamps
    contributed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player}'s contribution to {self.innovation} at {self.get_stage_display()}"


class TechTreeNode(models.Model):
    """Represents a node in the city's Tech Tree."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Categorization
    sector = models.ForeignKey('zones.Sector', on_delete=models.CASCADE, related_name="tech_tree_nodes")
    level = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Relationships
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="unlocks")
    
    # Unlockable content
    unlocked_experiences = models.ManyToManyField('experiences.Experience', blank=True, related_name="unlocked_by_tech")
    unlocked_powers = models.ManyToManyField('experiences.Power', blank=True, related_name="unlocked_by_tech")
    
    # Status
    is_unlocked = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    
    # Innovation that unlocked this node
    unlocked_by_innovation = models.ForeignKey(Innovation, null=True, blank=True, on_delete=models.SET_NULL, related_name="unlocked_tech")
    
    # Visualization
    icon = models.CharField(max_length=255, blank=True)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"
    
    class Meta:
        ordering = ['level', 'name']
