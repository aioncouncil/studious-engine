# Django Model Relationship Patterns

This document provides canonical implementation patterns for common Django model relationships used in the Atlantis Go project.

## One-to-One Relationships

### User to Profile 

**Pattern**: One User has exactly one Profile

```python
# In core/models.py
class PlayerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    # Other fields...
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
```

**Usage**:
```python
# Access profile from user
user_profile = user.profile

# Access user from profile
user = profile.user
```

**Uncertainty Handling**:
```python
# Handle case where profile might not exist
try:
    profile = user.profile
except PlayerProfile.DoesNotExist:
    profile = PlayerProfile.objects.create(user=user)
```

## One-to-Many Relationships

### Art to ArtParts

**Pattern**: One Art has many ArtParts

```python
# In art_system/models.py
class Art(models.Model):
    name = models.CharField(max_length=100)
    # Other fields...
    
    def __str__(self):
        return self.name

class ArtPart(models.Model):
    art = models.ForeignKey(
        Art,
        on_delete=models.CASCADE,
        related_name="parts"
    )
    name = models.CharField(max_length=100)
    order_index = models.IntegerField(default=0)
    # Other fields...
    
    class Meta:
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.art.name} - {self.name}"
```

**Usage**:
```python
# Get all parts for an art
parts = art.parts.all()

# Get the first part
first_part = art.parts.first()

# Get art from a part
art = part.art
```

**Uncertainty Handling**:
```python
# Check if parts exist before accessing
if art.parts.exists():
    first_part = art.parts.first()
else:
    # Handle case with no parts
    pass
```

## Many-to-Many Relationships

### Art to ParentArts

**Pattern**: Arts can have multiple parent arts (prerequisites)

```python
# In art_system/models.py
class Art(models.Model):
    name = models.CharField(max_length=100)
    parent_arts = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='child_arts',
        blank=True
    )
    # Other fields...
```

**Usage**:
```python
# Add a parent art
art.parent_arts.add(parent_art)

# Get all parent arts
prerequisites = art.parent_arts.all()

# Get all arts that have this art as a prerequisite
dependent_arts = art.child_arts.all()
```

**Uncertainty Handling**:
```python
# Check if any parents exist
has_prerequisites = art.parent_arts.exists()

# Safe iteration
for parent in art.parent_arts.all():
    try:
        # Do something with parent
        pass
    except Exception as e:
        # Handle error
        pass
```

## Many-to-Many Through Relationships

### User to Zone via ZoneMembership

**Pattern**: Users belong to zones with additional membership metadata

```python
# In zone_system/models.py
class Zone(models.Model):
    name = models.CharField(max_length=100)
    # Other fields...
    
    @property
    def member_count(self):
        return self.memberships.count()

class ZoneMembership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="zone_memberships"
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    joined_date = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, default="member")
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ["user", "zone"]
```

**Usage**:
```python
# Get all zones a user is a member of
zones = [membership.zone for membership in user.zone_memberships.all()]

# Get all users in a zone
users = [membership.user for membership in zone.memberships.all()]

# Get membership details
membership = ZoneMembership.objects.get(user=user, zone=zone)
user_role = membership.role
```

**Uncertainty Handling**:
```python
# Check if user is a member of a zone
is_member = ZoneMembership.objects.filter(user=user, zone=zone).exists()

# Try to get membership, create if it doesn't exist
try:
    membership = ZoneMembership.objects.get(user=user, zone=zone)
except ZoneMembership.DoesNotExist:
    membership = ZoneMembership.objects.create(user=user, zone=zone)
```

## Self-Referential Hierarchical Relationships

### ArtTaxonomy Hierarchy

**Pattern**: Categories can have parent categories, creating a tree structure

```python
# In art_system/models.py
class ArtTaxonomy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    level = models.IntegerField(default=0)
    path = models.CharField(max_length=255, blank=True)
    
    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
            self.path = f"{self.parent.path}/{self.id}" if self.parent.path else str(self.id)
        else:
            self.level = 0
            self.path = str(self.id) if self.id else ""
        super().save(*args, **kwargs)
        
        # Update path for all children if needed
        if 'path' in kwargs.get('update_fields', ['path']):
            for child in self.children.all():
                child.save(update_fields=['path'])
```

**Usage**:
```python
# Get parent category
parent = category.parent

# Get all child categories
children = category.children.all()

# Get all descendants (recursive)
def get_all_descendants(category):
    descendants = list(category.children.all())
    for child in category.children.all():
        descendants.extend(get_all_descendants(child))
    return descendants
```

**Uncertainty Handling**:
```python
# Safe parent access
parent_name = category.parent.name if category.parent else "Root Category"

# Check if it's a root category
is_root = category.parent is None

# Check if it's a leaf category
is_leaf = not category.children.exists()
```

## Polymorphic Relationships

### Resource Inventory

**Pattern**: Generic relationship to different resource types

```python
# In economic_system/models.py
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Resource(models.Model):
    name = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    # Other common fields...
    
    class Meta:
        abstract = True

class MaterialResource(Resource):
    weight = models.FloatField(default=0)
    volume = models.FloatField(default=0)
    # Material-specific fields...

class KnowledgeResource(Resource):
    complexity = models.IntegerField(default=1)
    subject_area = models.CharField(max_length=100)
    # Knowledge-specific fields...

class ResourceInventory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resources"
    )
    
    # Generic foreign key to any resource type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    resource = GenericForeignKey('content_type', 'object_id')
    
    quantity = models.IntegerField(default=1)
    acquired_date = models.DateTimeField(auto_now_add=True)
```

**Usage**:
```python
# Add a resource to inventory
material = MaterialResource.objects.create(name="Wood", resource_type="material")
inventory_item = ResourceInventory.objects.create(
    user=user,
    content_object=material,
    quantity=5
)

# Get all resources of a specific type
from django.contrib.contenttypes.models import ContentType

material_type = ContentType.objects.get_for_model(MaterialResource)
materials = ResourceInventory.objects.filter(
    user=user,
    content_type=material_type
)
```

**Uncertainty Handling**:
```python
# Safe access to polymorphic fields
try:
    resource_name = inventory_item.resource.name
except AttributeError:
    # Handle case where resource might be deleted
    resource_name = "Unknown Resource"
```

## Context Preservation Patterns

### Signals for Related Updates

**Pattern**: Update related objects when a model changes

```python
# In art_system/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Art, ArtMastery

@receiver(post_save, sender=Art)
def update_art_masteries(sender, instance, created, **kwargs):
    """Update masteries when an art is updated."""
    if not created:
        # Get all masteries for this art
        masteries = ArtMastery.objects.filter(art=instance)
        
        # Update something in all masteries
        for mastery in masteries:
            if mastery.current_part is None and instance.parts.exists():
                mastery.current_part = instance.parts.first()
                mastery.save(update_fields=['current_part'])
```

### Transaction Atomic for Multi-step Operations

**Pattern**: Ensure all related changes succeed or fail together

```python
from django.db import transaction

@transaction.atomic
def discover_art_with_initial_practice(user, art_id):
    """Discover an art and create initial practice record atomically."""
    art = Art.objects.get(pk=art_id)
    
    # Create mastery record
    mastery = ArtMastery.objects.create(
        user=user,
        art=art,
        discovery_date=timezone.now()
    )
    
    # Set initial part if available
    if art.parts.exists():
        first_part = art.parts.first()
        mastery.current_part = first_part
        mastery.save(update_fields=['current_part'])
        
        # Create practice record
        PracticeSession.objects.create(
            mastery=mastery,
            part=first_part,
            duration_minutes=5,
            notes="Initial discovery practice"
        )
    
    return mastery
```

## Reliability Metrics

### Adding Model Metrics Tracking

**Pattern**: Track timing and performance metrics for model operations

```python
import time
from functools import wraps
from django.db import connection

def db_metrics_decorator(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        initial_queries = len(connection.queries)
        
        result = method(self, *args, **kwargs)
        
        end_time = time.time()
        final_queries = len(connection.queries)
        
        print(f"Method {method.__name__}:")
        print(f"  Execution time: {end_time - start_time:.4f} seconds")
        print(f"  Database queries: {final_queries - initial_queries}")
        
        return result
    return wrapper

class ArtService:
    @db_metrics_decorator
    def get_art_with_parts(self, art_id):
        """Get an art with all its parts, optimized for performance."""
        return Art.objects.prefetch_related('parts').get(pk=art_id)
``` 