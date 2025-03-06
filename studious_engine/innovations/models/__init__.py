# Defining models directly in this file
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

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


class InnovationProcess(models.Model):
    """
    Represents a structured innovation process following the Vitruvian principles.
    This is an enhanced version of the Innovation model with more detailed tracking
    and integration with the Atlantis Go system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    initiator = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="initiated_innovations")
    zone = models.ForeignKey('zones.Zone', on_delete=models.CASCADE, related_name="zone_innovations")
    
    # Innovation type and categorization
    INNOVATION_TYPE_CHOICES = [
        ('product', 'Product Innovation'),
        ('process', 'Process Innovation'),
        ('service', 'Service Innovation'),
        ('social', 'Social Innovation'),
        ('governance', 'Governance Innovation'),
        ('educational', 'Educational Innovation'),
    ]
    innovation_type = models.CharField(max_length=20, choices=INNOVATION_TYPE_CHOICES)
    
    # Current stage in the Vitruvian process
    STAGE_CHOICES = [
        ('order', 'Order'),
        ('arrangement', 'Arrangement'),
        ('eurythmy', 'Eurythmy'),
        ('symmetry', 'Symmetry'),
        ('propriety', 'Propriety'),
        ('economy', 'Economy'),
    ]
    current_stage = models.CharField(max_length=15, choices=STAGE_CHOICES, default='order')
    
    # Detailed progress tracking for each stage
    stage_progress = models.JSONField(default=dict, blank=True, help_text="Tracking progress in each stage")
    
    # Related artifacts and participants
    artifacts = models.ManyToManyField('core.Artifact', blank=True, related_name="innovation_artifacts")
    participants = models.ManyToManyField('core.PlayerProfile', blank=True, related_name="participating_innovations")
    
    # Problem and solution details
    problem_statement = models.TextField()
    proposed_solution = models.TextField()
    
    # Validation metrics
    validation_metrics = models.JSONField(default=dict, blank=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_current_stage_display()})"
    
    def initialize_stage_progress(self):
        """Initialize the stage_progress JSON structure."""
        if not self.stage_progress:
            self.stage_progress = {
                'order': {
                    'completed': False,
                    'progress': 0,
                    'components': [],
                    'metrics': []
                },
                'arrangement': {
                    'completed': False,
                    'progress': 0,
                    'ground_plan': '',
                    'elevation': '',
                    'perspective': ''
                },
                'eurythmy': {
                    'completed': False,
                    'progress': 0,
                    'optimizations': []
                },
                'symmetry': {
                    'completed': False,
                    'progress': 0,
                    'standard': '',
                    'relations': []
                },
                'propriety': {
                    'completed': False,
                    'progress': 0,
                    'principles': [],
                    'justification': ''
                },
                'economy': {
                    'completed': False,
                    'progress': 0,
                    'resources': {},
                    'implementation_plan': ''
                }
            }
            self.save()
    
    def advance_stage(self):
        """Advance to the next stage if current stage is complete."""
        if not self.stage_progress:
            self.initialize_stage_progress()
            
        current = self.current_stage
        if self.stage_progress[current]['completed']:
            stages = [choice[0] for choice in self.STAGE_CHOICES]
            current_index = stages.index(current)
            
            if current_index < len(stages) - 1:
                self.current_stage = stages[current_index + 1]
                self.save()
                return True
            else:
                # Final stage complete
                self.status = 'completed'
                self.save()
                return True
        return False
    
    def calculate_overall_progress(self):
        """Calculate the overall progress percentage across all stages."""
        if not self.stage_progress:
            self.initialize_stage_progress()
            
        stages = [choice[0] for choice in self.STAGE_CHOICES]
        stage_weights = {stage: 1/len(stages) for stage in stages}
        
        total_progress = 0
        for stage, data in self.stage_progress.items():
            if data['completed']:
                total_progress += stage_weights[stage]
            else:
                total_progress += stage_weights[stage] * (data['progress'] / 100)
                
        return round(total_progress * 100)


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
