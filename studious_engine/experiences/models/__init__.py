# Defining models directly in this file
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class Power(models.Model):
    """
    Powers represent skills, ideas, or technologies that players can master.
    Similar to catching Pokémon in Pokémon Go.
    """
    TYPE_CHOICES = [
        ('idea', 'Idea'),
        ('skill', 'Skill'),
        ('technology', 'Technology'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    power_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    
    # Power attributes
    rarity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    complexity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Categorization
    sector = models.ForeignKey('zones.Sector', on_delete=models.SET_NULL, null=True, related_name="powers")
    
    # Visibility and acquisition
    is_public = models.BooleanField(default=True)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="unlocks")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_power_type_display()})"


class PlayerPower(models.Model):
    """Records a player's acquisition and mastery of a Power."""
    player = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="powers")
    power = models.ForeignKey(Power, on_delete=models.CASCADE, related_name="player_powers")
    
    # Mastery level
    level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    experience = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Timestamps
    acquired_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.player.user.username}'s {self.power.name} (Level {self.level})"
    
    class Meta:
        unique_together = [['player', 'power']]


class Experience(models.Model):
    """
    Experiences are activities or tasks that players can engage in.
    They form the core gameplay loop: Pull -> Think -> Do -> Review.
    """
    TYPE_CHOICES = [
        ('quest', 'Quest'),
        ('challenge', 'Challenge'),
        ('collaboration', 'Collaboration'),
        ('innovation', 'Innovation'),
        ('reflection', 'Reflection'),
    ]
    
    MATRIX_CHOICES = [
        ('soul_out', 'Soul Out (Think Tank)'),
        ('soul_in', 'Soul In (Review)'),
        ('body_out', 'Body Out (Production Tank)'),
        ('body_in', 'Body In (Market)'),
    ]
    
    ART_TYPE_CHOICES = [
        ('imitation', 'Imitation'),
        ('production', 'Production'),
        ('usage', 'Usage'),
    ]
    
    GOOD_TYPE_CHOICES = [
        ('present', 'Present Good'),
        ('present_future', 'Present/Future Good'),
        ('future', 'Future Good'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Categorization
    experience_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    matrix_position = models.CharField(max_length=10, choices=MATRIX_CHOICES)
    art_type = models.CharField(max_length=10, choices=ART_TYPE_CHOICES)
    good_type = models.CharField(max_length=15, choices=GOOD_TYPE_CHOICES)
    
    # Physical location for map display
    latitude = models.FloatField(null=True, blank=True, help_text="Geographic latitude for displaying on the map")
    longitude = models.FloatField(null=True, blank=True, help_text="Geographic longitude for displaying on the map")
    
    # Difficulty and rewards
    difficulty = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    happiness_reward = models.IntegerField(validators=[MinValueValidator(0)])
    experience_reward = models.IntegerField(validators=[MinValueValidator(0)])
    
    # References
    required_powers = models.ManyToManyField(Power, blank=True, related_name="required_for_experiences")
    associated_zones = models.ManyToManyField('zones.Zone', blank=True, related_name="experiences")
    prerequisite_experiences = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="unlocks")
    
    # Structure
    definition = models.TextField(verbose_name="What it is")
    end = models.TextField(verbose_name="Its purpose")
    parts = models.TextField(verbose_name="Its components")
    matter = models.TextField(verbose_name="The materials it uses")
    instrument = models.TextField(verbose_name="The tools it requires")
    
    # Visibility and availability
    is_active = models.BooleanField(default=True)
    minimum_rank = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_experience_type_display()})"


class ExperienceInstance(models.Model):
    """
    Represents a specific instance of an experience that is happening in the world.
    An Experience is a template, while ExperienceInstance is a concrete occurrence.
    """
    FREQUENCY_CHOICES = [
        ('once', 'One-time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Schedule'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name="instances")
    name = models.CharField(max_length=255, blank=True, 
                           help_text="Optional custom name for this instance. Defaults to experience name.")
    
    # Instance details
    host = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, null=True, 
                            related_name="hosted_experiences")
    zone = models.ForeignKey('zones.Zone', on_delete=models.SET_NULL, null=True, 
                            related_name="zone_experience_instances")
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='once')
    recurrence_rule = models.JSONField(default=dict, blank=True, 
                                     help_text="JSON data for recurring instances")
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    capacity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    current_participants = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_public = models.BooleanField(default=True)
    
    # Location specifics (can be different from the general experience location)
    location_description = models.CharField(max_length=255, blank=True)
    meeting_point = models.JSONField(default=dict, blank=True, 
                                    help_text="JSON data for specific meeting coordinates")
    
    # Matrix flow tracking
    current_matrix_phase = models.CharField(max_length=10, choices=Experience.MATRIX_CHOICES, 
                                          null=True, blank=True)
    matrix_flow_data = models.JSONField(default=dict, blank=True, 
                                     help_text="Data tracking the flow through different matrix quadrants")
    
    # Resources and outcomes
    resources_provided = models.JSONField(default=dict, blank=True)
    outcomes = models.JSONField(default=dict, blank=True, 
                             help_text="Aggregate outcomes across all participants")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Experience Instance"
        verbose_name_plural = "Experience Instances"
        ordering = ['-start_time']
    
    def __str__(self):
        instance_name = self.name if self.name else self.experience.name
        return f"{instance_name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    def save(self, *args, **kwargs):
        # Set default name if not provided
        if not self.name:
            self.name = self.experience.name
        
        # Set default end time if not provided
        if not self.end_time and self.start_time:
            self.end_time = self.start_time + timezone.timedelta(minutes=self.experience.duration_minutes)
            
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        now = timezone.now()
        return (self.status == 'active' and 
                self.start_time <= now and 
                (not self.end_time or self.end_time > now))
    
    @property
    def is_full(self):
        return self.current_participants >= self.capacity
    
    def add_participant(self, player):
        """Add a participant to this experience instance."""
        if self.is_full:
            return False
        
        # Create a participation record
        participation, created = ExperienceParticipation.objects.get_or_create(
            instance=self,
            player=player,
            defaults={
                'status': 'active'
            }
        )
        
        if created:
            self.current_participants += 1
            self.save()
            return True
        
        return False
    
    def remove_participant(self, player):
        """Remove a participant from this experience instance."""
        try:
            participation = ExperienceParticipation.objects.get(
                instance=self,
                player=player
            )
            participation.status = 'withdrawn'
            participation.withdrawn_at = timezone.now()
            participation.save()
            
            self.current_participants -= 1
            self.save()
            return True
        except ExperienceParticipation.DoesNotExist:
            return False
    
    def advance_matrix_phase(self):
        """Advance to the next matrix phase."""
        phases = [choice[0] for choice in Experience.MATRIX_CHOICES]
        
        if not self.current_matrix_phase:
            self.current_matrix_phase = phases[0]
        else:
            current_index = phases.index(self.current_matrix_phase)
            if current_index < len(phases) - 1:
                self.current_matrix_phase = phases[current_index + 1]
            else:
                # Completed all phases
                self.status = 'completed'
        
        self.save()
        return self.current_matrix_phase


class ExperienceParticipation(models.Model):
    """
    Records a player's participation in a specific experience instance.
    """
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(ExperienceInstance, on_delete=models.CASCADE, 
                                related_name="participations")
    player = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, 
                              related_name="experience_participations")
    
    # Status and progress
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='invited')
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    
    # Player's contributions and outcomes
    contributions = models.JSONField(default=dict, blank=True)
    personal_outcomes = models.JSONField(default=dict, blank=True)
    
    # Feedback
    feedback = models.TextField(blank=True)
    satisfaction_rating = models.IntegerField(null=True, blank=True, 
                                            validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Rewards
    happiness_gained = models.IntegerField(default=0)
    experience_gained = models.IntegerField(default=0)
    resources_gained = models.JSONField(default=dict, blank=True)
    
    # Matrix flow tracking for this participant
    individual_flow_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Experience Participation"
        verbose_name_plural = "Experience Participations"
        unique_together = [['instance', 'player']]
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.player.user.username}'s participation in {self.instance}"
    
    def complete(self):
        """Mark this participation as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        # Calculate rewards based on the experience
        experience = self.instance.experience
        self.happiness_gained = experience.happiness_reward
        self.experience_gained = experience.experience_reward
        
        # Record the rewards for the player
        player = self.player
        
        # Apply experience points
        player.experience_points += self.experience_gained
        player.save()
        
        # Apply happiness (ideally this would update the happiness metrics model)
        # This is simplified - a real implementation would update specific virtue metrics
        
        self.save()
        return True


class PlayerExperience(models.Model):
    """Records a player's participation in an Experience."""
    STATUS_CHOICES = [
        ('pull', 'Pull - Identified'),
        ('think', 'Think - Planning'),
        ('do', 'Do - Implementing'),
        ('review', 'Review - Evaluating'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    player = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="experiences")
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name="player_experiences")
    
    # Progress tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pull')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    reflection_notes = models.TextField(blank=True)
    
    # Resources committed
    resources_committed = models.JSONField(default=dict, blank=True)
    
    # Rewards received
    happiness_gained = models.IntegerField(default=0)
    experience_gained = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.player.user.username}'s {self.experience.name} ({self.get_status_display()})"
    
    class Meta:
        unique_together = [['player', 'experience']]
