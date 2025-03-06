# Virtue Metrics Calculation Debugging Guide

This document contains solutions for common issues encountered when implementing or debugging the Virtue Metrics Calculation pattern.

## Issue: Inconsistent happiness scores across user sessions

### Symptoms

- Users report fluctuating happiness scores when refreshing the page
- Happiness score calculation produces different results for the same input values
- Logs show multiple recalculations within short time periods

### Affected Components

- CORE_USER_SYSTEM
- VirtueMetrics model
- HappinessCalculationService

### Root Cause

The happiness score calculation was not properly normalized and was sensitive to the order of operations. The floating-point calculations had precision issues that caused slight variations depending on the execution path.

### Solution

Standardized the calculation with explicit rounding and a consistent order of operations:

```python
def calculate_happiness_score(self):
    """Calculate happiness score based on virtue balance."""
    # Get the virtue values
    cardinal_virtues = [
        self.wisdom, 
        self.courage, 
        self.temperance, 
        self.justice
    ]
    physical_virtues = [
        self.strength, 
        self.health, 
        self.beauty, 
        self.endurance
    ]
    
    # Calculate averages with consistent precision
    cardinal_avg = round(sum(cardinal_virtues) / len(cardinal_virtues), 2)
    physical_avg = round(sum(physical_virtues) / len(physical_virtues), 2)
    
    # Calculate variance with consistent precision
    cardinal_variance = round(sum((v - cardinal_avg) ** 2 for v in cardinal_virtues) / len(cardinal_virtues), 2)
    physical_variance = round(sum((v - physical_avg) ** 2 for v in physical_virtues) / len(physical_virtues), 2)
    
    # Calculate the balance factor (lower variance = better balance)
    balance_factor = round(100 - (cardinal_variance + physical_variance) / 2, 2)
    
    # Calculate the overall score with weights
    base_score = round(0.7 * (cardinal_avg + physical_avg) / 2 + 0.3 * balance_factor, 2)
    
    # Ensure the score is within bounds
    happiness_score = max(0, min(100, base_score))
    
    return happiness_score
```

Also added a caching mechanism to prevent recalculation unless virtue values change:

```python
def save(self, *args, **kwargs):
    """Override save to ensure happiness score is calculated consistently."""
    # Check if any virtue values have changed
    if self.pk:
        old_values = VirtueMetrics.objects.get(pk=self.pk)
        virtues_changed = any(
            getattr(self, virtue) != getattr(old_values, virtue)
            for virtue in self.VIRTUE_FIELDS
        )
        
        # Only recalculate if virtues changed or happiness score is None
        if virtues_changed or self.happiness_score is None:
            self.happiness_score = self.calculate_happiness_score()
            self.last_calculated = timezone.now()
    else:
        # New instance, calculate happiness score
        self.happiness_score = self.calculate_happiness_score()
        self.last_calculated = timezone.now()
            
    super().save(*args, **kwargs)
```

### Prevention

- Added unit tests to verify consistent happiness scores for the same inputs
- Documented the precise calculation method in the model documentation
- Added assertions to verify the happiness score remains within 0-100
- Implemented logging to track when and why recalculations occur

## Issue: Matrix quadrant detection not matching user expectations

### Symptoms

- Users report being placed in quadrants that don't match their self-assessment
- Matrix quadrant remains the same despite significant changes in virtues
- Logs show "quadrant boundary case" warnings

### Affected Components

- CORE_USER_SYSTEM
- VirtueMetrics model
- MatrixService

### Root Cause

The matrix quadrant calculation was using simple averages to determine quadrant placement, but this failed to account for the relative strengths in individual virtues that should influence quadrant determination. The calculation also lacked hysteresis, causing users near quadrant boundaries to experience frequent quadrant changes.

### Solution

Implemented a more sophisticated quadrant calculation with weighted scoring and hysteresis:

```python
def determine_matrix_quadrant(self):
    """Determine the user's matrix quadrant based on virtue values."""
    # Calculate the soul and body scores
    soul_out = self.wisdom * 0.6 + self.courage * 0.4
    body_out = self.strength * 0.6 + self.endurance * 0.4
    soul_in = self.temperance * 0.6 + self.justice * 0.4
    body_in = self.health * 0.6 + self.beauty * 0.4
    
    # Calculate quadrant scores
    quadrant_scores = {
        'SO': soul_out,
        'BO': body_out, 
        'SI': soul_in,
        'BI': body_in
    }
    
    # Get current and highest quadrant
    current_quadrant = self.matrix_quadrant
    highest_quadrant = max(quadrant_scores.items(), key=lambda x: x[1])[0]
    
    # Apply hysteresis - only change quadrant if the new highest is significantly higher
    # than the current, or if this is the first calculation
    if current_quadrant is None:
        new_quadrant = highest_quadrant
    else:
        # Get score of current quadrant
        current_score = quadrant_scores[current_quadrant]
        highest_score = quadrant_scores[highest_quadrant]
        
        # Only change if the new highest is at least 10% higher than current
        if highest_score > current_score * 1.1:
            new_quadrant = highest_quadrant
        else:
            new_quadrant = current_quadrant
    
    return new_quadrant
```

Also improved the historical tracking to provide context for quadrant changes:

```python
def record_quadrant_change(self, new_quadrant):
    """Record a change in matrix quadrant with context."""
    if not self.virtue_history:
        self.virtue_history = []
        
    # Add quadrant change to history
    quadrant_change = {
        'timestamp': timezone.now().isoformat(),
        'old_quadrant': self.matrix_quadrant,
        'new_quadrant': new_quadrant,
        'virtues': {
            'wisdom': self.wisdom,
            'courage': self.courage,
            'temperance': self.temperance,
            'justice': self.justice,
            'strength': self.strength,
            'health': self.health, 
            'beauty': self.beauty,
            'endurance': self.endurance
        }
    }
    
    self.virtue_history.append(quadrant_change)
    self.matrix_quadrant = new_quadrant
```

### Prevention

- Added visualization of quadrant boundaries in the user dashboard
- Implemented a "stability threshold" to prevent frequent changes
- Added notifications to explain quadrant changes to users
- Created a matrix position visualization showing relative distance to each quadrant

## Issue: Virtue history growing too large causing performance issues

### Symptoms

- Slow loading times for user profiles with long history
- Database queries timing out when accessing virtue metrics
- Memory usage spikes when processing virtue history
- Error logs showing "exceeded maximum JSON size"

### Affected Components

- CORE_USER_SYSTEM
- VirtueMetrics model
- User profile views

### Root Cause

The virtue history was being stored as a JSON field that continuously grew without any pruning mechanism. Each virtue update added a new entry, eventually leading to excessively large JSON objects that were expensive to serialize, deserialize, and process.

### Solution

Implemented a pruning mechanism to limit history size while preserving meaningful data:

```python
def add_virtue_history_entry(self, changes, context=None):
    """Add an entry to virtue history with pruning if needed."""
    if not self.virtue_history:
        self.virtue_history = []
        
    # Create new history entry
    entry = {
        'timestamp': timezone.now().isoformat(),
        'changes': changes
    }
    
    if context:
        entry['context'] = context
        
    # Add new entry
    self.virtue_history.append(entry)
    
    # Prune history if too large
    if len(self.virtue_history) > settings.MAX_VIRTUE_HISTORY_ENTRIES:
        # Keep the first entry (baseline) and most recent entries
        self.virtue_history = [
            self.virtue_history[0],
            *self.virtue_history[-(settings.MAX_VIRTUE_HISTORY_ENTRIES-1):]
        ]
        
    # Compress older entries (older than 30 days) by aggregating by week
    thirty_days_ago = (timezone.now() - timezone.timedelta(days=30)).isoformat()
    
    # Group old entries by week
    old_entries = [e for e in self.virtue_history if e['timestamp'] < thirty_days_ago]
    recent_entries = [e for e in self.virtue_history if e['timestamp'] >= thirty_days_ago]
    
    if old_entries:
        # Group by week and compress
        weekly_entries = self._aggregate_entries_by_week(old_entries)
        self.virtue_history = weekly_entries + recent_entries
```

Also added a helper method to aggregate weekly data:

```python
def _aggregate_entries_by_week(self, entries):
    """Aggregate history entries by week."""
    from datetime import datetime
    import iso8601
    from collections import defaultdict
    
    # Group by year and week
    weekly_groups = defaultdict(list)
    for entry in entries:
        dt = iso8601.parse_date(entry['timestamp'])
        year, week, _ = dt.isocalendar()
        weekly_groups[(year, week)].append(entry)
    
    # Create aggregated entries
    aggregated = []
    for (year, week), week_entries in weekly_groups.items():
        if len(week_entries) <= 1:
            # No need to aggregate single entries
            aggregated.extend(week_entries)
            continue
            
        # Create an aggregated entry
        first_entry = min(week_entries, key=lambda e: e['timestamp'])
        last_entry = max(week_entries, key=lambda e: e['timestamp'])
        
        aggregated_entry = {
            'timestamp': first_entry['timestamp'],
            'timestamp_end': last_entry['timestamp'],
            'aggregated': True,
            'entry_count': len(week_entries),
            'changes': self._aggregate_virtue_changes(week_entries)
        }
        
        if 'context' in first_entry:
            aggregated_entry['context'] = f"Week {week}, {year}"
            
        aggregated.append(aggregated_entry)
    
    return sorted(aggregated, key=lambda e: e['timestamp'])
```

### Prevention

- Added configuration settings for maximum history size
- Implemented database migrations to prune existing oversized histories
- Added monitoring for JSON field sizes in the database
- Created a scheduled task to periodically compress old history entries

## Tags

#performance #data-integrity #optimization #calculation #matrix-flow 