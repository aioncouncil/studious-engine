# Core User System Cheat Sheet

## Quick Reference Guide

This cheat sheet provides quick reference information for working with the Core User System in the Atlantis Go project.

## Key Models

### User (Django's Built-in User)
- **Purpose**: Authentication and core user information
- **Key fields**: `username`, `email`, `password`, `is_active`, `date_joined`

### PlayerProfile
- **Purpose**: Extended user information and game progression
- **Key fields**: `user`, `rank`, `experience_points`, `economic_layer`, `title`, `bio`
- **Relationships**: OneToOne with `User`

### PlayerHappiness
- **Purpose**: Tracks virtue metrics for the user
- **Key fields**: Multiple virtue metrics (`wisdom`, `courage`, etc.), aggregate scores
- **Relationships**: OneToOne with `PlayerProfile`

### UserPreferences
- **Purpose**: User settings and preferences
- **Key fields**: Various JSON fields for preferences
- **Relationships**: OneToOne with `PlayerProfile`

### UserLocation
- **Purpose**: Tracks user's geographic location
- **Key fields**: `latitude`, `longitude`, `current_zone`, `last_updated`
- **Relationships**: OneToOne with `PlayerProfile`

## Common Operations

### User Creation

```python
from django.contrib.auth import get_user_model
from core.services.user_service import UserService

User = get_user_model()

# Create basic user
user = User.objects.create_user(
    username='johndoe',
    email='john@example.com',
    password='securepassword'
)

# Create complete user profile with related models
profile = UserService.create_user_profile(user)
```

### User Authentication

```python
from django.contrib.auth import authenticate, login, logout

# Authenticate user
user = authenticate(request, username='johndoe', password='securepassword')

if user is not None:
    # Login user
    login(request, user)
else:
    # Handle invalid login
    pass

# Logout user
logout(request)
```

### Accessing User Profile and Related Data

```python
# Get profile
profile = user.profile

# Get happiness metrics
happiness = profile.happiness

# Get wisdom virtue value
wisdom = happiness.wisdom

# Get all user preferences
preferences = profile.preferences
language = preferences.language_preference

# Get user location
location = profile.location
latitude = location.latitude
longitude = location.longitude
```

### Updating Virtue Metrics

```python
from core.services.user_service import UserService

# Update multiple virtues
updated_happiness = UserService.update_happiness(
    profile,
    wisdom=5,  # Increase wisdom by 5
    courage=3,  # Increase courage by 3
    temperance=-1  # Decrease temperance by 1
)

# Get updated happiness score
new_score = updated_happiness.happiness
```

### Working with Economic Layers

```python
# Check user's economic layer
economic_layer = profile.economic_layer  # 'port', 'laws', or 'republic'

# Get permissions based on economic layer
from core.services.user_service import UserService
permissions = UserService.get_economic_layer_permissions(profile)

# Check specific permissions
can_trade = permissions['can_trade']
can_govern = permissions['can_participate_governance']

# Upgrade economic layer
profile.economic_layer = 'laws'
profile.save()
```

### User Location Updates

```python
# Update user location
location.update_location(
    latitude=37.7749,
    longitude=-122.4194,
    accuracy=10.5,
    device_id='mobile-ios-12345'
)

# Check if user is in a specific zone
is_in_zone = location.current_zone == zone

# Get previously visited zones
previous_zones = location.previous_zones  # List of zone IDs
```

## Handling User Preferences

```python
# Update interface preferences
preferences.interface_settings.update({
    'theme': 'dark',
    'fontSize': 'large'
})
preferences.save()

# Update notification preferences
preferences.notification_preferences['push'] = False
preferences.save()

# Get user language preference
language = preferences.language_preference
```

## Common Edge Cases & Gotchas

### 1. Profile Creation

**Gotcha**: Forgetting to create related models

**Solution**: Always use `UserService.create_user_profile()` which creates all related models

```python
# Wrong - missing related models
profile = PlayerProfile.objects.create(user=user)

# Right - creates all related models
profile = UserService.create_user_profile(user)
```

### 2. Profile Access

**Gotcha**: Accessing profile when it doesn't exist

**Solution**: Use try/except or create if missing

```python
# Robust profile access
try:
    profile = user.profile
except PlayerProfile.DoesNotExist:
    profile = UserService.create_user_profile(user)
```

### 3. Happiness Calculation

**Gotcha**: Manually updating happiness scores without recalculating

**Solution**: Use the service method or call calculate_happiness()

```python
# Wrong - doesn't recalculate
happiness.wisdom += 5
happiness.save()

# Right - handles recalculation
UserService.update_happiness(profile, wisdom=5)

# Also right - explicit recalculation
happiness.wisdom += 5
happiness.calculate_happiness()
happiness.save()
```

### 4. JSON Fields

**Gotcha**: Modifying JSON fields without saving

**Solution**: Always save after modifying JSON fields

```python
# Wrong - changes lost after request
preferences.interface_settings['theme'] = 'dark'

# Right - changes persisted
preferences.interface_settings['theme'] = 'dark'
preferences.save()
```

## Performance Tips

1. **Use select_related for profile queries**
   ```python
   # Efficient - one query
   user_with_profile = User.objects.select_related('profile').get(id=user_id)
   profile = user_with_profile.profile
   
   # Inefficient - two queries
   user = User.objects.get(id=user_id)
   profile = user.profile
   ```

2. **Use prefetch_related for multiple related models**
   ```python
   # Efficient - fewer queries
   user_with_all = User.objects.prefetch_related(
       'profile',
       'profile__happiness',
       'profile__preferences'
   ).get(id=user_id)
   ```

3. **Use update_fields when saving partial updates**
   ```python
   # More efficient - only updates specified fields
   profile.rank = 2
   profile.save(update_fields=['rank'])
   ```

## Database Schema Reference

```
User
├── id (PK)
├── username
├── email
├── password
└── ...standard Django User fields

PlayerProfile
├── id (PK)
├── user_id (FK → User.id)
├── rank
├── experience_points
├── economic_layer
├── avatar
├── title
└── bio

PlayerHappiness
├── id (PK)
├── player_id (FK → PlayerProfile.id)
├── happiness
├── good_score
├── prosperity_score
├── wisdom
├── courage
├── temperance
├── justice
├── strength
├── health
├── beauty
├── endurance
└── virtue_history (JSON)

UserPreferences
├── id (PK)
├── player_id (FK → PlayerProfile.id)
├── interface_settings (JSON)
├── notification_preferences (JSON)
├── privacy_settings (JSON)
├── ai_guide_settings (JSON)
├── language_preference
└── accessibility_options (JSON)

UserLocation
├── id (PK)
├── player_id (FK → PlayerProfile.id)
├── latitude
├── longitude
├── current_zone_id (FK → Zone.id)
├── previous_zones (JSON)
├── accuracy_meters
└── device_id
``` 