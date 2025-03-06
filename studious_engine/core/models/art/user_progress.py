from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

from .art import Art, ArtStage, ArtParts
from .tech_tree import TechTree

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()

class PracticeSession(models.Model):
    """
    Model to record individual practice sessions for arts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        verbose_name=_('User'),
        on_delete=models.CASCADE, 
        related_name='practice_sessions'
    )
    art = models.ForeignKey(
        Art, 
        verbose_name=_('Art'),
        on_delete=models.CASCADE, 
        related_name='practice_sessions'
    )
    part = models.ForeignKey(
        ArtParts,
        verbose_name=_('Art Part'),
        on_delete=models.CASCADE,
        related_name='practice_sessions'
    )
    started_at = models.DateTimeField(_('Started At'), default=timezone.now)
    duration_minutes = models.PositiveIntegerField(_('Duration (Minutes)'), default=0)
    notes = models.TextField(_('Notes'), blank=True)
    rating = models.PositiveSmallIntegerField(_('Rating'), null=True, blank=True, 
                                             help_text=_('User self-rating from 1-5'))
    validated = models.BooleanField(_('Validated'), default=False)
    completed = models.BooleanField(_('Completed'), default=False)
    experience_gained = models.PositiveIntegerField(_('Experience Gained'), default=0)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Practice Session')
        verbose_name_plural = _('Practice Sessions')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.art.name} - {self.part.name} ({self.duration_minutes} min)"
    
    @property
    def is_recent(self):
        """Check if practice session is from within the last week"""
        return (timezone.now() - self.started_at).days <= 7

class ArtMastery(models.Model):
    """
    Tracks a user's mastery of a specific art.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        verbose_name=_('User'),
        on_delete=models.CASCADE, 
        related_name='art_masteries'
    )
    art = models.ForeignKey(
        Art, 
        verbose_name=_('Art'),
        on_delete=models.CASCADE, 
        related_name='masteries'
    )
    discovery_date = models.DateTimeField(_('Discovery Date'), default=timezone.now)
    mastery_level = models.IntegerField(_('Mastery Level'), default=0)
    last_practiced = models.DateTimeField(_('Last Practiced'), null=True, blank=True)
    practice_streak = models.IntegerField(_('Practice Streak'), default=0)
    is_featured = models.BooleanField(_('Is Featured'), default=False)
    practice_history = models.JSONField(_('Practice History'), default=list, blank=True)
    completed_parts = models.JSONField(_('Completed Parts'), default=list, blank=True)
    current_part = models.ForeignKey(
        ArtParts,
        verbose_name=_('Current Part'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users'
    )
    public_portfolio = models.BooleanField(_('Public Portfolio'), default=False)
    mastery_achievements = models.JSONField(_('Mastery Achievements'), default=list, blank=True)
    notes = models.TextField(_('Personal Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Art Mastery')
        verbose_name_plural = _('Art Masteries')
        ordering = ['-mastery_level', 'art__name']
        unique_together = [['user', 'art']]
    
    def __str__(self):
        return f"{self.user.username} - {self.art.name} ({self.mastery_level}%)"
    
    @property
    def days_since_practiced(self):
        """Calculate days since last practice"""
        if not self.last_practiced:
            return None
        delta = timezone.now() - self.last_practiced
        return delta.days
    
    @property
    def is_stale(self):
        """Check if practice is stale (no activity for 14+ days)"""
        if not self.last_practiced:
            return True
        return self.days_since_practiced >= 14
    
    @property
    def total_practice_sessions(self):
        """Get total number of practice sessions"""
        return len(self.practice_history)
    
    def log_practice_session(self, part, duration_minutes, notes=None, validated=False):
        """
        Log a new practice session
        
        Args:
            part: The ArtPart that was practiced
            duration_minutes: Duration of practice in minutes
            notes: Optional notes about the practice
            validated: Whether the practice has been validated
        """
        session = {
            'part_id': str(part.id),
            'part_name': part.name, 
            'timestamp': timezone.now().isoformat(),
            'duration_minutes': duration_minutes,
            'notes': notes or '',
            'validated': validated
        }
        
        # Update practice history
        if self.practice_history is None:
            self.practice_history = []
        self.practice_history.append(session)
        
        # Update last practiced time
        self.last_practiced = timezone.now()
        
        # Update practice streak if practiced within last 48 hours
        if self.last_practiced and (timezone.now() - self.last_practiced).days < 2:
            self.practice_streak += 1
        else:
            self.practice_streak = 1
        
        # If validated, add to completed parts if not already there
        if validated and str(part.id) not in self.completed_parts:
            if self.completed_parts is None:
                self.completed_parts = []
            self.completed_parts.append(str(part.id))
            
            # Update current part to next part if available
            next_part = part.get_next_part()
            if next_part:
                self.current_part = next_part
        
        self.save()
        
        # Call method to recalculate mastery level
        self.recalculate_mastery_level()
        
        return session
    
    def recalculate_mastery_level(self):
        """
        Recalculate the mastery level based on completed parts
        """
        total_parts = self.art.parts.count()
        if total_parts == 0:
            return
        
        completed_count = len(self.completed_parts or [])
        self.mastery_level = min(100, int((completed_count / total_parts) * 100))
        self.save()


class UserArtStageProgress(models.Model):
    """
    Tracks a user's progress through art stages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        verbose_name=_('User'),
        on_delete=models.CASCADE, 
        related_name='art_stage_progress'
    )
    art_stage = models.ForeignKey(
        ArtStage, 
        verbose_name=_('Art Stage'),
        on_delete=models.CASCADE, 
        related_name='user_progress'
    )
    reached_date = models.DateTimeField(_('Reached Date'), default=timezone.now)
    is_current = models.BooleanField(_('Is Current'), default=True)
    completion_percentage = models.IntegerField(_('Completion Percentage'), default=0)
    notable_achievements = models.JSONField(_('Notable Achievements'), default=list, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Art Stage Progress')
        verbose_name_plural = _('User Art Stage Progress')
        ordering = ['art_stage__art', 'art_stage__order_index']
        unique_together = [['user', 'art_stage']]
    
    def __str__(self):
        return f"{self.user.username} - {self.art_stage.art.name} - {self.art_stage.name} ({self.completion_percentage}%)"
    
    def complete_stage(self):
        """Mark this stage as completed and move to the next stage"""
        self.completion_percentage = 100
        self.is_current = False
        self.save()
        
        # Get the next stage
        next_stage = self.art_stage.get_next_stage()
        if next_stage:
            # Create progress for the next stage
            UserArtStageProgress.objects.create(
                user=self.user,
                art_stage=next_stage,
                is_current=True
            )
            
        return next_stage


class UserTechTreeProgress(models.Model):
    """
    Tracks a user's progress through the tech tree.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        verbose_name=_('User'),
        on_delete=models.CASCADE, 
        related_name='tech_tree_progress'
    )
    tech_tree = models.ForeignKey(
        TechTree, 
        verbose_name=_('Tech Tree'),
        on_delete=models.CASCADE, 
        related_name='user_progress'
    )
    unlocked_date = models.DateTimeField(_('Unlocked Date'), null=True, blank=True)
    progress_percentage = models.IntegerField(_('Progress Percentage'), default=0)
    missing_requirements = models.JSONField(_('Missing Requirements'), default=dict, blank=True)
    is_unlocked = models.BooleanField(_('Is Unlocked'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Tech Tree Progress')
        verbose_name_plural = _('User Tech Tree Progress')
        ordering = ['tech_tree__level', 'tech_tree__name']
        unique_together = [['user', 'tech_tree']]
    
    def __str__(self):
        status = "Unlocked" if self.is_unlocked else f"{self.progress_percentage}% Progress"
        return f"{self.user.username} - {self.tech_tree.name} ({status})"
    
    def unlock(self):
        """Unlock this tech tree node for the user"""
        if not self.is_unlocked:
            self.is_unlocked = True
            self.unlocked_date = timezone.now()
            self.progress_percentage = 100
            self.missing_requirements = {}
            self.save()
            
            # Unlock any arts associated with this node
            from studious_engine.core.services.art_service import ArtService
            for art_id in self.tech_tree.unlocks_arts:
                try:
                    art = Art.objects.get(id=art_id)
                    ArtService.discover_art(self.user, art)
                except Art.DoesNotExist:
                    pass
    
    def check_requirements(self):
        """
        Check if all requirements are met to unlock this tech tree node
        
        Returns:
            bool: True if all requirements are met, False otherwise
        """
        from studious_engine.core.services.user_service import UserService
        from studious_engine.core.models import PlayerProfile
        
        missing = {}
        
        # Check if user profile exists
        try:
            profile = PlayerProfile.objects.get(user=self.user)
        except PlayerProfile.DoesNotExist:
            missing['profile'] = "User profile not found"
            self.missing_requirements = missing
            self.save()
            return False
        
        # Check required arts
        if self.tech_tree.required_arts:
            user_arts = set(ArtMastery.objects.filter(
                user=self.user, 
                mastery_level__gte=50  # Require at least 50% mastery
            ).values_list('art__id', flat=True))
            
            missing_arts = []
            for art_id in self.tech_tree.required_arts:
                if str(art_id) not in map(str, user_arts):
                    try:
                        art = Art.objects.get(id=art_id)
                        missing_arts.append(art.name)
                    except Art.DoesNotExist:
                        missing_arts.append(f"Unknown Art ({art_id})")
            
            if missing_arts:
                missing['arts'] = missing_arts
        
        # Check economic layer requirement
        econ_permissions = UserService.get_economic_layer_permissions(profile)
        zone_types_allowed = econ_permissions.get('permitted_zone_types', [])
        
        if self.tech_tree.zone_type_filter != 'ANY' and self.tech_tree.zone_type_filter not in zone_types_allowed:
            missing['zone_type'] = f"Requires access to {self.tech_tree.get_zone_type_filter_display()} zones"
        
        # Check rank requirement
        if profile.rank < self.tech_tree.required_zone_level:
            missing['rank'] = f"Requires rank {self.tech_tree.required_zone_level} (current: {profile.rank})"
        
        # Check required resources
        if self.tech_tree.required_resources:
            # This would require the ResourceInventory model from Phase 5
            # For now, we'll just note that we can't check this yet
            missing['resources'] = "Resource checking not implemented yet"
        
        # Save missing requirements
        self.missing_requirements = missing
        self.save()
        
        # If nothing is missing, requirements are met
        return len(missing) == 0 