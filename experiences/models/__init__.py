# Defining models directly in this file
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
        return f"{self.player}'s {self.power} (Level {self.level})"
    
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
        return f"{self.player}'s {self.experience} ({self.get_status_display()})"
    
    class Meta:
        unique_together = [['player', 'experience']]
