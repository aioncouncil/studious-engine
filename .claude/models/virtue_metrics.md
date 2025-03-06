# VirtueMetrics Model

## Purpose

The VirtueMetrics model tracks a user's progress in developing virtues, which are central to the Atlantis Go philosophy. This model stores both current virtue levels and historical data, enabling the system to calculate changes, recommend experiences, and track overall growth. Virtues are organized into cardinal virtues (wisdom, courage, temperance, justice) and physical virtues (strength, health, beauty, endurance).

## Schema

### Fields

| Field Name | Type | Description | Constraints |
|------------|------|-------------|------------|
| id | UUID | Primary key | Auto-generated |
| user | ForeignKey | User this record belongs to | One-to-One, On delete CASCADE |
| wisdom | Integer | Wisdom virtue level | Range 0-100, Default=10 |
| courage | Integer | Courage virtue level | Range 0-100, Default=10 |
| temperance | Integer | Temperance virtue level | Range 0-100, Default=10 |
| justice | Integer | Justice virtue level | Range 0-100, Default=10 |
| strength | Integer | Strength virtue level | Range 0-100, Default=10 |
| health | Integer | Health virtue level | Range 0-100, Default=10 |
| beauty | Integer | Beauty virtue level | Range 0-100, Default=10 |
| endurance | Integer | Endurance virtue level | Range 0-100, Default=10 |
| virtue_history | JSONB | Historical virtue changes | Default=[] |
| happiness_score | Integer | Calculated happiness level | Range 0-100, Default=50 |
| last_calculated | DateTime | Last calculation timestamp | Auto update on save |
| matrix_quadrant | String | Dominant matrix quadrant | Enum(SO, BO, SI, BI), nullable |

### Relationships

| Relationship | Type | Related Model | Through | Description |
|-------------|------|--------------|---------|-------------|
| user | Many-to-One | User | user_id | User whose virtues are tracked |

## Patterns

### Creation Pattern

```python
# Create new VirtueMetrics for a user
from core.models import VirtueMetrics

virtue_metrics = VirtueMetrics.objects.create(
    user=user,
    wisdom=10,
    courage=10,
    temperance=10,
    justice=10,
    strength=10,
    health=10,
    beauty=10,
    endurance=10,
    virtue_history=[],
    happiness_score=50
)
```

### Query Patterns

```python
# Get a user's virtue metrics
metrics = VirtueMetrics.objects.get(user=user)

# Find users with high wisdom
wise_users = VirtueMetrics.objects.filter(wisdom__gte=70).select_related('user')

# Find users with balanced virtues
balanced_users = VirtueMetrics.objects.filter(
    wisdom__gte=50,
    courage__gte=50,
    temperance__gte=50,
    justice__gte=50
).select_related('user')

# Get users in a specific matrix quadrant
soul_out_users = VirtueMetrics.objects.filter(matrix_quadrant='SO').select_related('user')

# Get users with happiness below threshold (potential for intervention)
unhappy_users = VirtueMetrics.objects.filter(happiness_score__lt=30).select_related('user')
```

### Update Patterns

```python
# Update a single virtue
def update_virtue(user_id, virtue_name, change_amount, source=None):
    try:
        metrics = VirtueMetrics.objects.get(user_id=user_id)
        
        # Get current value
        current_value = getattr(metrics, virtue_name)
        
        # Apply change with bounds checking
        new_value = max(0, min(100, current_value + change_amount))
        setattr(metrics, virtue_name, new_value)
        
        # Record in history
        timestamp = timezone.now().isoformat()
        history_entry = {
            "timestamp": timestamp,
            "virtue": virtue_name,
            "old_value": current_value,
            "new_value": new_value,
            "change": change_amount,
            "source": source or "unknown"
        }
        
        # Append to history
        metrics.virtue_history.append(history_entry)
        
        # Recalculate happiness and save
        metrics.calculate_happiness()
        metrics.save()
        
        return True, new_value
    except VirtueMetrics.DoesNotExist:
        return False, "VirtueMetrics not found"
    except Exception as e:
        return False, str(e)

# Update multiple virtues at once
def update_multiple_virtues(user_id, virtue_changes, source=None):
    try:
        metrics = VirtueMetrics.objects.get(user_id=user_id)
        history_entries = []
        timestamp = timezone.now().isoformat()
        
        for virtue_name, change_amount in virtue_changes.items():
            if hasattr(metrics, virtue_name):
                current_value = getattr(metrics, virtue_name)
                new_value = max(0, min(100, current_value + change_amount))
                setattr(metrics, virtue_name, new_value)
                
                history_entries.append({
                    "timestamp": timestamp,
                    "virtue": virtue_name,
                    "old_value": current_value,
                    "new_value": new_value,
                    "change": change_amount,
                    "source": source or "unknown"
                })
        
        # Extend history with new entries
        metrics.virtue_history.extend(history_entries)
        
        # Recalculate happiness and save
        metrics.calculate_happiness()
        metrics.save()
        
        return True, "Virtues updated successfully"
    except VirtueMetrics.DoesNotExist:
        return False, "VirtueMetrics not found"
    except Exception as e:
        return False, str(e)
```

### Complex Calculations

```python
# Calculate happiness based on virtue balance
def calculate_happiness(self):
    """
    Calculate happiness based on virtue levels and balance.
    The formula considers:
    1. Overall virtue levels (higher is better)
    2. Balance between virtues (balanced is better)
    3. Recent positive changes
    """
    # Calculate average virtue level
    cardinal_virtues = [self.wisdom, self.courage, self.temperance, self.justice]
    physical_virtues = [self.strength, self.health, self.beauty, self.endurance]
    
    cardinal_avg = sum(cardinal_virtues) / len(cardinal_virtues)
    physical_avg = sum(physical_virtues) / len(physical_virtues)
    overall_avg = (cardinal_avg + physical_avg) / 2
    
    # Calculate variance (lower is better, indicating balance)
    all_virtues = cardinal_virtues + physical_virtues
    variance = sum((v - overall_avg) ** 2 for v in all_virtues) / len(all_virtues)
    balance_factor = 100 - min(variance, 100)  # Lower variance = higher balance
    
    # Base happiness from average levels
    base_happiness = overall_avg * 0.7
    
    # Balance contribution
    balance_contribution = balance_factor * 0.3
    
    # Calculate final happiness score
    self.happiness_score = int(base_happiness + balance_contribution)
    self.last_calculated = timezone.now()
    
    # Determine matrix quadrant
    self._calculate_matrix_quadrant()
    
    return self.happiness_score

# Calculate matrix quadrant
def _calculate_matrix_quadrant(self):
    """
    Determine the dominant matrix quadrant based on virtue patterns.
    SO (Soul Out): High wisdom and courage
    BO (Body Out): High strength and endurance
    SI (Soul In): High temperance and justice
    BI (Body In): High health and beauty
    """
    quadrant_scores = {
        'SO': (self.wisdom + self.courage) / 2,
        'BO': (self.strength + self.endurance) / 2,
        'SI': (self.temperance + self.justice) / 2,
        'BI': (self.health + self.beauty) / 2
    }
    
    # Find quadrant with highest score
    self.matrix_quadrant = max(quadrant_scores.items(), key=lambda x: x[1])[0]
    
    return self.matrix_quadrant
```

## Interfaces

### Main Properties

```python
@property
def cardinal_virtues_avg(self):
    """Returns the average of cardinal virtues."""
    virtues = [self.wisdom, self.courage, self.temperance, self.justice]
    return sum(virtues) / len(virtues)

@property
def physical_virtues_avg(self):
    """Returns the average of physical virtues."""
    virtues = [self.strength, self.health, self.beauty, self.endurance]
    return sum(virtues) / len(virtues)

@property
def dominant_virtue(self):
    """Returns the name of the highest virtue."""
    virtues = {
        'wisdom': self.wisdom,
        'courage': self.courage,
        'temperance': self.temperance,
        'justice': self.justice,
        'strength': self.strength,
        'health': self.health,
        'beauty': self.beauty,
        'endurance': self.endurance
    }
    return max(virtues.items(), key=lambda x: x[1])[0]

@property
def recent_changes(self, days=7):
    """Returns virtue changes in the last X days."""
    if not self.virtue_history:
        return {}
    
    # Filter history entries within time range
    cutoff_date = (timezone.now() - timedelta(days=days)).isoformat()
    recent_entries = [
        entry for entry in self.virtue_history 
        if entry['timestamp'] >= cutoff_date
    ]
    
    # Aggregate changes by virtue
    changes = {}
    for entry in recent_entries:
        virtue = entry['virtue']
        change = entry['change']
        if virtue in changes:
            changes[virtue] += change
        else:
            changes[virtue] = change
    
    return changes
```

### Public Methods

```python
def get_virtue_history(self, virtue_name=None, days=30):
    """Get historical data for specified virtue(s)."""
    if not self.virtue_history:
        return []
    
    # Filter by time
    cutoff_date = (timezone.now() - timedelta(days=days)).isoformat()
    filtered_history = [
        entry for entry in self.virtue_history 
        if entry['timestamp'] >= cutoff_date
    ]
    
    # Filter by virtue if specified
    if virtue_name:
        filtered_history = [
            entry for entry in filtered_history 
            if entry['virtue'] == virtue_name
        ]
    
    return filtered_history

def get_growth_rate(self, virtue_name, days=30):
    """Calculate growth rate for a virtue over time period."""
    history = self.get_virtue_history(virtue_name, days)
    
    if not history:
        return 0
    
    # Sum all changes
    total_change = sum(entry['change'] for entry in history)
    
    # Calculate daily rate
    return total_change / days

def get_recommended_focus(self):
    """Identify which virtue needs the most attention."""
    virtues = {
        'wisdom': self.wisdom,
        'courage': self.courage,
        'temperance': self.temperance,
        'justice': self.justice,
        'strength': self.strength,
        'health': self.health,
        'beauty': self.beauty,
        'endurance': self.endurance
    }
    
    # Find the lowest virtue
    lowest_virtue = min(virtues.items(), key=lambda x: x[1])
    
    return {
        'virtue': lowest_virtue[0],
        'current_value': lowest_virtue[1],
        'suggested_activities': self._get_activities_for_virtue(lowest_virtue[0])
    }

def _get_activities_for_virtue(self, virtue_name):
    """Get recommended activities to improve a specific virtue."""
    # This would integrate with the Experience or Art systems
    from experience.services import ExperienceRecommendationService
    
    service = ExperienceRecommendationService()
    return service.get_recommendations_for_virtue(virtue_name)
```

## Invariants

The following invariants must be maintained:

1. All virtue values must be between 0 and 100 inclusive
2. The user reference must always be valid and unique (one VirtueMetrics per user)
3. Virtue history must be a valid JSON array of change records
4. Happiness score must be recalculated whenever virtue values change
5. Matrix quadrant must reflect the dominant virtue pattern
6. Last_calculated timestamp must be updated on every recalculation

## Error States

### Invalid Virtue Value

- **Cause**: Attempt to set a virtue value outside the 0-100 range
- **Detection**: Validation during save
- **Resolution**: Clamp values to the valid range before saving

### Corrupted History Data

- **Cause**: Invalid JSON structure in virtue_history field
- **Detection**: ValueError during deserialization
- **Resolution**: Initialize with empty array, implement validation before saving

### Calculation Timeout

- **Cause**: Complex happiness calculations taking too long
- **Detection**: TimeoutError during calculation
- **Resolution**: Optimize calculation algorithm, implement caching

### Orphaned Record

- **Cause**: VirtueMetrics record exists but User was deleted
- **Detection**: IntegrityError during query or CASCADE on delete
- **Resolution**: Ensure proper CASCADE delete behavior, implement periodic cleanup 