# Matrix Flow Patterns

## Overview

The Matrix Flow is a fundamental philosophical and mechanical concept in Atlantis Go, based on the rhythm of human growth and development. It represents a four-stage cycle through which experiences, activities, and growth occur. This pattern document explains how to implement and utilize the Matrix Flow across different components of the system.

## Matrix Quadrants

The Matrix Flow consists of four quadrants, each representing a different aspect of human experience:

1. **Soul Out (SO)**: Represents wisdom and courage, focused on understanding and initiating
2. **Body Out (BO)**: Represents strength and endurance, focused on physical action and implementation
3. **Soul In (SI)**: Represents temperance and justice, focused on reflection and integration
4. **Body In (BI)**: Represents health and beauty, focused on embodiment and nurturing

Each quadrant has specific virtues associated with it and tends to follow a cyclical pattern: SO → BO → SI → BI → SO.

## Common Patterns

### Pattern 1: Matrix Flow in Experience Design

**Purpose**: Structure experiences to guide users through all four quadrants of development.

**Implementation**:

```python
class Experience(models.Model):
    # Basic fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Matrix flow fields
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
    
    # Matrix flow progression tracking
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
    
    def advance_quadrant(self):
        """Advance to the next quadrant in the matrix flow."""
        flow_sequence = ['SO', 'BO', 'SI', 'BI']
        current_index = flow_sequence.index(self.current_quadrant)
        next_index = (current_index + 1) % len(flow_sequence)
        self.current_quadrant = flow_sequence[next_index]
        self.save(update_fields=['current_quadrant'])
        return self.current_quadrant
    
    def get_current_component(self):
        """Get the content for the current quadrant."""
        component_map = {
            'SO': self.soul_out_component,
            'BO': self.body_out_component,
            'SI': self.soul_in_component,
            'BI': self.body_in_component
        }
        return component_map.get(self.current_quadrant)
```

**Key Points**:
- Each experience explicitly defines components for all four quadrants
- Experiences track current quadrant for each participant
- Progress through experiences follows the matrix flow sequence

**When to Use**:
- When designing new experience types
- When structuring learning activities
- When implementing progression systems

**When to Avoid**:
- For simple, non-educational interactions
- When an experience naturally belongs to only one quadrant

### Pattern 2: Matrix Quadrant Calculation

**Purpose**: Determine a user's dominant quadrant based on their virtue metrics.

**Implementation**:

```python
def calculate_matrix_quadrant(virtue_metrics):
    """
    Calculate the dominant matrix quadrant based on virtue patterns.
    Returns one of: 'SO', 'BO', 'SI', 'BI'
    """
    # Calculate score for each quadrant
    quadrant_scores = {
        'SO': (virtue_metrics.wisdom + virtue_metrics.courage) / 2,
        'BO': (virtue_metrics.strength + virtue_metrics.endurance) / 2,
        'SI': (virtue_metrics.temperance + virtue_metrics.justice) / 2,
        'BI': (virtue_metrics.health + virtue_metrics.beauty) / 2
    }
    
    # Find dominant quadrant (highest score)
    dominant_quadrant = max(quadrant_scores.items(), key=lambda x: x[1])[0]
    
    return dominant_quadrant

def calculate_quadrant_balance(virtue_metrics):
    """
    Calculate how balanced a user is across all quadrants.
    Returns a value between 0 (completely unbalanced) and 1 (perfectly balanced).
    """
    quadrant_scores = {
        'SO': (virtue_metrics.wisdom + virtue_metrics.courage) / 2,
        'BO': (virtue_metrics.strength + virtue_metrics.endurance) / 2,
        'SI': (virtue_metrics.temperance + virtue_metrics.justice) / 2,
        'BI': (virtue_metrics.health + virtue_metrics.beauty) / 2
    }
    
    # Calculate average and variance
    values = list(quadrant_scores.values())
    avg = sum(values) / len(values)
    variance = sum((v - avg) ** 2 for v in values) / len(values)
    
    # Max possible variance would be if one quadrant had max value (100)
    # and others had minimum (0)
    # For 4 quadrants: [(100-25)² + 3*(0-25)²]/4 = 1875
    max_variance = 1875  
    
    # Return balance as inverse of normalized variance
    balance = 1 - (variance / max_variance)
    return balance
```

**Key Points**:
- Quadrant calculation uses the average of associated virtues
- Balance calculation measures variance across quadrants
- Higher balance scores indicate more well-rounded development

**When to Use**:
- For user profiling and recommendations
- When determining which experiences to suggest
- For visualization of user development

**When to Avoid**:
- When virtues aren't the primary focus (e.g., in purely technical contexts)

### Pattern 3: Matrix-Based Experience Recommendations

**Purpose**: Recommend experiences based on a user's matrix quadrant profile.

**Implementation**:

```python
class ExperienceRecommendationService:
    def get_quadrant_recommendations(self, user):
        """
        Recommend experiences based on matrix quadrant analysis.
        Uses three strategies:
        1. Dominant quadrant alignment (strengthen strengths)
        2. Weakest quadrant development (address weaknesses)
        3. Next quadrant in flow (maintain flow progression)
        """
        # Get the user's virtue metrics
        try:
            virtue_metrics = user.virtue_metrics
        except AttributeError:
            return {'error': 'User does not have virtue metrics'}
        
        # Calculate dominant and weakest quadrants
        quadrant_scores = {
            'SO': (virtue_metrics.wisdom + virtue_metrics.courage) / 2,
            'BO': (virtue_metrics.strength + virtue_metrics.endurance) / 2,
            'SI': (virtue_metrics.temperance + virtue_metrics.justice) / 2,
            'BI': (virtue_metrics.health + virtue_metrics.beauty) / 2
        }
        
        dominant = max(quadrant_scores.items(), key=lambda x: x[1])[0]
        weakest = min(quadrant_scores.items(), key=lambda x: x[1])[0]
        
        # Determine next quadrant in flow
        flow_sequence = ['SO', 'BO', 'SI', 'BI']
        current_index = flow_sequence.index(dominant)
        next_index = (current_index + 1) % len(flow_sequence)
        next_quadrant = flow_sequence[next_index]
        
        # Get recommendations for each strategy
        from experience.models import Experience
        
        # Strategy 1: Strengthen strengths
        strength_experiences = Experience.objects.filter(
            models.Q(primary_quadrant=dominant) &
            ~models.Q(id__in=user.completed_experiences.values_list('id', flat=True))
        ).order_by('?')[:3]
        
        # Strategy 2: Address weaknesses
        weakness_experiences = Experience.objects.filter(
            models.Q(primary_quadrant=weakest) &
            ~models.Q(id__in=user.completed_experiences.values_list('id', flat=True))
        ).order_by('?')[:3]
        
        # Strategy 3: Maintain flow progression
        flow_experiences = Experience.objects.filter(
            models.Q(primary_quadrant=next_quadrant) &
            ~models.Q(id__in=user.completed_experiences.values_list('id', flat=True))
        ).order_by('?')[:3]
        
        return {
            'dominant_quadrant': dominant,
            'weakest_quadrant': weakest,
            'next_in_flow': next_quadrant,
            'recommendations': {
                'strengthen': strength_experiences,
                'develop': weakness_experiences,
                'flow': flow_experiences
            }
        }
```

**Key Points**:
- Uses multiple recommendation strategies
- Considers both strengths and weaknesses
- Maintains the natural flow progression

**When to Use**:
- For personalized user recommendations
- When implementing AI guide features
- For balancing user development

**When to Avoid**:
- When user has explicitly selected a focus area
- For non-matrix-related recommendations

### Pattern 4: Matrix Flow in Zone Classification

**Purpose**: Classify zones according to matrix quadrants to create a balanced environment.

**Implementation**:

```python
class Zone(models.Model):
    # Basic fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.PointField()
    
    # Matrix classification
    matrix_quadrant = models.CharField(
        max_length=2,
        choices=[
            ('SO', 'Soul Out'),
            ('BO', 'Body Out'),
            ('SI', 'Soul In'),
            ('BI', 'Body In'),
        ],
        default='SO'
    )
    
    # Zone type influences available activities
    zone_type = models.CharField(
        max_length=50,
        choices=[
            ('EDUCATION', 'Educational Zone'),
            ('EXERCISE', 'Exercise Zone'),
            ('REFLECTION', 'Reflection Zone'),
            ('ARTS', 'Arts Zone'),
            # Other zone types...
        ]
    )
    
    @property
    def quadrant_activities(self):
        """Get activities appropriate for this zone's quadrant."""
        from activities.models import Activity
        
        return Activity.objects.filter(
            matrix_quadrant=self.matrix_quadrant
        )
    
    @staticmethod
    def get_balanced_zone_distribution(area_polygon, count=4):
        """
        Generate a balanced distribution of zones in a geographic area,
        with one zone for each matrix quadrant.
        """
        from django.contrib.gis.geos import Point
        import random
        
        # Generate random points within the polygon
        points = []
        min_x, min_y, max_x, max_y = area_polygon.extent
        
        while len(points) < count:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            point = Point(x, y)
            
            if point.within(area_polygon):
                points.append(point)
        
        # Create one zone for each quadrant
        quadrants = ['SO', 'BO', 'SI', 'BI']
        zone_types = {
            'SO': 'EDUCATION',
            'BO': 'EXERCISE',
            'SI': 'REFLECTION',
            'BI': 'ARTS'
        }
        
        zones = []
        for i, point in enumerate(points[:4]):
            quadrant = quadrants[i]
            
            zone = Zone.objects.create(
                name=f"{quadrant} Zone",
                description=f"A zone focused on {quadrant} development",
                location=point,
                matrix_quadrant=quadrant,
                zone_type=zone_types[quadrant]
            )
            zones.append(zone)
        
        return zones
```

**Key Points**:
- Zones are classified by matrix quadrant
- Zone types align with quadrant focus
- Balanced zone distribution ensures all quadrants are represented

**When to Use**:
- When designing the geographic layout
- When classifying different areas of the application
- When creating a balanced ecosystem

**When to Avoid**:
- For zones with highly specific purposes that don't fit the matrix model

## Uncertainty Handling

When implementing Matrix Flow patterns, several forms of uncertainty may arise:

1. **Ambiguous Quadrant Classification**:
   - When a user has nearly equal scores in multiple quadrants
   - Solution: Identify secondary quadrant and consider both in recommendations

2. **Incomplete Matrix Data**:
   - When not all quadrant components are defined for an experience
   - Solution: Use default templates or skip missing quadrants

3. **Flow Interruptions**:
   - When user activity doesn't follow the natural flow
   - Solution: Allow flow jumping but track ideal path for guidance

Example handling code:

```python
def handle_ambiguous_classification(virtue_metrics, threshold=5):
    """Handle cases where multiple quadrants have similar scores."""
    quadrant_scores = {
        'SO': (virtue_metrics.wisdom + virtue_metrics.courage) / 2,
        'BO': (virtue_metrics.strength + virtue_metrics.endurance) / 2,
        'SI': (virtue_metrics.temperance + virtue_metrics.justice) / 2,
        'BI': (virtue_metrics.health + virtue_metrics.beauty) / 2
    }
    
    # Sort quadrants by score
    sorted_quadrants = sorted(quadrant_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Check if top two are within threshold
    if sorted_quadrants[0][1] - sorted_quadrants[1][1] <= threshold:
        return {
            'primary': sorted_quadrants[0][0],
            'secondary': sorted_quadrants[1][0],
            'is_ambiguous': True
        }
    
    return {
        'primary': sorted_quadrants[0][0],
        'secondary': None,
        'is_ambiguous': False
    }
```

## Error Recovery

Common errors in Matrix Flow implementation include:

1. **Circular Flow Patterns**:
   - Problem: Custom flows that don't follow the standard sequence
   - Resolution: Allow custom flows but validate they visit each quadrant

2. **Missing Quadrant Implementation**:
   - Problem: Experience doesn't implement all quadrants
   - Resolution: Provide templates and defaults for each quadrant

3. **Quadrant Calculation Errors**:
   - Problem: Miscalculations due to missing or invalid virtue data
   - Resolution: Implement default values and validation

Example error recovery code:

```python
def ensure_complete_matrix_flow(experience):
    """Ensure an experience has all required matrix flow components."""
    quadrants = ['soul_out_component', 'body_out_component', 
                 'soul_in_component', 'body_in_component']
    
    templates = {
        'soul_out_component': "Understand the principles and concepts behind {experience.name}.",
        'body_out_component': "Practice the physical components of {experience.name}.",
        'soul_in_component': "Reflect on what you've learned about {experience.name}.",
        'body_in_component': "Embody and nurture the results of your {experience.name} practice."
    }
    
    updated = False
    
    for quadrant in quadrants:
        if not getattr(experience, quadrant):
            setattr(experience, quadrant, templates[quadrant].format(experience=experience))
            updated = True
    
    if updated:
        experience.save()
    
    return experience
```

## Performance Considerations

Matrix Flow implementations should consider:

1. **Calculation Caching**:
   - Cache matrix quadrant calculations to avoid recalculating frequently
   - Update cache when virtue metrics change

2. **Precomputed Recommendations**:
   - Generate and cache recommendations during off-peak times
   - Update when user completes relevant experiences

3. **Bulk Matrix Operations**:
   - When processing multiple users, use bulk database operations
   - Avoid recalculating matrix data for unchanged virtue metrics

Example performance optimization:

```python
class MatrixFlowCache:
    """Cache for matrix flow calculations."""
    
    @staticmethod
    def get_user_quadrant(user_id):
        """Get cached quadrant or calculate and cache."""
        cache_key = f"matrix_quadrant:{user_id}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        # Calculate if not in cache
        from users.models import User
        user = User.objects.select_related('virtue_metrics').get(id=user_id)
        quadrant = calculate_matrix_quadrant(user.virtue_metrics)
        
        # Cache for 12 hours
        cache.set(cache_key, quadrant, 60*60*12)
        
        return quadrant
    
    @staticmethod
    def invalidate_user_quadrant(user_id):
        """Invalidate cache when virtue metrics change."""
        cache_key = f"matrix_quadrant:{user_id}"
        cache.delete(cache_key)
```

## Related Patterns

- [Virtue Metrics Calculation](virtue_metrics_calculation.md)
- [Experience Progression](experience_progression.md)
- [Zone Geographic Patterns](zone_geographic_patterns.md) 