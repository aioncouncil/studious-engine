# Art Model Documentation

## Purpose

The Art model represents a creative practice or skill that can be learned, practiced, and mastered by users. It serves as the fundamental collection item in the Atlantis Go "Pokédex" system, allowing users to discover, collect, and master different types of human creative endeavors.

## Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|------------|
| id | UUID | Primary key | Auto-generated |
| name | String | Name of the art | Required, Unique |
| description | Text | Detailed description | Required |
| icon | String | Path to icon image | Required |
| banner_image | String | Path to banner image | Optional |
| difficulty_level | Integer | Difficulty rating (1-10) | Required, Default=1 |
| creation_date | DateTime | When the art was added | Auto (now) |
| taxonomy_id | UUID | Foreign key to ArtTaxonomy | Required |
| parent_arts | Many-to-Many | Arts that are prerequisites | Optional |
| required_virtues | JSONB | Virtues needed to practice | Optional |
| improved_virtues | JSONB | Virtues improved by practice | Required |
| tech_tree_level | Integer | Level in technology tree | Required, Default=1 |
| is_unlocked_default | Boolean | Available without requirements | Default=False |
| rank_required | Integer | User rank required (1-4) | Default=1 |
| economic_layer_required | Enum | PORT, LAWS, or REPUBLIC | Default="PORT" |
| practice_method | Enum | SOLO, PAIR, or GROUP | Required |
| average_mastery_time_days | Integer | Estimated days to master | Optional |

## Relationships

| Relationship | Type | Related Model | Through | Description |
|-------------|------|--------------|---------|-------------|
| taxonomy | Many-to-One | ArtTaxonomy | taxonomy_id | Categorization of the art |
| parent_arts | Many-to-Many | Art | self-referential | Arts that are prerequisites for this art |
| child_arts | Many-to-Many | Art | parent_arts (reverse) | Arts that have this art as a prerequisite |
| parts | One-to-Many | ArtPart | art_id (reverse) | Components or aspects of the art that must be practiced |
| stages | One-to-Many | ArtStage | art_id (reverse) | Different learning stages for the art |
| masteries | One-to-Many | ArtMastery | art_id (reverse) | User mastery records for this art |
| required_for_tech_nodes | Many-to-Many | TechTree | required_arts | Tech tree nodes requiring this art |
| unlocked_by_tech_nodes | Many-to-Many | TechTree | unlocks_arts | Tech tree nodes that unlock this art |

## Patterns

### Creation Pattern

```python
# Create a new Art
art = Art.objects.create(
    name="Poetry",
    description="The art of rhythmical composition for exciting pleasure by imagination or emotion",
    icon="icons/poetry.png",
    banner_image="banners/poetry.jpg",
    difficulty_level=3,
    taxonomy=literature_taxonomy,  # ArtTaxonomy instance
    required_virtues={"wisdom": 20, "temperance": 15},
    improved_virtues={"wisdom": 5, "temperance": 3, "beauty": 4},
    tech_tree_level=2,
    is_unlocked_default=False,
    rank_required=1,
    economic_layer_required="PORT",
    practice_method="SOLO",
    average_mastery_time_days=90
)

# Add parent arts (prerequisites)
art.parent_arts.add(language_art)  # Assuming language_art is another Art instance
```

### Query Patterns

```python
# Get all arts in a specific taxonomy
literature_arts = Art.objects.filter(taxonomy=literature_taxonomy)

# Get all arts available to a user of rank 1
beginner_arts = Art.objects.filter(rank_required=1)

# Get all arts unlocked by default
default_arts = Art.objects.filter(is_unlocked_default=True)

# Get arts that are prerequisites for a specific art
prerequisites = art.parent_arts.all()

# Get arts that have this art as a prerequisite
dependent_arts = art.child_arts.all()

# Get all parts for an art
parts = art.parts.all()

# Get all learning stages for an art
stages = art.stages.all()

# Get all users who are practicing this art
practicing_users = User.objects.filter(art_masteries__art=art)
```

### Deletion Pattern

```python
# When deleting an art, all related objects will be affected:
# - ArtParts will be deleted (CASCADE)
# - ArtStages will be deleted (CASCADE)
# - ArtMastery records will be deleted (CASCADE)
# - Many-to-many relationships will be removed

# Safe deletion with checks
def safe_delete_art(art_id):
    try:
        art = Art.objects.get(pk=art_id)
        
        # Check if this art is a prerequisite for other arts
        if art.child_arts.exists():
            return False, "Cannot delete: this art is a prerequisite for other arts"
            
        # Check if this art is required for tech tree nodes
        if art.required_for_tech_nodes.exists():
            return False, "Cannot delete: this art is required for tech tree progression"
            
        # If safe, delete the art
        art.delete()
        return True, "Art deleted successfully"
    except Art.DoesNotExist:
        return False, "Art not found"
```

## Interfaces

### Main Properties

```python
class Art(models.Model):
    # Fields as defined above
    
    @property
    def parts_count(self):
        """Get the number of parts in this art."""
        return self.parts.count()
    
    @property
    def mastering_users_count(self):
        """Get the number of users currently mastering this art."""
        return self.masteries.count()
    
    @property
    def completed_users_count(self):
        """Get the number of users who have fully mastered this art."""
        return self.masteries.filter(mastery_level__gte=95).count()
        
    @property
    def average_mastery_level(self):
        """Calculate the average mastery level across all users."""
        return self.masteries.aggregate(Avg('mastery_level'))['mastery_level__avg'] or 0
    
    @property
    def full_taxonomy_path(self):
        """Get the full taxonomy path for this art."""
        if not self.taxonomy:
            return ""
        return self.taxonomy.full_path
```

### Public Methods

```python
def is_unlocked_for_user(self, user):
    """Check if this art is unlocked for a specific user."""
    # Check if unlocked by default
    if self.is_unlocked_default:
        return True
        
    # Check user rank requirement
    if user.profile.rank < self.rank_required:
        return False
        
    # Check economic layer requirement
    if self.economic_layer_hierarchy[self.economic_layer_required] > \
       self.economic_layer_hierarchy[user.profile.economic_layer]:
        return False
    
    # Check if prerequisites are mastered
    for parent_art in self.parent_arts.all():
        try:
            mastery = ArtMastery.objects.get(user=user, art=parent_art)
            if mastery.mastery_level < 50:  # Require at least 50% mastery
                return False
        except ArtMastery.DoesNotExist:
            return False
    
    # Check if unlocked via tech tree
    for node in self.unlocked_by_tech_nodes.all():
        progress = UserTechTreeProgress.objects.filter(
            user=user, 
            tech_tree=node,
            unlocked_date__isnull=False
        ).exists()
        if progress:
            return True
    
    return False

def get_unlock_requirements(self, user):
    """Get what the user needs to unlock this art."""
    requirements = {
        "rank": {"required": self.rank_required, "current": user.profile.rank},
        "economic_layer": {
            "required": self.economic_layer_required,
            "current": user.profile.economic_layer
        },
        "parent_arts": [],
        "tech_tree_nodes": []
    }
    
    # Check parent arts
    for parent_art in self.parent_arts.all():
        try:
            mastery = ArtMastery.objects.get(user=user, art=parent_art)
            requirements["parent_arts"].append({
                "art": parent_art.name,
                "required_mastery": 50,
                "current_mastery": mastery.mastery_level,
                "satisfied": mastery.mastery_level >= 50
            })
        except ArtMastery.DoesNotExist:
            requirements["parent_arts"].append({
                "art": parent_art.name,
                "required_mastery": 50,
                "current_mastery": 0,
                "satisfied": False
            })
    
    # Check tech tree nodes
    for node in self.unlocked_by_tech_nodes.all():
        try:
            progress = UserTechTreeProgress.objects.get(user=user, tech_tree=node)
            requirements["tech_tree_nodes"].append({
                "node": node.name,
                "progress_percentage": progress.progress_percentage,
                "satisfied": progress.unlocked_date is not None
            })
        except UserTechTreeProgress.DoesNotExist:
            requirements["tech_tree_nodes"].append({
                "node": node.name,
                "progress_percentage": 0,
                "satisfied": False
            })
    
    return requirements
```

## Invariants

1. **Name Uniqueness**: Each Art must have a unique name
2. **Valid Taxonomy**: Each Art must belong to a valid ArtTaxonomy
3. **Practice Method Format**: practice_method must be one of "SOLO", "PAIR", or "GROUP"
4. **Economic Layer Format**: economic_layer_required must be one of "PORT", "LAWS", or "REPUBLIC"
5. **Required Virtues Structure**: required_virtues must be a valid JSON object with virtue names as keys and integer values
6. **Improved Virtues Structure**: improved_virtues must be a valid JSON object with virtue names as keys and integer values
7. **No Circular Dependencies**: An Art cannot have itself as a parent (directly or indirectly)
8. **Valid Tech Tree Level**: tech_tree_level must be a positive integer
9. **Valid Difficulty**: difficulty_level must be between 1 and 10

## Error States

| Error | Cause | Resolution |
|-------|-------|------------|
| IntegrityError: duplicate key value violates unique constraint | Attempting to create an Art with a name that already exists | Choose a different name for the art |
| ValueError: practice_method must be one of SOLO, PAIR, GROUP | Invalid practice_method value | Use only allowed values |
| ValueError: economic_layer_required must be one of PORT, LAWS, REPUBLIC | Invalid economic_layer_required value | Use only allowed values |
| ValidationError: Invalid JSON format for required_virtues | Malformed JSON in required_virtues field | Ensure proper JSON format with virtue names as keys and integer values |
| CircularDependencyError | Adding a parent art that creates a circular dependency | Restructure dependencies to avoid circles |
| ForeignKeyViolation | Deleting a taxonomy that arts are using | Reassign arts to a different taxonomy before deletion | 