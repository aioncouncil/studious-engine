# Q&A: Art System Model Relationships

## Question: How should I structure the relationship between Art and ArtParts?

**Context**: When implementing the Art and ArtParts models, I need to decide on the best relationship structure for efficient queries and maintenance.

**Answer**: The relationship between Art and ArtParts should be a one-to-many relationship, where one Art can have multiple ArtParts, but each ArtPart belongs to exactly one Art.

```python
# In art_system/models.py

class Art(models.Model):
    name = models.CharField(max_length=100)
    # ... other fields
    
    def __str__(self):
        return self.name
    
    @property
    def parts_count(self):
        return self.parts.count()

class ArtPart(models.Model):
    art = models.ForeignKey(
        Art,
        on_delete=models.CASCADE,
        related_name="parts"
    )
    name = models.CharField(max_length=100)
    order_index = models.IntegerField(default=0)
    # ... other fields
    
    class Meta:
        ordering = ['order_index']
        
    def __str__(self):
        return f"{self.art.name} - {self.name}"
```

Using this structure:

1. You can easily query all parts for an art: `art.parts.all()`
2. You can access the art from a part: `part.art`
3. The `related_name="parts"` makes the relationship intuitive
4. Using `order_index` allows for ordered parts
5. The `on_delete=models.CASCADE` ensures that when an art is deleted, all its parts are deleted too

When creating ArtParts, make sure to always associate them with an Art:

```python
art = Art.objects.get(id=1)
part = ArtPart.objects.create(
    art=art,
    name="Foundations",
    order_index=1
)
```

## Question: How should the ArtMastery model track progress through ArtParts?

**Context**: I need to implement a way to track a user's progress through different ArtParts as they master an Art.

**Answer**: The ArtMastery model should maintain both a reference to the current ArtPart being practiced and a record of completed parts. This can be implemented using a foreign key relationship to the current part and a JSON field for tracking completed parts with metadata.

```python
class ArtMastery(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="art_masteries"
    )
    art = models.ForeignKey(
        Art, 
        on_delete=models.CASCADE,
        related_name="masteries"
    )
    discovery_date = models.DateTimeField(auto_now_add=True)
    mastery_level = models.IntegerField(default=0)
    last_practiced = models.DateTimeField(null=True, blank=True)
    practice_streak = models.IntegerField(default=0)
    
    # Current part being practiced
    current_part = models.ForeignKey(
        ArtPart,
        on_delete=models.SET_NULL,
        related_name="current_masteries",
        null=True,
        blank=True
    )
    
    # Record of completed parts with completion dates and notes
    completed_parts = models.JSONField(default=list, blank=True)
    
    def advance_to_next_part(self):
        """Advance to the next part if available."""
        if not self.current_part:
            # Get first part if no current part
            next_part = self.art.parts.first()
        else:
            # Mark current part as completed
            completion_record = {
                "part_id": str(self.current_part.id),
                "part_name": self.current_part.name,
                "completed_date": timezone.now().isoformat(),
                "practice_count": self.get_practice_count(self.current_part)
            }
            
            if not self.completed_parts:
                self.completed_parts = []
                
            self.completed_parts.append(completion_record)
            
            # Get next part based on order_index
            next_part = self.art.parts.filter(
                order_index__gt=self.current_part.order_index
            ).first()
        
        # Update current part
        self.current_part = next_part
        self.save()
        
        return next_part
    
    def get_practice_count(self, part):
        """Get number of practice sessions for a specific part."""
        return PracticeSession.objects.filter(
            mastery=self,
            part=part
        ).count()
    
    def is_part_completed(self, part_id):
        """Check if a specific part has been completed."""
        if not self.completed_parts:
            return False
            
        return any(record.get('part_id') == str(part_id) for record in self.completed_parts)
    
    def get_progress_percentage(self):
        """Calculate overall progress percentage based on completed parts."""
        total_parts = self.art.parts.count()
        if total_parts == 0:
            return 100  # If no parts, consider complete
            
        completed_count = len(self.completed_parts) if self.completed_parts else 0
        return int((completed_count / total_parts) * 100)
```

This approach provides:

1. A clear way to track which part the user is currently working on
2. Historical data about completed parts, including when they were completed
3. Methods to advance to the next part and check progress
4. The ability to calculate overall progress as a percentage

When implementing the UI, you can use these methods to show the user their progress and guide them to the next part to practice.

## Question: How should the Art model relate to the TechTree for unlocking progression?

**Context**: I need to implement the relationship between Arts and the TechTree to manage unlocking new arts as users progress.

**Answer**: The relationship between Art and TechTree should be implemented using a many-to-many relationship in both directions - Arts that are required to unlock a tech tree node, and Arts that get unlocked by a tech tree node.

```python
class TechTree(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1)
    
    # Arts required to unlock this tech tree node
    required_arts = models.ManyToManyField(
        Art,
        related_name="required_for_tech_nodes",
        blank=True
    )
    
    # Arts unlocked by this tech tree node
    unlocks_arts = models.ManyToManyField(
        Art,
        related_name="unlocked_by_tech_nodes",
        blank=True
    )
    
    # Other requirements
    required_resources = models.JSONField(default=dict, blank=True)
    required_zone_level = models.IntegerField(default=0)
    zone_type_filter = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name
    
    def is_unlocked_for_user(self, user):
        """Check if this tech tree node is unlocked for a user."""
        # If no required arts, it's automatically unlocked
        if not self.required_arts.exists():
            return True
            
        # Get all user's masteries
        user_masteries = ArtMastery.objects.filter(user=user)
        user_mastered_art_ids = [
            mastery.art_id for mastery in user_masteries 
            if mastery.mastery_level >= 50  # Consider "mastered" at 50% or higher
        ]
        
        # Check if all required arts are mastered
        required_art_ids = self.required_arts.values_list('id', flat=True)
        missing_arts = set(required_art_ids) - set(user_mastered_art_ids)
        
        return len(missing_arts) == 0
    
    def get_missing_requirements(self, user):
        """Get missing requirements for a user to unlock this node."""
        missing = {
            "arts": [],
            "resources": {},
            "zone_level": False,
            "zone_type": False
        }
        
        # Check required arts
        user_masteries = ArtMastery.objects.filter(user=user)
        user_mastered_art_ids = [
            mastery.art_id for mastery in user_masteries 
            if mastery.mastery_level >= 50
        ]
        
        for art in self.required_arts.all():
            if art.id not in user_mastered_art_ids:
                missing["arts"].append({
                    "id": str(art.id),
                    "name": art.name
                })
        
        # Additional requirements would be checked here
        
        return missing
```

Then, create a model to track user progress through the tech tree:

```python
class UserTechTreeProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tech_tree_progress"
    )
    tech_tree = models.ForeignKey(
        TechTree,
        on_delete=models.CASCADE,
        related_name="user_progress"
    )
    unlocked_date = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)
    missing_requirements = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ["user", "tech_tree"]
    
    def update_progress(self):
        """Update progress and check if newly unlocked."""
        # Get missing requirements
        missing = self.tech_tree.get_missing_requirements(self.user)
        self.missing_requirements = missing
        
        # Calculate progress percentage
        if not missing["arts"] and self.unlocked_date is None:
            # Just unlocked!
            self.unlocked_date = timezone.now()
            self.progress_percentage = 100
        elif missing["arts"]:
            # Calculate partial progress
            total_required = self.tech_tree.required_arts.count()
            if total_required > 0:
                missing_count = len(missing["arts"])
                self.progress_percentage = int(((total_required - missing_count) / total_required) * 100)
            
        self.save()
        return self.progress_percentage == 100
```

This implementation provides:

1. A clear way to define which arts unlock and are unlocked by tech tree nodes
2. Methods to check if a tech tree node is unlocked for a user
3. Methods to check what requirements are missing for a user
4. A tracking system for user progress through the tech tree

To use this system to check if an art is unlocked for a user:

```python
def is_art_unlocked_for_user(art, user):
    """Check if an art is unlocked for a user."""
    # Arts that are unlocked by default
    if art.is_unlocked_default:
        return True
        
    # Check if unlocked via tech tree
    unlocking_nodes = art.unlocked_by_tech_nodes.all()
    for node in unlocking_nodes:
        progress = UserTechTreeProgress.objects.get_or_create(
            user=user,
            tech_tree=node
        )[0]
        
        if progress.unlocked_date is not None:
            return True
            
    return False
```

This approach creates a flexible tech tree system that can handle complex unlock requirements. 