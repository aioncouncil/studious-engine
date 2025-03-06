from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
import uuid

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class ArtTaxonomy(models.Model):
    """
    Categorization system for arts.
    """
    TAXONOMY_LEVELS = (
        (1, _('Category')),
        (2, _('Subcategory')),
        (3, _('Specialty')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    parent = models.ForeignKey(
        'self', 
        verbose_name=_('Parent Taxonomy'),
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='children'
    )
    level = models.IntegerField(_('Level'), choices=TAXONOMY_LEVELS, default=1)
    path = models.CharField(_('Path'), max_length=255, blank=True)
    icon = models.CharField(_('Icon Path'), max_length=255, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Art Taxonomy')
        verbose_name_plural = _('Art Taxonomies')
        ordering = ['level', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Update path when saving"""
        if self.parent:
            self.path = f"{self.parent.path}/{self.id}"
        else:
            self.path = f"{self.id}"
        super().save(*args, **kwargs)
    
    def get_full_path_display(self):
        """Return human-readable taxonomy path"""
        if self.parent:
            return f"{self.parent.get_full_path_display()} > {self.name}"
        return self.name


class Art(models.Model):
    """
    Base model representing a creative practice that can be learned and mastered.
    """
    DIFFICULTY_LEVELS = (
        (1, _('Beginner')),
        (2, _('Intermediate')),
        (3, _('Advanced')),
        (4, _('Expert')),
        (5, _('Master')),
    )
    
    ECONOMIC_LAYERS = (
        ('PORT', _('Port')),
        ('LAWS', _('Laws')),
        ('REPUBLIC', _('Republic')),
    )
    
    PRACTICE_METHODS = (
        ('SOLO', _('Solo')),
        ('PAIR', _('Pair')),
        ('GROUP', _('Group')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    icon = models.CharField(_('Icon Path'), max_length=255, blank=True)
    banner_image = models.CharField(_('Banner Image Path'), max_length=255, blank=True)
    difficulty_level = models.IntegerField(_('Difficulty Level'), choices=DIFFICULTY_LEVELS, default=1)
    creation_date = models.DateTimeField(_('Creation Date'), auto_now_add=True)
    taxonomy = models.ForeignKey(
        ArtTaxonomy, 
        verbose_name=_('Taxonomy'),
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='arts'
    )
    parent_arts = models.ManyToManyField(
        'self', 
        verbose_name=_('Parent Arts'),
        symmetrical=False,
        blank=True,
        related_name='child_arts'
    )
    required_virtues = models.JSONField(_('Required Virtues'), default=dict, blank=True)
    improved_virtues = models.JSONField(_('Improved Virtues'), default=dict, blank=True)
    tech_tree_level = models.IntegerField(_('Tech Tree Level'), default=1)
    is_unlocked_default = models.BooleanField(_('Unlocked by Default'), default=False)
    rank_required = models.IntegerField(_('Rank Required'), default=1)
    economic_layer_required = models.CharField(
        _('Economic Layer Required'),
        max_length=20,
        choices=ECONOMIC_LAYERS,
        default='PORT'
    )
    practice_method = models.CharField(
        _('Practice Method'),
        max_length=20,
        choices=PRACTICE_METHODS,
        default='SOLO'
    )
    average_mastery_time_days = models.IntegerField(_('Average Mastery Time (Days)'), default=30)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Art')
        verbose_name_plural = _('Arts')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_advanced(self):
        """Check if this is an advanced art (difficulty 3+)"""
        return self.difficulty_level >= 3
    
    @property
    def primary_virtue(self):
        """Return the primary virtue this art improves"""
        if not self.improved_virtues:
            return None
        return max(self.improved_virtues.items(), key=lambda x: x[1])[0]
    
    def get_prerequisites(self):
        """Return all prerequisite arts"""
        return self.parent_arts.all()


class ArtParts(models.Model):
    """
    Components or aspects of an art that must be practiced and mastered.
    """
    PRACTICE_METHODS = (
        ('THEORY', _('Theory')),
        ('PRACTICE', _('Practice')),
        ('CREATION', _('Creation')),
        ('REFLECTION', _('Reflection')),
        ('TEACHING', _('Teaching')),
    )
    
    VALIDATION_METHODS = (
        ('SELF', _('Self-Validation')),
        ('PEER', _('Peer Review')),
        ('MENTOR', _('Mentor Approval')),
        ('SYSTEM', _('System Verification')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    art = models.ForeignKey(
        Art, 
        verbose_name=_('Art'),
        on_delete=models.CASCADE, 
        related_name='parts'
    )
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    order_index = models.IntegerField(_('Order Index'), default=0)
    practice_method = models.CharField(
        _('Practice Method'),
        max_length=20,
        choices=PRACTICE_METHODS,
        default='PRACTICE'
    )
    practice_description = models.TextField(_('Practice Description'))
    validation_method = models.CharField(
        _('Validation Method'),
        max_length=20,
        choices=VALIDATION_METHODS,
        default='SELF'
    )
    estimated_hours = models.IntegerField(_('Estimated Hours'), default=1)
    resources_required = models.JSONField(_('Resources Required'), default=dict, blank=True)
    media_references = models.JSONField(_('Media References'), default=list, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Art Part')
        verbose_name_plural = _('Art Parts')
        ordering = ['art', 'order_index']
        unique_together = [['art', 'order_index']]
    
    def __str__(self):
        return f"{self.art.name} - {self.name}"
    
    @property
    def is_first_part(self):
        """Check if this is the first part of the art"""
        return self.order_index == 0
    
    @property
    def is_last_part(self):
        """Check if this is the last part of the art"""
        return self.order_index == self.art.parts.count() - 1
    
    def get_next_part(self):
        """Get the next part in sequence"""
        try:
            return self.art.parts.get(order_index=self.order_index + 1)
        except ArtParts.DoesNotExist:
            return None
    
    def get_previous_part(self):
        """Get the previous part in sequence"""
        if self.order_index == 0:
            return None
        try:
            return self.art.parts.get(order_index=self.order_index - 1)
        except ArtParts.DoesNotExist:
            return None


class ArtStage(models.Model):
    """
    Represents different learning stages for an art.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    art = models.ForeignKey(
        Art, 
        verbose_name=_('Art'),
        on_delete=models.CASCADE, 
        related_name='stages'
    )
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    order_index = models.IntegerField(_('Order Index'), default=0)
    mastery_threshold = models.IntegerField(_('Mastery Threshold'), default=20)
    stage_badge = models.CharField(_('Stage Badge Path'), max_length=255, blank=True)
    virtue_bonuses = models.JSONField(_('Virtue Bonuses'), default=dict, blank=True)
    unlock_requirements = models.JSONField(_('Unlock Requirements'), default=dict, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Art Stage')
        verbose_name_plural = _('Art Stages')
        ordering = ['art', 'order_index']
        unique_together = [['art', 'order_index']]
    
    def __str__(self):
        return f"{self.art.name} - {self.name}"
    
    @property
    def is_first_stage(self):
        """Check if this is the first stage of the art"""
        return self.order_index == 0
    
    @property
    def is_last_stage(self):
        """Check if this is the final stage of the art"""
        return self.order_index == self.art.stages.count() - 1
    
    def get_next_stage(self):
        """Get the next stage in sequence"""
        try:
            return self.art.stages.get(order_index=self.order_index + 1)
        except ArtStage.DoesNotExist:
            return None 