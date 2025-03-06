# Virtue Metrics Calculation Patterns

## Overview

Virtue Metrics are central to the Atlantis Go philosophy and mechanics, representing the core values and traits users develop during their journey. This pattern document explains how to implement and utilize Virtue Metrics calculations across the system.

## Core Virtues

Atlantis Go defines eight core virtues, organized into two categories:

1. **Cardinal Virtues** (Soul-based):
   - **Wisdom**: Knowledge, understanding, discernment
   - **Courage**: Bravery, fortitude, initiative 
   - **Temperance**: Moderation, self-control, patience
   - **Justice**: Fairness, honor, integrity

2. **Physical Virtues** (Body-based):
   - **Strength**: Physical power, resilience
   - **Health**: Wellness, vitality, fitness
   - **Beauty**: Aesthetic development, harmony, skill
   - **Endurance**: Stamina, perseverance, consistency

## Common Patterns

### Pattern 1: Core Virtue Metrics Storage

**Purpose**: Store and retrieve a user's virtue metrics.

**Implementation**:

```python
class VirtueMetrics(models.Model):
    """Model for storing user virtue metrics."""
    
    # Foreign key to the user
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='virtue_metrics'
    )
    
    # Cardinal virtues (soul-based)
    wisdom = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Knowledge, understanding, discernment"
    )
    courage = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Bravery, fortitude, initiative"
    )
    temperance = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Moderation, self-control, patience"
    )
    justice = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Fairness, honor, integrity"
    )
    
    # Physical virtues (body-based)
    strength = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Physical power, resilience"
    )
    health = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Wellness, vitality, fitness"
    )
    beauty = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Aesthetic development, harmony, skill"
    )
    endurance = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Stamina, perseverance, consistency"
    )
    
    # Historical data for tracking progress
    virtue_history = models.JSONField(
        default=dict,
        help_text="Historical record of virtue changes"
    )
    
    # Derived metrics
    happiness_score = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ],
        help_text="Calculated happiness based on virtue balance"
    )
    
    # Tracking fields
    last_calculated = models.DateTimeField(
        auto_now=True,
        help_text="Last time virtue metrics were calculated"
    )
    
    # Matrix quadrant (derived from virtue patterns)
    matrix_quadrant = models.CharField(
        max_length=2,
        choices=[
            ('SO', 'Soul Out'),
            ('BO', 'Body Out'),
            ('SI', 'Soul In'),
            ('BI', 'Body In'),
        ],
        default='SO',
        help_text="User's dominant matrix quadrant"
    )
    
    def __str__(self):
        return f"Virtue Metrics for {self.user.username}"
    
    class Meta:
        verbose_name = "Virtue Metrics"
        verbose_name_plural = "Virtue Metrics"
        ordering = ['-last_calculated']
```

**Key Points**:
- Each user has exactly one VirtueMetrics record
- All virtues use a consistent scale (0-100)
- Default values provide a starting point for new users
- JSON field stores historical data for tracking progress

**When to Use**:
- When creating new user accounts
- For storing base virtue values
- When implementing virtue-based features

**When to Avoid**:
- For transient or calculated virtue metrics (use methods instead)
- When only temporary virtue effects are needed

### Pattern 2: Virtue Modification

**Purpose**: Update virtue values based on user activities while maintaining history.

**Implementation**:

```python
class VirtueService:
    """Service for handling virtue modifications."""
    
    @staticmethod
    def modify_virtue(user, virtue_name, value_change, reason=None):
        """
        Modify a user's virtue and record the change in history.
        
        Args:
            user: User model instance
            virtue_name: String name of virtue (lowercase)
            value_change: Integer amount to change (positive or negative)
            reason: Optional string explaining the reason for change
            
        Returns:
            tuple: (new_value, previous_value)
        """
        try:
            metrics = user.virtue_metrics
        except AttributeError:
            raise ValueError("User does not have virtue metrics")
            
        if virtue_name not in [
            'wisdom', 'courage', 'temperance', 'justice',
            'strength', 'health', 'beauty', 'endurance'
        ]:
            raise ValueError(f"Invalid virtue name: {virtue_name}")
            
        # Get current value
        current_value = getattr(metrics, virtue_name)
        
        # Calculate new value (constrained to 0-100)
        new_value = max(0, min(100, current_value + value_change))
        
        # Update virtue history
        timestamp = timezone.now().isoformat()
        
        if not metrics.virtue_history:
            metrics.virtue_history = {}
            
        if virtue_name not in metrics.virtue_history:
            metrics.virtue_history[virtue_name] = []
            
        metrics.virtue_history[virtue_name].append({
            'timestamp': timestamp,
            'previous': current_value,
            'new': new_value,
            'change': value_change,
            'reason': reason or 'Unspecified'
        })
        
        # Set the new value
        setattr(metrics, virtue_name, new_value)
        
        # Recalculate derived metrics
        VirtueService.recalculate_derived_metrics(metrics)
        
        # Save changes
        metrics.save()
        
        return (new_value, current_value)
    
    @staticmethod
    def recalculate_derived_metrics(metrics):
        """
        Recalculate derived metrics based on current virtue values.
        
        Args:
            metrics: VirtueMetrics instance
        """
        # Recalculate happiness (example formula)
        metrics.happiness_score = VirtueService.calculate_happiness(metrics)
        
        # Determine matrix quadrant
        metrics.matrix_quadrant = VirtueService.calculate_matrix_quadrant(metrics)
        
    @staticmethod
    def calculate_happiness(metrics):
        """
        Calculate happiness score based on virtue balance.
        
        Returns a value from 0-100.
        """
        # Get all virtue values
        virtues = [
            metrics.wisdom, metrics.courage, 
            metrics.temperance, metrics.justice,
            metrics.strength, metrics.health, 
            metrics.beauty, metrics.endurance
        ]
        
        # Base score is the average of all virtues
        base_score = sum(virtues) / len(virtues)
        
        # Calculate standard deviation (lower is better)
        mean = sum(virtues) / len(virtues)
        variance = sum((v - mean) ** 2 for v in virtues) / len(virtues)
        std_dev = math.sqrt(variance)
        
        # Balance modifier: higher if virtues are balanced
        # Max reasonable std_dev would be around 35 (if some virtues at 100, others at 0)
        balance_factor = 1 - (std_dev / 35)
        
        # Final score combines base level and balance
        # 70% from average level, 30% from balance
        happiness = (base_score * 0.7) + (base_score * balance_factor * 0.3)
        
        return round(happiness, 1)
    
    @staticmethod
    def calculate_matrix_quadrant(metrics):
        """
        Calculate the dominant matrix quadrant based on virtue patterns.
        Returns one of: 'SO', 'BO', 'SI', 'BI'
        """
        # Calculate score for each quadrant
        quadrant_scores = {
            'SO': (metrics.wisdom + metrics.courage) / 2,
            'BO': (metrics.strength + metrics.endurance) / 2,
            'SI': (metrics.temperance + metrics.justice) / 2,
            'BI': (metrics.health + metrics.beauty) / 2
        }
        
        # Find dominant quadrant (highest score)
        dominant_quadrant = max(quadrant_scores.items(), key=lambda x: x[1])[0]
        
        return dominant_quadrant
```

**Key Points**:
- Changes to virtues are always tracked in history
- Values are constrained to a valid range (0-100)
- Derived metrics are recalculated automatically
- All modifications go through a central service for consistency

**When to Use**:
- When users complete experiences
- After completing challenges
- For regular virtue updates from activities
- When applying virtue bonuses or penalties

**When to Avoid**:
- For temporary or visual-only changes
- When simulating "what-if" scenarios

### Pattern 3: Virtue History Analysis

**Purpose**: Analyze historical virtue data to provide insights into user growth.

**Implementation**:

```python
class VirtueAnalyticsService:
    """Service for analyzing virtue history and trends."""
    
    @staticmethod
    def get_virtue_progression(user, virtue_name, period_days=30):
        """
        Get progression data for a specific virtue over time.
        
        Args:
            user: User model instance
            virtue_name: String name of virtue
            period_days: Number of days to look back
            
        Returns:
            list: List of data points with timestamp and value
        """
        try:
            metrics = user.virtue_metrics
        except AttributeError:
            raise ValueError("User does not have virtue metrics")
            
        if not metrics.virtue_history or virtue_name not in metrics.virtue_history:
            return []
            
        # Get raw history data
        history = metrics.virtue_history[virtue_name]
        
        # Calculate cutoff date
        cutoff = timezone.now() - timezone.timedelta(days=period_days)
        cutoff_str = cutoff.isoformat()
        
        # Filter to relevant period
        filtered_history = [
            entry for entry in history 
            if entry['timestamp'] >= cutoff_str
        ]
        
        # Prepare data points for chart
        data_points = [
            {
                'timestamp': entry['timestamp'],
                'value': entry['new'],
                'change': entry['change'],
                'reason': entry['reason']
            } 
            for entry in filtered_history
        ]
        
        return data_points
    
    @staticmethod
    def get_growth_summary(user, period_days=30):
        """
        Get a summary of all virtue growth in the specified period.
        
        Returns:
            dict: Growth summary with fastest growing, most improved, etc.
        """
        try:
            metrics = user.virtue_metrics
        except AttributeError:
            raise ValueError("User does not have virtue metrics")
            
        if not metrics.virtue_history:
            return {
                'fastest_growing': None,
                'most_improved': None,
                'needs_attention': None,
                'total_growth': 0
            }
            
        # Calculate cutoff date
        cutoff = timezone.now() - timezone.timedelta(days=period_days)
        cutoff_str = cutoff.isoformat()
        
        # Track growth for each virtue
        growth_data = {}
        
        for virtue in [
            'wisdom', 'courage', 'temperance', 'justice',
            'strength', 'health', 'beauty', 'endurance'
        ]:
            if virtue not in metrics.virtue_history:
                growth_data[virtue] = {
                    'net_change': 0,
                    'change_count': 0,
                    'start_value': getattr(metrics, virtue),
                    'current_value': getattr(metrics, virtue)
                }
                continue
                
            # Filter to relevant period
            history = metrics.virtue_history[virtue]
            filtered_history = [
                entry for entry in history 
                if entry['timestamp'] >= cutoff_str
            ]
            
            if not filtered_history:
                growth_data[virtue] = {
                    'net_change': 0,
                    'change_count': 0,
                    'start_value': getattr(metrics, virtue),
                    'current_value': getattr(metrics, virtue)
                }
                continue
                
            # Calculate metrics
            start_value = filtered_history[0]['previous']
            current_value = getattr(metrics, virtue)
            net_change = current_value - start_value
            change_count = len(filtered_history)
            
            growth_data[virtue] = {
                'net_change': net_change,
                'change_count': change_count,
                'start_value': start_value,
                'current_value': current_value
            }
            
        # Determine insights
        fastest_growing = max(
            growth_data.items(), 
            key=lambda x: x[1]['change_count'] if x[1]['net_change'] > 0 else 0
        )[0] if any(v['net_change'] > 0 for v in growth_data.values()) else None
        
        most_improved = max(
            growth_data.items(), 
            key=lambda x: x[1]['net_change']
        )[0] if any(v['net_change'] > 0 for v in growth_data.values()) else None
        
        # Find virtue with lowest value that hasn't grown
        needs_attention = min(
            [(virtue, data) for virtue, data in growth_data.items() 
             if data['net_change'] <= 0],
            key=lambda x: x[1]['current_value'],
            default=(None, None)
        )[0]
        
        # Calculate total growth across all virtues
        total_growth = sum(data['net_change'] for data in growth_data.values())
        
        return {
            'fastest_growing': fastest_growing,
            'most_improved': most_improved,
            'needs_attention': needs_attention,
            'total_growth': total_growth,
            'virtue_data': growth_data
        }
```

**Key Points**:
- Analysis focuses on trends and patterns over time
- Provides insights that can be used to guide user recommendations
- Can identify areas that need attention
- Flexible time period for different analysis contexts

**When to Use**:
- For user progress reports
- When generating personalized recommendations
- For weekly/monthly summary features
- In data visualization components

**When to Avoid**:
- For real-time decision making (too computationally intensive)
- When historical data is not relevant

### Pattern 4: Multi-Virtue Updates from Experiences

**Purpose**: Update multiple virtues simultaneously from complex activities.

**Implementation**:

```python
class ExperienceVirtueService:
    """Service for handling virtue updates from experiences."""
    
    @staticmethod
    def apply_experience_virtues(user, experience, performance_factor=1.0):
        """
        Apply virtue changes from an experience with performance scaling.
        
        Args:
            user: User model instance
            experience: Experience model instance
            performance_factor: Scale factor for virtue gains (0.5-1.5)
                               1.0 is standard, higher for better performance
                               
        Returns:
            dict: Summary of virtue changes
        """
        try:
            metrics = user.virtue_metrics
        except AttributeError:
            raise ValueError("User does not have virtue metrics")
            
        # Get virtue impacts from experience
        virtue_impacts = experience.virtue_impacts
        
        if not virtue_impacts:
            return {'message': 'No virtue impacts for this experience'}
            
        # Track changes for reporting
        changes = {}
        
        # Apply each virtue change
        for virtue_name, base_value in virtue_impacts.items():
            # Skip invalid virtues
            if virtue_name not in [
                'wisdom', 'courage', 'temperance', 'justice',
                'strength', 'health', 'beauty', 'endurance'
            ]:
                continue
                
            # Calculate actual change with performance factor
            actual_change = base_value * performance_factor
            
            # Apply the change
            reason = f"Completed '{experience.name}' experience"
            new_value, old_value = VirtueService.modify_virtue(
                user, 
                virtue_name, 
                actual_change, 
                reason
            )
            
            changes[virtue_name] = {
                'previous': old_value,
                'new': new_value,
                'change': new_value - old_value
            }
            
        return {
            'experience_name': experience.name,
            'performance_factor': performance_factor,
            'virtue_changes': changes
        }
    
    @staticmethod
    def calculate_performance_factor(user, experience, metrics_data):
        """
        Calculate a performance factor based on user performance metrics.
        
        Args:
            user: User model instance
            experience: Experience model instance
            metrics_data: Dict with performance metrics like:
                         {'completion_time': 1200, 'accuracy': 0.85, ...}
                         
        Returns:
            float: Performance factor from 0.5 to 1.5
        """
        # Define weights for different metrics
        metric_weights = {
            'completion_time': 0.3,
            'accuracy': 0.4,
            'consistency': 0.3
        }
        
        # Calculate score components (normalized to 0-1 range)
        scores = {}
        
        # Completion time - faster is better, relative to target time
        if 'completion_time' in metrics_data and experience.target_time:
            # Target time is the expected time to complete
            # Normalize so 2x target time = 0, 0.5x target time = 1
            time_ratio = metrics_data['completion_time'] / experience.target_time
            time_score = max(0, min(1, 2 - time_ratio))
            scores['completion_time'] = time_score
        else:
            # Default to neutral if missing data
            scores['completion_time'] = 0.5
            
        # Accuracy - higher is better
        if 'accuracy' in metrics_data:
            # Direct mapping - accuracy should be 0-1 already
            scores['accuracy'] = metrics_data['accuracy']
        else:
            scores['accuracy'] = 0.5
            
        # Consistency - higher is better
        if 'consistency' in metrics_data:
            scores['consistency'] = metrics_data['consistency']
        else:
            scores['consistency'] = 0.5
            
        # Calculate weighted average
        weighted_sum = sum(
            scores.get(metric, 0.5) * weight 
            for metric, weight in metric_weights.items()
        )
        
        # Convert to 0.5-1.5 range
        performance_factor = 0.5 + weighted_sum
        
        return performance_factor
```

**Key Points**:
- Updates multiple virtues in a single transaction
- Performance factor scales virtue gains based on user performance
- All changes recorded with consistent reason tracking
- Maintains full history for each virtue

**When to Use**:
- When users complete experiences
- For milestone achievements
- When calculating virtue updates from tracked activities

**When to Avoid**:
- For simple one-virtue updates (use VirtueService.modify_virtue instead)
- When precise control over individual virtues is needed

## Uncertainty Handling

When implementing Virtue Metrics patterns, several forms of uncertainty may arise:

1. **Missing Historical Data**:
   - When virtue history is incomplete or corrupted
   - Solution: Use current values as baseline and rebuild history going forward

2. **Performance Measurement Uncertainty**:
   - When performance metrics are subjective or incomplete
   - Solution: Use reasonable defaults and weight certain metrics higher

3. **Virtue Categorization Ambiguity**:
   - When an activity affects virtues in complex ways
   - Solution: Distribute smaller impacts across multiple virtues

Example handling code:

```python
def handle_missing_virtue_history(metrics, virtue_name):
    """Handle cases where virtue history is missing."""
    current_value = getattr(metrics, virtue_name, 10)
    
    # Initialize empty history
    if not metrics.virtue_history:
        metrics.virtue_history = {}
        
    # Initialize virtue history
    if virtue_name not in metrics.virtue_history:
        metrics.virtue_history[virtue_name] = [{
            'timestamp': timezone.now().isoformat(),
            'previous': current_value,
            'new': current_value,
            'change': 0,
            'reason': 'Initialized history'
        }]
        metrics.save()
        
    return metrics.virtue_history[virtue_name]
```

## Error Recovery

Common errors in Virtue Metrics implementation include:

1. **Out-of-Range Values**:
   - Problem: Virtue values outside the valid 0-100 range
   - Resolution: Implement value clamping in all update methods

2. **Incorrect History Records**:
   - Problem: Inconsistencies in historical data
   - Resolution: Validate and repair history sequences

3. **Orphaned Virtue Records**:
   - Problem: VirtueMetrics without associated user
   - Resolution: Implement cleanup routines

Example error recovery code:

```python
def repair_virtue_metrics(user):
    """Repair common issues with a user's virtue metrics."""
    try:
        metrics = user.virtue_metrics
    except (AttributeError, VirtueMetrics.DoesNotExist):
        # Create if missing
        metrics = VirtueMetrics.objects.create(user=user)
        
    # Ensure all virtues are in valid range
    for virtue in [
        'wisdom', 'courage', 'temperance', 'justice',
        'strength', 'health', 'beauty', 'endurance'
    ]:
        current_value = getattr(metrics, virtue)
        if current_value < 0 or current_value > 100:
            # Fix out-of-range value
            corrected_value = max(0, min(100, current_value))
            setattr(metrics, virtue, corrected_value)
            
    # Ensure history exists
    if not hasattr(metrics, 'virtue_history') or metrics.virtue_history is None:
        metrics.virtue_history = {}
        
    # Validate history consistency
    for virtue in metrics.virtue_history.keys():
        history = metrics.virtue_history[virtue]
        
        # Sort by timestamp if needed
        if len(history) > 1:
            history.sort(key=lambda x: x['timestamp'])
            
        # Check for and fix inconsistencies
        for i in range(1, len(history)):
            if history[i]['previous'] != history[i-1]['new']:
                history[i]['previous'] = history[i-1]['new']
                history[i]['change'] = history[i]['new'] - history[i]['previous']
                
    # Recalculate derived metrics
    VirtueService.recalculate_derived_metrics(metrics)
    
    # Save repairs
    metrics.save()
    
    return metrics
```

## Performance Considerations

Virtue Metrics implementations should consider:

1. **Batch Updates**:
   - Batch multiple virtue changes in a single transaction when possible
   - Especially important after completing complex experiences

2. **History Pruning**:
   - Implement policies for pruning old history entries
   - Consider aggregating older entries (e.g., daily summaries past 3 months)

3. **Calculation Caching**:
   - Cache derived metrics that are expensive to calculate
   - Invalidate cache when virtues are updated

Example performance optimization:

```python
class VirtueMetricsCache:
    """Cache for expensive virtue metrics calculations."""
    
    @staticmethod
    def get_growth_summary(user_id, period_days=30):
        """Get cached growth summary or calculate and cache."""
        cache_key = f"virtue_growth:{user_id}:{period_days}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        # Calculate if not in cache
        from users.models import User
        user = User.objects.get(id=user_id)
        summary = VirtueAnalyticsService.get_growth_summary(user, period_days)
        
        # Cache for 1 hour
        cache.set(cache_key, summary, 60*60)
        
        return summary
    
    @staticmethod
    def invalidate_growth_summary(user_id):
        """Invalidate cache when virtues change."""
        # Clear all period caches
        for period in [7, 30, 90]:
            cache_key = f"virtue_growth:{user_id}:{period}"
            cache.delete(cache_key)
```

## Related Patterns

- [Matrix Flow](matrix_flow.md)
- [Experience Design](experience_design.md)
- [User Progress Tracking](user_progress_tracking.md) 