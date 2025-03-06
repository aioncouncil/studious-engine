# User Model

## Purpose

The User model is the central entity in the Atlantis Go system, representing a player's identity, authentication, and core profile information. It serves as the foundation for tracking player progress, preferences, location, and interactions across all components of the application.

## Schema

### Fields

| Field Name | Type | Description | Constraints |
|------------|------|-------------|------------|
| id | UUID | Primary key | Auto-generated |
| username | String | Unique username | Required, Unique |
| email | String | Email address | Required, Unique |
| password | String | Encrypted password | Required |
| first_name | String | First name | Optional |
| last_name | String | Last name | Optional |
| date_joined | DateTime | Registration date | Auto (now) |
| last_login | DateTime | Last login timestamp | Auto |
| is_active | Boolean | Account active status | Default=True |
| is_staff | Boolean | Staff access status | Default=False |
| rank | Integer | Player rank (1-4) | Default=1 |
| economic_layer | String | Economic layer access | Enum(PORT, LAWS, REPUBLIC), Default=PORT |
| tutorial_progress | JSONB | Tutorial completion tracking | Default={} |
| device_settings | JSONB | Device-specific settings | Default={} |

### Relationships

| Relationship | Type | Related Model | Through | Description |
|-------------|------|--------------|---------|-------------|
| profile | One-to-One | PlayerProfile | profile (reverse) | Extended profile information |
| virtue_metrics | One-to-One | VirtueMetrics | user (reverse) | Virtue scores and history |
| preferences | One-to-One | UserPreferences | user (reverse) | User preferences and settings |
| location | One-to-One | UserLocation | user (reverse) | Geospatial location tracking |
| art_masteries | One-to-Many | ArtMastery | user (reverse) | Art collection and mastery progress |
| experience_instances | One-to-Many | ExperienceInstance | user (reverse) | Experience participation |
| zone_memberships | One-to-Many | ZoneMembership | user (reverse) | Zone participation |
| tech_tree_progress | One-to-Many | UserTechTreeProgress | user (reverse) | Tech tree progression |
| resource_inventory | One-to-One | ResourceInventory | user (reverse) | Resource holdings |

## Patterns

### Creation Pattern

```python
# Basic user creation
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.create_user(
    username="johndoe",
    email="john@example.com",
    password="secure_password",
    first_name="John",
    last_name="Doe",
    rank=1,
    economic_layer="PORT",
    tutorial_progress={"intro_completed": True},
    device_settings={"notifications_enabled": True}
)

# Create related models
from core.models import PlayerProfile, VirtueMetrics, UserPreferences, UserLocation

PlayerProfile.objects.create(
    user=user,
    bio="Game enthusiast",
    avatar="avatars/default.png"
)

VirtueMetrics.objects.create(
    user=user,
    wisdom=10,
    courage=10,
    temperance=10,
    justice=10
)

UserPreferences.objects.create(
    user=user,
    language="en",
    theme="light",
    notification_preferences={"daily_summary": True}
)

UserLocation.objects.create(
    user=user,
    latitude=37.7749,
    longitude=-122.4194,
    last_updated=timezone.now()
)
```

### Query Patterns

```python
# Get user by username
user = User.objects.get(username="johndoe")

# Get user with related models
user = User.objects.select_related(
    'profile', 
    'virtue_metrics', 
    'preferences', 
    'location'
).get(id=user_id)

# Filter users by rank
advanced_users = User.objects.filter(rank__gte=3)

# Filter users by economic layer
republic_users = User.objects.filter(economic_layer="REPUBLIC")

# Get users in a specific zone
zone_users = User.objects.filter(zone_memberships__zone_id=zone_id)

# Get users who have mastered a specific art
art_masters = User.objects.filter(
    art_masteries__art_id=art_id,
    art_masteries__mastery_level__gte=90
)

# Get users with specific virtue metrics
wise_users = User.objects.filter(virtue_metrics__wisdom__gte=50)
```

### Update Patterns

```python
# Update user rank
user.rank = 2
user.save(update_fields=['rank'])

# Update economic layer
user.economic_layer = "LAWS"
user.save(update_fields=['economic_layer'])

# Update tutorial progress
tutorial_progress = user.tutorial_progress
tutorial_progress['market_completed'] = True
user.tutorial_progress = tutorial_progress
user.save(update_fields=['tutorial_progress'])

# Update device settings
device_settings = user.device_settings
device_settings['push_enabled'] = False
user.device_settings = device_settings
user.save(update_fields=['device_settings'])
```

### Deletion Pattern

```python
# Safe deletion with cascading effects
def safe_delete_user(user_id):
    try:
        user = User.objects.get(pk=user_id)
        
        # Optional: Instead of deleting, mark as inactive
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        # If permanent deletion is required:
        # user.delete()  # This will cascade to all related models
        
        return True, "User deactivated successfully"
    except User.DoesNotExist:
        return False, "User not found"
```

## Interfaces

### Main Properties

```python
@property
def full_name(self):
    """Returns the user's full name or username if not available."""
    if self.first_name or self.last_name:
        return f"{self.first_name} {self.last_name}".strip()
    return self.username

@property
def primary_virtue(self):
    """Returns the user's highest virtue."""
    if not hasattr(self, 'virtue_metrics'):
        return None
    
    virtues = {
        'wisdom': self.virtue_metrics.wisdom,
        'courage': self.virtue_metrics.courage,
        'temperance': self.virtue_metrics.temperance,
        'justice': self.virtue_metrics.justice
    }
    
    return max(virtues.items(), key=lambda x: x[1])[0]

@property
def arts_discovered(self):
    """Returns the count of arts discovered by the user."""
    return self.art_masteries.count()

@property
def arts_mastered(self):
    """Returns the count of arts mastered by the user."""
    return self.art_masteries.filter(mastery_level__gte=90).count()
```

### Public Methods

```python
def increase_rank(self):
    """Increase user rank if eligible."""
    if self.rank < 4:  # Max rank is 4
        self.rank += 1
        self.save(update_fields=['rank'])
        return True
    return False

def advance_economic_layer(self):
    """Advance to the next economic layer if eligible."""
    layers = ["PORT", "LAWS", "REPUBLIC"]
    current_index = layers.index(self.economic_layer)
    
    if current_index < len(layers) - 1:
        self.economic_layer = layers[current_index + 1]
        self.save(update_fields=['economic_layer'])
        return True
    return False

def get_zone_access(self):
    """Get zones the user has access to."""
    from zone.models import Zone
    return Zone.objects.filter(
        models.Q(zone_memberships__user=self) | 
        models.Q(is_public=True)
    ).distinct()

def is_eligible_for_art(self, art):
    """Check if user is eligible to discover an art."""
    # Check rank requirement
    if self.rank < art.rank_required:
        return False
    
    # Check economic layer requirement
    layers = ["PORT", "LAWS", "REPUBLIC"]
    user_layer_index = layers.index(self.economic_layer)
    art_layer_index = layers.index(art.economic_layer_required)
    
    if user_layer_index < art_layer_index:
        return False
    
    # Additional checks can be implemented here
    
    return True
```

## Invariants

The following invariants must be maintained:

1. Username must be unique across all users
2. Email must be unique across all users
3. Rank must be between 1 and 4
4. Economic layer must be one of: "PORT", "LAWS", "REPUBLIC"
5. Tutorial progress and device settings must be valid JSON objects
6. A user must have exactly one PlayerProfile, VirtueMetrics, UserPreferences, and UserLocation
7. When a user is deleted, all related models should be deleted (CASCADE)

## Error States

### Authentication Errors

- **Cause**: Invalid credentials during login
- **Detection**: Failed login attempts
- **Resolution**: Provide appropriate error messages, implement rate limiting for security

### Duplicate Username/Email

- **Cause**: Attempting to create a user with an existing username or email
- **Detection**: IntegrityError during user creation
- **Resolution**: Validate uniqueness before creation, provide clear error message

### Invalid JSON Format

- **Cause**: Malformed JSON in tutorial_progress or device_settings fields
- **Detection**: ValidationError during save
- **Resolution**: Validate JSON structure before saving, provide default values on error

### Missing Required Related Models

- **Cause**: User created without required related models (profile, virtue_metrics, etc.)
- **Detection**: RelatedObjectDoesNotExist when accessing attributes
- **Resolution**: Create related models in a transaction during user creation, implement signal handlers

### Permission Denied

- **Cause**: User attempting to access features beyond their rank or economic layer
- **Detection**: Permission checks in views or services
- **Resolution**: Implement robust permission checking, provide clear guidance on requirements 