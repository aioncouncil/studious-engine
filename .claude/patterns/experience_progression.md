# Experience Progression Patterns

## Overview

Experience Progression is a fundamental concept in Atlantis Go, representing how users grow and develop through participating in structured experiences. This pattern document explains how to implement and track experience progression, completion, and the associated rewards and growth.

## Experience Lifecycle

The lifecycle of an experience in Atlantis Go follows these general stages:

1. **Discovery**: User discovers an experience through exploration, recommendations, or the tech tree
2. **Initiation**: User begins the experience and progresses through initial steps
3. **Matrix Flow**: User advances through the four matrix quadrants (SO→BO→SI→BI)
4. **Completion**: User completes all required components and meets completion criteria
5. **Mastery**: After completion, user can continue to practice and achieve higher mastery levels

## Common Patterns

### Pattern 1: Experience Definition

**Purpose**: Define the structure and requirements of an experience.

**Implementation**:

```python
class Experience(models.Model):
    """Model for defining experiences in Atlantis Go."""
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Categorization
    category = models.CharField(
        max_length=50,
        choices=[
            ('PHYSICAL', 'Physical'),
            ('MENTAL', 'Mental'),
            ('CREATIVE', 'Creative'),
            ('SOCIAL', 'Social'),
            ('SPIRITUAL', 'Spiritual'),
        ]
    )
    tags = models.JSONField(default=list)
    
    # Requirements
    min_level = models.IntegerField(default=1)
    required_virtues = models.JSONField(
        default=dict,
        help_text="Dict of virtue requirements {'wisdom': 20, 'courage': 15}"
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='unlocks',
        blank=True
    )
    
    # Matrix flow components
    soul_out_component = models.TextField(
        help_text="The wisdom/understanding component of the experience"
    )
    body_out_component = models.TextField(
        help_text="The action/implementation component of the experience"
    )
    soul_in_component = models.TextField(
        help_text="The reflection/integration component of the experience"
    )
    body_in_component = models.TextField(
        help_text="The embodiment/nurturing component of the experience"
    )
    primary_quadrant = models.CharField(
        max_length=2,
        choices=[
            ('SO', 'Soul Out'),
            ('BO', 'Body Out'),
            ('SI', 'Soul In'),
            ('BI', 'Body In'),
        ],
        default='SO'
    )
    
    # Rewards
    virtue_impacts = models.JSONField(
        default=dict,
        help_text="Dict of virtue changes {'wisdom': 5, 'courage': 3}"
    )
    xp_reward = models.IntegerField(default=100)
    
    # Progress tracking
    estimated_duration_minutes = models.IntegerField(default=60)
    completion_criteria = models.JSONField(
        default=dict,
        help_text="Dict of criteria {'min_time_minutes': 45, 'required_outputs': ['reflection']}"
    )
    max_mastery_level = models.IntegerField(default=5)
    
    # Geocoding (optional)
    location_required = models.BooleanField(default=False)
    location_point = models.PointField(null=True, blank=True)
    location_radius_meters = models.IntegerField(default=100)
    
    # Stats and metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_experiences'
    )
    
    def __str__(self):
        return self.name
    
    def check_prerequisites(self, user):
        """Check if user meets all prerequisites for this experience."""
        # Check level requirement
        if user.level < self.min_level:
            return False
            
        # Check virtue requirements
        for virtue_name, min_value in self.required_virtues.items():
            try:
                user_value = getattr(user.virtue_metrics, virtue_name)
                if user_value < min_value:
                    return False
            except (AttributeError, KeyError):
                return False
                
        # Check prerequisite experiences
        for prereq in self.prerequisites.all():
            if not UserExperience.objects.filter(
                user=user,
                experience=prereq,
                status='COMPLETED'
            ).exists():
                return False
                
        return True
    
    def get_current_component(self, quadrant):
        """Get the content for a specific quadrant."""
        component_map = {
            'SO': self.soul_out_component,
            'BO': self.body_out_component,
            'SI': self.soul_in_component,
            'BI': self.body_in_component
        }
        return component_map.get(quadrant)
```

**Key Points**:
- Experiences define a complete structure with requirements and rewards
- Matrix flow components are defined for each quadrant
- Prerequisite system allows for experience dependency chains
- Virtue requirements and impacts define the growth path

**When to Use**:
- When defining new experience types
- For structuring learning activities
- When implementing progression systems

**When to Avoid**:
- For simple, non-educational interactions
- For system events that don't require full experience structure

### Pattern 2: User Experience Tracking

**Purpose**: Track a user's progress through experiences.

**Implementation**:

```python
class UserExperience(models.Model):
    """Model for tracking user progress through experiences."""
    
    # Relationships
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    experience = models.ForeignKey(
        'Experience',
        on_delete=models.CASCADE,
        related_name='user_experiences'
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('DISCOVERED', 'Discovered'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('MASTERED', 'Mastered'),
            ('ABANDONED', 'Abandoned')
        ],
        default='DISCOVERED'
    )
    
    # Progress tracking
    current_quadrant = models.CharField(
        max_length=2,
        choices=[
            ('SO', 'Soul Out'),
            ('BO', 'Body Out'),
            ('SI', 'Soul In'),
            ('BI', 'Body In'),
        ],
        default='SO'
    )
    quadrants_completed = models.JSONField(default=list)
    
    mastery_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # Time tracking
    discovered_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_progress = models.DateTimeField(auto_now=True)
    
    # User data and reflection
    user_notes = models.TextField(blank=True)
    reflection_text = models.TextField(blank=True)
    user_outputs = models.JSONField(default=dict)
    
    # Stats tracking
    total_time_seconds = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'experience')
        ordering = ['-last_progress']
    
    def __str__(self):
        return f"{self.user.username} - {self.experience.name} ({self.status})"
    
    def advance_quadrant(self):
        """
        Advance the user to the next quadrant in the matrix flow.
        Returns the new quadrant or None if all quadrants are completed.
        """
        # Mark current quadrant as completed
        if self.current_quadrant not in self.quadrants_completed:
            quadrants = self.quadrants_completed.copy()
            quadrants.append(self.current_quadrant)
            self.quadrants_completed = quadrants
            
        # Determine next quadrant
        flow_sequence = ['SO', 'BO', 'SI', 'BI']
        current_index = flow_sequence.index(self.current_quadrant)
        next_index = (current_index + 1) % len(flow_sequence)
        next_quadrant = flow_sequence[next_index]
        
        # Check if we've completed a full cycle
        if next_quadrant in self.quadrants_completed and len(self.quadrants_completed) >= 4:
            # All quadrants completed
            return None
            
        # Update to next quadrant
        self.current_quadrant = next_quadrant
        self.save(update_fields=['current_quadrant', 'quadrants_completed', 'last_progress'])
        
        return next_quadrant
    
    def complete_experience(self):
        """
        Mark the experience as completed and apply rewards.
        Returns dict with virtue changes and other rewards.
        """
        if self.status == 'COMPLETED' or self.status == 'MASTERED':
            return {'message': 'Experience already completed'}
            
        # Ensure we have all requirements
        if len(self.quadrants_completed) < 4:
            return {'error': 'Not all quadrants have been completed'}
            
        if not self.reflection_text:
            return {'error': 'Reflection is required to complete the experience'}
            
        # Update status
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        
        # Apply rewards
        from users.services import VirtueService
        
        rewards = {
            'xp_gained': self.experience.xp_reward,
            'virtue_changes': {}
        }
        
        # Apply XP
        self.user.add_xp(self.experience.xp_reward)
        
        # Apply virtue changes
        for virtue_name, value_change in self.experience.virtue_impacts.items():
            try:
                new_value, old_value = VirtueService.modify_virtue(
                    self.user,
                    virtue_name,
                    value_change,
                    f"Completed '{self.experience.name}' experience"
                )
                
                rewards['virtue_changes'][virtue_name] = {
                    'previous': old_value,
                    'new': new_value,
                    'change': new_value - old_value
                }
            except Exception as e:
                rewards['errors'] = rewards.get('errors', []) + [str(e)]
                
        # Set mastery level to 1 upon completion
        self.mastery_level = 1
                
        # Save the record
        self.save()
        
        return rewards
    
    def increase_mastery(self, performance_factor=1.0):
        """
        Increase mastery level based on repeated practice.
        Returns new mastery level or None if already at max.
        """
        if self.status != 'COMPLETED' and self.status != 'MASTERED':
            return {'error': 'Experience must be completed before mastery can increase'}
            
        if self.mastery_level >= self.experience.max_mastery_level:
            return {'message': 'Already at maximum mastery level'}
            
        # Increase mastery based on performance
        # Base chance of 20% per practice, modified by performance
        base_chance = 0.2
        adjusted_chance = base_chance * performance_factor
        
        # Higher levels are harder to achieve
        level_difficulty = 1 + (self.mastery_level * 0.2)  # Each level is 20% harder
        final_chance = adjusted_chance / level_difficulty
        
        # Random roll for mastery increase
        import random
        if random.random() < final_chance:
            self.mastery_level += 1
            
            # Update status if reached max mastery
            if self.mastery_level >= self.experience.max_mastery_level:
                self.status = 'MASTERED'
                
            self.save()
            
            # Apply small virtue bonuses for mastery progress
            # This creates an incentive for continued practice
            from users.services import VirtueService
            
            rewards = {
                'mastery_level': self.mastery_level,
                'virtue_changes': {}
            }
            
            # Apply small virtue boosts (25% of original values)
            for virtue_name, value_change in self.experience.virtue_impacts.items():
                mastery_bonus = value_change * 0.25
                if mastery_bonus > 0:
                    try:
                        new_value, old_value = VirtueService.modify_virtue(
                            self.user,
                            virtue_name,
                            mastery_bonus,
                            f"Increased mastery in '{self.experience.name}' to level {self.mastery_level}"
                        )
                        
                        rewards['virtue_changes'][virtue_name] = {
                            'previous': old_value,
                            'new': new_value,
                            'change': new_value - old_value
                        }
                    except Exception as e:
                        rewards['errors'] = rewards.get('errors', []) + [str(e)]
                        
            return rewards
        else:
            return {
                'message': 'Practice recorded but mastery level unchanged',
                'mastery_level': self.mastery_level
            }
    
    def record_session(self, duration_seconds, outputs=None):
        """
        Record a session of practice for this experience.
        Updates total time and session count, stores outputs.
        """
        if self.status == 'DISCOVERED':
            self.status = 'IN_PROGRESS'
            self.started_at = timezone.now()
            
        # Update time tracking
        self.total_time_seconds += duration_seconds
        self.total_sessions += 1
        
        # Store outputs if provided
        if outputs:
            new_outputs = self.user_outputs.copy()
            timestamp = timezone.now().isoformat()
            
            # Store as a timestamped entry
            new_outputs[timestamp] = outputs
            self.user_outputs = new_outputs
            
        self.save()
        
        return {
            'total_sessions': self.total_sessions,
            'total_time_seconds': self.total_time_seconds,
            'total_time_formatted': format_time_duration(self.total_time_seconds)
        }
        
def format_time_duration(seconds):
    """Helper to format seconds into a readable duration."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {remaining_seconds}s"
    elif minutes > 0:
        return f"{minutes}m {remaining_seconds}s"
    else:
        return f"{remaining_seconds}s"
```

**Key Points**:
- Tracks user progress through matrix flow quadrants
- Records detailed metrics about time spent and sessions
- Implements mastery progression with diminishing returns
- Stores user outputs and reflections

**When to Use**:
- For tracking user engagement with experiences
- When implementing completion and mastery systems
- For progress visualization components

**When to Avoid**:
- For system events that don't require user engagement
- For ephemeral activities with no lasting impact

### Pattern 3: Experience Recommendation

**Purpose**: Recommend relevant experiences based on user profile and progress.

**Implementation**:

```python
class ExperienceRecommendationService:
    """Service for recommending experiences to users."""
    
    def get_recommendations(self, user, limit=10):
        """
        Get personalized experience recommendations for a user.
        Uses multiple recommendation strategies.
        
        Returns:
            dict: Categorized recommendations with explanations
        """
        recommendations = {
            'matrix_quadrant': self._get_quadrant_recommendations(user, limit=3),
            'virtue_growth': self._get_virtue_recommendations(user, limit=3),
            'next_steps': self._get_progression_recommendations(user, limit=3),
            'nearby': self._get_location_recommendations(user, limit=3),
            'popular': self._get_popular_recommendations(user, limit=3),
        }
        
        # Collect all recommendation IDs for deduplication
        all_ids = []
        for category in recommendations.values():
            if category.get('items'):
                all_ids.extend([item['id'] for item in category['items']])
        
        # Ensure we have enough unique recommendations
        if len(set(all_ids)) < limit and len(set(all_ids)) < 10:
            # Add random recommendations to fill out the list
            random_items = self._get_random_recommendations(
                user, 
                limit=limit,
                exclude_ids=all_ids
            )
            recommendations['discover'] = {
                'title': 'Discover Something New',
                'explanation': 'Expand your horizons with these experiences',
                'items': random_items
            }
            
        return recommendations
    
    def _get_quadrant_recommendations(self, user, limit=3):
        """Get recommendations based on matrix quadrant."""
        try:
            dominant_quadrant = user.virtue_metrics.matrix_quadrant
        except AttributeError:
            return {'title': 'Matrix Balance', 'explanation': 'Error calculating quadrant', 'items': []}
            
        from experience.models import Experience
        from django.db.models import Q
        
        # Get user's previously completed experiences
        completed_ids = user.experiences.filter(
            status__in=['COMPLETED', 'MASTERED']
        ).values_list('experience_id', flat=True)
        
        # Find experiences that match the dominant quadrant
        experiences = Experience.objects.filter(
            primary_quadrant=dominant_quadrant
        ).exclude(
            id__in=completed_ids
        ).order_by('?')[:limit]
        
        items = [
            {
                'id': str(exp.id),
                'name': exp.name,
                'description': exp.description,
                'category': exp.category,
                'primary_quadrant': exp.primary_quadrant,
                'estimated_duration_minutes': exp.estimated_duration_minutes,
                'virtue_impacts': exp.virtue_impacts,
            }
            for exp in experiences
        ]
        
        # Return with explanation
        quadrant_names = {
            'SO': 'Soul Out (wisdom, courage)',
            'BO': 'Body Out (strength, endurance)',
            'SI': 'Soul In (temperance, justice)',
            'BI': 'Body In (health, beauty)'
        }
        
        return {
            'title': f'For Your {quadrant_names.get(dominant_quadrant, "Balance")}',
            'explanation': f'Experiences that align with your dominant {quadrant_names.get(dominant_quadrant, "qualities")}',
            'items': items
        }
        
    def _get_virtue_recommendations(self, user, limit=3):
        """Get recommendations based on virtue needs."""
        try:
            metrics = user.virtue_metrics
            
            # Find lowest virtue
            virtues = {
                'wisdom': metrics.wisdom,
                'courage': metrics.courage,
                'temperance': metrics.temperance,
                'justice': metrics.justice,
                'strength': metrics.strength,
                'health': metrics.health,
                'beauty': metrics.beauty,
                'endurance': metrics.endurance
            }
            
            lowest_virtue = min(virtues.items(), key=lambda x: x[1])
            lowest_name, lowest_value = lowest_virtue
            
        except AttributeError:
            return {'title': 'Virtue Growth', 'explanation': 'Error accessing virtues', 'items': []}
            
        from experience.models import Experience
        from django.db.models import Q
        import json
        
        # Get user's previously completed experiences
        completed_ids = user.experiences.filter(
            status__in=['COMPLETED', 'MASTERED']
        ).values_list('experience_id', flat=True)
        
        # Find experiences that improve the lowest virtue
        # We need to filter where the JSON field virtue_impacts contains our virtue
        experiences = Experience.objects.filter(
            virtue_impacts__contains=lowest_name
        ).exclude(
            id__in=completed_ids
        ).order_by('?')[:limit]
        
        # Further filter to ensure the value is positive
        filtered_items = []
        for exp in experiences:
            if exp.virtue_impacts.get(lowest_name, 0) > 0:
                filtered_items.append({
                    'id': str(exp.id),
                    'name': exp.name,
                    'description': exp.description,
                    'category': exp.category,
                    'primary_quadrant': exp.primary_quadrant,
                    'estimated_duration_minutes': exp.estimated_duration_minutes,
                    'virtue_impacts': exp.virtue_impacts,
                })
                
        return {
            'title': f'Improve Your {lowest_name.title()}',
            'explanation': f'Experiences to help develop your {lowest_name}, currently at {lowest_value}/100',
            'items': filtered_items
        }
    
    def _get_progression_recommendations(self, user, limit=3):
        """Get recommendations based on natural progression path."""
        # Get experiences user has already completed
        from experience.models import Experience, UserExperience
        
        completed_experiences = UserExperience.objects.filter(
            user=user,
            status__in=['COMPLETED', 'MASTERED']
        ).values_list('experience_id', flat=True)
        
        if not completed_experiences:
            # User hasn't completed anything yet, suggest starter experiences
            experiences = Experience.objects.filter(
                min_level=1,
                prerequisites=None
            ).order_by('?')[:limit]
        else:
            # Find experiences that are unlocked by what the user has completed
            unlocked = Experience.objects.filter(
                prerequisites__in=completed_experiences
            ).exclude(
                id__in=completed_experiences
            ).order_by('?')[:limit]
            
            experiences = unlocked
            
        items = [
            {
                'id': str(exp.id),
                'name': exp.name,
                'description': exp.description,
                'category': exp.category,
                'primary_quadrant': exp.primary_quadrant,
                'estimated_duration_minutes': exp.estimated_duration_minutes,
                'virtue_impacts': exp.virtue_impacts,
            }
            for exp in experiences
        ]
        
        title = "Your Next Steps" if completed_experiences else "Getting Started"
        explanation = (
            "Experiences that build on what you've already completed" 
            if completed_experiences else 
            "Great first experiences to begin your journey"
        )
        
        return {
            'title': title,
            'explanation': explanation,
            'items': items
        }
    
    def _get_location_recommendations(self, user, limit=3):
        """Get recommendations based on user location."""
        # Get user's current location
        try:
            location = user.current_location.point
        except AttributeError:
            return {'title': 'Nearby', 'explanation': 'Location not available', 'items': []}
            
        from experience.models import Experience
        from django.contrib.gis.db.models.functions import Distance
        from django.contrib.gis.measure import D
        
        # Find experiences near the user's location
        # Get user's previously completed experiences
        completed_ids = user.experiences.filter(
            status__in=['COMPLETED', 'MASTERED']
        ).values_list('experience_id', flat=True)
        
        experiences = Experience.objects.filter(
            location_required=True
        ).exclude(
            id__in=completed_ids
        ).annotate(
            distance=Distance('location_point', location)
        ).filter(
            location_point__distance_lte=(location, D(km=5))  # Within 5 km
        ).order_by('distance')[:limit]
        
        items = [
            {
                'id': str(exp.id),
                'name': exp.name,
                'description': exp.description,
                'category': exp.category,
                'primary_quadrant': exp.primary_quadrant,
                'estimated_duration_minutes': exp.estimated_duration_minutes,
                'virtue_impacts': exp.virtue_impacts,
                'distance_km': round(exp.distance.km, 1)
            }
            for exp in experiences
        ]
        
        return {
            'title': 'Nearby Experiences',
            'explanation': 'Experiences available near your current location',
            'items': items
        }
    
    def _get_popular_recommendations(self, user, limit=3):
        """Get recommendations based on popularity."""
        from experience.models import Experience, UserExperience
        from django.db.models import Count
        
        # Get user's previously completed experiences
        completed_ids = user.experiences.filter(
            status__in=['COMPLETED', 'MASTERED']
        ).values_list('experience_id', flat=True)
        
        # Find popular experiences based on completion count
        popular_ids = UserExperience.objects.filter(
            status__in=['COMPLETED', 'MASTERED']
        ).values('experience_id').annotate(
            count=Count('experience_id')
        ).order_by('-count').values_list('experience_id', flat=True)[:20]
        
        # Get the actual experience objects, excluding completed ones
        experiences = Experience.objects.filter(
            id__in=popular_ids
        ).exclude(
            id__in=completed_ids
        ).order_by('?')[:limit]
        
        items = [
            {
                'id': str(exp.id),
                'name': exp.name,
                'description': exp.description,
                'category': exp.category,
                'primary_quadrant': exp.primary_quadrant,
                'estimated_duration_minutes': exp.estimated_duration_minutes,
                'virtue_impacts': exp.virtue_impacts,
            }
            for exp in experiences
        ]
        
        return {
            'title': 'Popular Experiences',
            'explanation': 'Experiences other users are enjoying',
            'items': items
        }
    
    def _get_random_recommendations(self, user, limit=3, exclude_ids=None):
        """Get random recommendations, optionally excluding certain IDs."""
        from experience.models import Experience
        
        # Get user's previously completed experiences
        completed_ids = list(user.experiences.filter(
            status__in=['COMPLETED', 'MASTERED']
        ).values_list('experience_id', flat=True))
        
        # Combine with any explicitly excluded IDs
        if exclude_ids:
            exclude_ids = list(set(list(exclude_ids) + completed_ids))
        else:
            exclude_ids = completed_ids
            
        # Get random experiences
        experiences = Experience.objects.exclude(
            id__in=exclude_ids
        ).order_by('?')[:limit]
        
        items = [
            {
                'id': str(exp.id),
                'name': exp.name,
                'description': exp.description,
                'category': exp.category,
                'primary_quadrant': exp.primary_quadrant,
                'estimated_duration_minutes': exp.estimated_duration_minutes,
                'virtue_impacts': exp.virtue_impacts,
            }
            for exp in experiences
        ]
        
        return items
```

**Key Points**:
- Uses multiple recommendation strategies for diverse suggestions
- Considers user's dominant matrix quadrant
- Accounts for virtue development needs
- Includes location-based and popularity-based recommendations
- Provides natural progression paths based on prerequisites

**When to Use**:
- For homepage and dashboard recommendations
- When users complete experiences and need next steps
- For location-based discovery features

**When to Avoid**:
- When the user has explicitly searched for something specific
- For system-mandated experiences with no choice component

## Uncertainty Handling

When implementing Experience Progression patterns, several forms of uncertainty may arise:

1. **Interrupted Experiences**:
   - When users start an experience but don't complete it in one session
   - Solution: Persist progress state and allow resumption

2. **Uncertain Completion Criteria**:
   - When it's unclear if an experience has been properly completed
   - Solution: Combine objective metrics with user self-reporting

3. **Mastery Progression Uncertainty**:
   - Difficulty in measuring true mastery vs. simple repetition
   - Solution: Probabilistic progression with performance factors

Example handling code:

```python
def handle_interrupted_experience(user_experience):
    """
    Handle cases where an experience was interrupted.
    Determines if progress can be recovered or needs reset.
    """
    from django.utils import timezone
    
    # Check how long ago the last progress was
    time_since_last = timezone.now() - user_experience.last_progress
    days_since_last = time_since_last.days
    
    if days_since_last > 30:
        # It's been too long, reset progress but keep discovery
        if user_experience.status != 'COMPLETED' and user_experience.status != 'MASTERED':
            user_experience.status = 'DISCOVERED'
            user_experience.current_quadrant = 'SO'
            user_experience.quadrants_completed = []
            user_experience.save()
            
            return {
                'status': 'reset',
                'message': 'Progress was reset due to inactivity'
            }
    
    # For shorter interruptions, maintain progress but add a note
    return {
        'status': 'maintained',
        'message': f'Continuing from where you left off {days_since_last} days ago'
    }
```

## Error Recovery

Common errors in Experience Progression implementation include:

1. **Progress State Inconsistency**:
   - Problem: Contradictory progress tracking data
   - Resolution: Validate and repair progress state

2. **Reward Application Failures**:
   - Problem: Virtue updates or XP application fails
   - Resolution: Transaction management and retry mechanisms

3. **Orphaned User Experiences**:
   - Problem: User experiences without valid user or experience references
   - Resolution: Cleanup routines and integrity checks

Example error recovery code:

```python
def repair_progress_inconsistencies(user_experience):
    """Repair common inconsistencies in experience progress tracking."""
    # Check for inconsistent status
    if user_experience.status == 'COMPLETED' and not user_experience.completed_at:
        user_experience.completed_at = user_experience.last_progress
        
    if user_experience.status == 'IN_PROGRESS' and not user_experience.started_at:
        user_experience.started_at = user_experience.last_progress
        
    # Check for quadrant inconsistencies
    if user_experience.status == 'COMPLETED' and len(user_experience.quadrants_completed) < 4:
        # Fill in missing quadrants for completed experiences
        user_experience.quadrants_completed = ['SO', 'BO', 'SI', 'BI']
        
    # Check if mastery level is appropriate
    if user_experience.status == 'MASTERED' and user_experience.mastery_level < user_experience.experience.max_mastery_level:
        user_experience.mastery_level = user_experience.experience.max_mastery_level
        
    # Check timing inconsistencies
    if user_experience.completed_at and user_experience.started_at and user_experience.completed_at < user_experience.started_at:
        # Swap them if completion is before start (impossible)
        user_experience.started_at, user_experience.completed_at = user_experience.completed_at, user_experience.started_at
        
    # Save repairs
    user_experience.save()
    
    return user_experience
```

## Performance Considerations

Experience Progression implementations should consider:

1. **Recommendation Caching**:
   - Cache recommendations and invalidate on relevant changes
   - Generate suggestions during quiet periods, not on-demand

2. **Denormalized Progress Data**:
   - Store aggregated progress metrics for quick dashboard rendering
   - Update denormalized data on checkpoints, not every interaction

3. **Batch Processing for Rewards**:
   - Process virtue and XP updates in batches where possible
   - Use database transactions to ensure atomicity

Example performance optimization:

```python
class ExperienceCache:
    """Cache for expensive experience operations."""
    
    @staticmethod
    def get_user_recommendations(user_id):
        """Get cached recommendations or generate and cache."""
        cache_key = f"experience_recommendations:{user_id}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        # Generate if not in cache
        from users.models import User
        from experience.services import ExperienceRecommendationService
        
        user = User.objects.get(id=user_id)
        service = ExperienceRecommendationService()
        recommendations = service.get_recommendations(user)
        
        # Cache for 6 hours
        cache.set(cache_key, recommendations, 60*60*6)
        
        return recommendations
    
    @staticmethod
    def invalidate_user_recommendations(user_id):
        """Invalidate cache when user completes experiences."""
        cache_key = f"experience_recommendations:{user_id}"
        cache.delete(cache_key)
```

## Related Patterns

- [Matrix Flow](matrix_flow.md)
- [Virtue Metrics Calculation](virtue_metrics_calculation.md)
- [User Progress Tracking](user_progress_tracking.md) 