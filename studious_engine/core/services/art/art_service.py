from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
from django.utils.translation import gettext_lazy as _

from core.models import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    Art, 
    ArtParts, 
    ArtTaxonomy, 
    ArtStage,
    ArtMastery, 
    UserArtStageProgress,
    PlayerProfile
)

User = get_user_model()

class ArtService:
    """
    Service for managing Art objects and related operations.
    """
    
    @staticmethod
    def create_art(name, description, taxonomy=None, **kwargs):
        """
        Creates a new Art object.
        
        Args:
            name: The name of the art
            description: A description of the art
            taxonomy: Optional ArtTaxonomy object or ID
            **kwargs: Additional fields for the Art object
            
        Returns:
            Art: The created Art object
        """
        art = Art(
            name=name,
            description=description,
            **kwargs
        )
        
        if taxonomy:
            if isinstance(taxonomy, ArtTaxonomy):
                art.taxonomy = taxonomy
            else:
                try:
                    art.taxonomy = ArtTaxonomy.objects.get(id=taxonomy)
                except ArtTaxonomy.DoesNotExist:
                    pass
        
        art.save()
        return art
    
    @staticmethod
    def add_art_part(art, name, description, practice_method, practice_description, **kwargs):
        """
        Adds a part to an existing Art.
        
        Args:
            art: The Art object or ID
            name: Name of the part
            description: Description of the part
            practice_method: Method of practice (THEORY, PRACTICE, etc.)
            practice_description: Description of how to practice
            **kwargs: Additional fields for the ArtPart object
            
        Returns:
            ArtParts: The created ArtParts object
        """
        if not isinstance(art, Art):
            try:
                art = Art.objects.get(id=art)
            except Art.DoesNotExist:
                raise ValueError(f"Art with ID {art} does not exist")
        
        # Get next order index
        order_index = ArtParts.objects.filter(art=art).count()
        
        part = ArtParts.objects.create(
            art=art,
            name=name,
            description=description,
            order_index=order_index,
            practice_method=practice_method,
            practice_description=practice_description,
            **kwargs
        )
        
        return part
    
    @staticmethod
    def add_art_stage(art, name, description, mastery_threshold, **kwargs):
        """
        Adds a learning stage to an Art.
        
        Args:
            art: The Art object or ID
            name: Name of the stage
            description: Description of the stage
            mastery_threshold: Mastery level required to reach this stage
            **kwargs: Additional fields for the ArtStage object
            
        Returns:
            ArtStage: The created ArtStage object
        """
        if not isinstance(art, Art):
            try:
                art = Art.objects.get(id=art)
            except Art.DoesNotExist:
                raise ValueError(f"Art with ID {art} does not exist")
        
        # Get next order index
        order_index = ArtStage.objects.filter(art=art).count()
        
        stage = ArtStage.objects.create(
            art=art,
            name=name,
            description=description,
            order_index=order_index,
            mastery_threshold=mastery_threshold,
            **kwargs
        )
        
        return stage
    
    @staticmethod
    def discover_art(user, art, initial_part=None):
        """
        Records a user's discovery of an art and initializes their mastery.
        
        Args:
            user: The User object or ID
            art: The Art object or ID
            initial_part: Optional specific ArtPart to start with (defaults to first part)
            
        Returns:
            ArtMastery: The created ArtMastery object
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
                
        if not isinstance(art, Art):
            try:
                art = Art.objects.get(id=art)
            except Art.DoesNotExist:
                raise ValueError(f"Art with ID {art} does not exist")
        
        # Check if user already has mastery for this art
        existing = ArtMastery.objects.filter(user=user, art=art).first()
        if existing:
            return existing
            
        with transaction.atomic():
            # Get the first part or specified part
            if initial_part:
                if not isinstance(initial_part, ArtParts):
                    try:
                        initial_part = ArtParts.objects.get(id=initial_part, art=art)
                    except ArtParts.DoesNotExist:
                        initial_part = None
            
            if not initial_part:
                initial_part = ArtParts.objects.filter(art=art).order_by('order_index').first()
            
            # Create the mastery record
            mastery = ArtMastery.objects.create(
                user=user,
                art=art,
                discovery_date=timezone.now(),
                current_part=initial_part
            )
            
            # Initialize first stage progress if stages exist
            first_stage = ArtStage.objects.filter(art=art).order_by('order_index').first()
            if first_stage:
                UserArtStageProgress.objects.create(
                    user=user,
                    art_stage=first_stage,
                    is_current=True
                )
                
            # Award discovery experience points
            try:
                profile = PlayerProfile.objects.get(user=user)
                profile.experience_points += 10  # Basic discovery XP
                profile.save()
            except PlayerProfile.DoesNotExist:
                pass
                
        return mastery
    
    @staticmethod
    def get_available_arts(user, include_unlocked=True, economic_filter=True, rank_filter=True):
        """
        Get arts available to a user based on their profile.
        
        Args:
            user: The User object or ID
            include_unlocked: Whether to include arts already unlocked by the user
            economic_filter: Whether to filter by economic layer
            rank_filter: Whether to filter by rank
            
        Returns:
            QuerySet: QuerySet of available Art objects
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        # Start with all arts or just those not already discovered
        if include_unlocked:
            available_arts = Art.objects.all()
        else:
            unlocked_ids = ArtMastery.objects.filter(user=user).values_list('art_id', flat=True)
            available_arts = Art.objects.exclude(id__in=unlocked_ids)
        
        # Apply economic layer and rank filters if requested
        if economic_filter or rank_filter:
            try:
                profile = PlayerProfile.objects.get(user=user)
                
                if economic_filter:
                    economic_layers = {
                        'port': ['PORT'],
                        'laws': ['PORT', 'LAWS'],
                        'republic': ['PORT', 'LAWS', 'REPUBLIC']
                    }
                    allowed_layers = economic_layers.get(profile.economic_layer, ['PORT'])
                    available_arts = available_arts.filter(economic_layer_required__in=allowed_layers)
                
                if rank_filter:
                    available_arts = available_arts.filter(rank_required__lte=profile.rank)
            
            except PlayerProfile.DoesNotExist:
                pass
        
        return available_arts
    
    @staticmethod
    def get_featured_arts(limit=6, difficulty_level=None, taxonomy=None):
        """
        Get a selection of featured arts, optionally filtered.
        
        Args:
            limit: Number of arts to return
            difficulty_level: Optional filter by difficulty level
            taxonomy: Optional filter by taxonomy
            
        Returns:
            QuerySet: QuerySet of Art objects
        """
        query = Art.objects.filter(is_unlocked_default=True)
        
        if difficulty_level:
            query = query.filter(difficulty_level=difficulty_level)
            
        if taxonomy:
            if isinstance(taxonomy, ArtTaxonomy):
                query = query.filter(taxonomy=taxonomy)
            else:
                try:
                    taxonomy_obj = ArtTaxonomy.objects.get(id=taxonomy)
                    query = query.filter(taxonomy=taxonomy_obj)
                except ArtTaxonomy.DoesNotExist:
                    pass
                    
        return query.order_by('?')[:limit]  # Random selection
    
    @staticmethod
    def get_arts_by_virtue(virtue_name, limit=10):
        """
        Get arts that improve a specific virtue.
        
        Args:
            virtue_name: Name of the virtue (wisdom, courage, etc.)
            limit: Maximum number of arts to return
            
        Returns:
            list: List of Art objects
        """
        # Note: This is a simplistic implementation that assumes virtues are stored
        # in a predictable format in the improved_virtues JSONField
        results = []
        
        for art in Art.objects.all():
            virtues = art.improved_virtues or {}
            if virtue_name.lower() in [k.lower() for k in virtues.keys()]:
                results.append(art)
                if len(results) >= limit:
                    break
                    
        return results
    
    @staticmethod
    def get_related_arts(art, limit=3):
        """
        Get related arts based on taxonomy and virtue improvements.
        
        Args:
            art: The Art object to find related arts for
            limit: Maximum number of arts to return
            
        Returns:
            QuerySet: QuerySet of related Art objects
        """
        # Start with arts in the same taxonomy
        related_arts = Art.objects.filter(taxonomy=art.taxonomy).exclude(id=art.id)
        
        # If we don't have enough, add arts that improve the same primary virtue
        if related_arts.count() < limit:
            primary_virtue = art.primary_virtue
            if primary_virtue:
                virtue_arts = Art.objects.filter(improved_virtues__has_key=primary_virtue)
                virtue_arts = virtue_arts.exclude(id=art.id).exclude(id__in=[a.id for a in related_arts])
                related_arts = list(related_arts) + list(virtue_arts)
        
        # If still not enough, add arts with similar difficulty level
        if len(related_arts) < limit:
            difficulty_arts = Art.objects.filter(
                difficulty_level__in=[
                    max(1, art.difficulty_level - 1),
                    art.difficulty_level,
                    min(5, art.difficulty_level + 1)
                ]
            ).exclude(id=art.id)
            difficulty_arts = difficulty_arts.exclude(id__in=[a.id for a in related_arts])
            related_arts = list(related_arts) + list(difficulty_arts)
        
        # Limit to the requested number
        return related_arts[:limit]
    
    @staticmethod
    def create_taxonomy(name, description, parent=None, level=1, **kwargs):
        """
        Create a new art taxonomy category.
        
        Args:
            name: Name of the taxonomy
            description: Description of the taxonomy
            parent: Optional parent taxonomy
            level: Taxonomy level
            **kwargs: Additional fields
            
        Returns:
            ArtTaxonomy: The created taxonomy
        """
        return ArtTaxonomy.objects.create(
            name=name,
            description=description,
            parent=parent,
            level=level,
            **kwargs
        ) 