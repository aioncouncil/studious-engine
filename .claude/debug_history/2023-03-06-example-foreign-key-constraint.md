# Foreign Key Constraint Error in ArtMastery Creation

**Date**: 2023-03-06  
**Component**: art_system  
**Error Type**: database  

## Error Description

When attempting to create a new `ArtMastery` record, the following error occurred:

```
django.db.utils.IntegrityError: (1452, 'Cannot add or update a child row: a foreign key constraint fails (`atlantis_db`.`art_system_artmastery`, CONSTRAINT `art_system_artmastery_current_part_id_fkey` FOREIGN KEY (`current_part_id`) REFERENCES `art_system_artpart` (`id`))')
```

## Context

This error occurred when implementing the automatic creation of an `ArtMastery` record when a user discovers a new art. The problematic code was in the `ArtService.discover_art` method:

```python
def discover_art(self, user, art_id):
    art = Art.objects.get(pk=art_id)
    
    # Create ArtMastery record
    mastery = ArtMastery.objects.create(
        user=user,
        art=art,
        discovery_date=timezone.now(),
        mastery_level=0,
        current_part=art.parts.first(),  # This line caused the error
    )
    
    return mastery
```

## Diagnosis

The error occurred because we were trying to set `current_part` to the first part of the art without checking if the art actually had any parts. When `art.parts.first()` returned `None` (because the art had no parts yet), it violated the foreign key constraint which cannot accept NULL for `current_part_id`.

## Solution

Modified the code to make `current_part` optional by:

1. Making the field nullable in the model
2. Checking if parts exist before assigning `current_part`

### Model Change

```python
# Before
current_part = models.ForeignKey(
    'ArtPart',
    on_delete=models.CASCADE,
    related_name='current_masteries'
)

# After
current_part = models.ForeignKey(
    'ArtPart',
    on_delete=models.CASCADE,
    related_name='current_masteries',
    null=True,
    blank=True
)
```

### Service Method Change

```python
def discover_art(self, user, art_id):
    art = Art.objects.get(pk=art_id)
    
    # Create ArtMastery record
    mastery = ArtMastery(
        user=user,
        art=art,
        discovery_date=timezone.now(),
        mastery_level=0
    )
    
    # Only set current_part if parts exist
    first_part = art.parts.first()
    if first_part:
        mastery.current_part = first_part
    
    mastery.save()
    return mastery
```

## Tags

`foreign-key`, `null-constraint`, `model-relationship`, `art-system`

## Related Issues

- This pattern should be checked in all similar model relationships
- Added a note in the model documentation to clarify that `current_part` can be null if the art has no parts yet 