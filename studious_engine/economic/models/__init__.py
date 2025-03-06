from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey

# [REF:45a8e9b3-c1d2-e3f4-a5b6-c7d8e9f0a1b2:ECONOMIC_SYSTEM]
# [CLAUDE:CHECK_PATTERN:economic_transaction_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the economic_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class Resource(models.Model):
    """
    Base resource model that defines resources in the economic system.
    This includes materials, currencies, knowledge, and other tradable assets.
    """
    RESOURCE_TYPE_CHOICES = [
        ('material', 'Material Resource'),
        ('currency', 'Currency'),
        ('knowledge', 'Knowledge Asset'),
        ('social', 'Social Capital'),
        ('service', 'Service'),
        ('energy', 'Energy'),
        ('time', 'Time'),
    ]
    
    RARITY_CHOICES = [
        (1, 'Common'),
        (2, 'Uncommon'),
        (3, 'Rare'),
        (4, 'Epic'),
        (5, 'Legendary'),
    ]
    
    ORIGIN_TYPE_CHOICES = [
        ('natural', 'Natural'),
        ('manufactured', 'Manufactured'),
        ('intellectual', 'Intellectual'),
        ('digital', 'Digital'),
        ('social', 'Social'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic information
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=50, unique=True, help_text="Unique code for this resource")
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    
    # Classification
    rarity = models.IntegerField(choices=RARITY_CHOICES, default=1)
    origin_type = models.CharField(max_length=15, choices=ORIGIN_TYPE_CHOICES)
    tags = models.JSONField(default=list, blank=True)
    
    # Economic properties
    base_value = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    current_market_value = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    is_tradable = models.BooleanField(default=True)
    is_depleting = models.BooleanField(default=False, help_text="Whether this resource depletes with use")
    is_renewable = models.BooleanField(default=False, help_text="Whether this resource regenerates over time")
    regeneration_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    
    # System relationships
    related_sector = models.ForeignKey('zones.Sector', on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name="related_resources")
    dependent_resources = models.ManyToManyField('self', blank=True, symmetrical=False,
                                              related_name="required_for")
    
    # Asset references
    icon = models.CharField(max_length=255, blank=True, help_text="Path or reference to resource icon")
    image = models.CharField(max_length=255, blank=True, help_text="Path or reference to resource image")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name_plural = "Resources"
        ordering = ['name']
    
    @property
    def market_status(self):
        """Return the current market status of the resource."""
        if self.current_market_value > self.base_value * 1.5:
            return "high_demand"
        elif self.current_market_value < self.base_value * 0.75:
            return "over_supplied"
        else:
            return "stable"
    
    def recalculate_market_value(self):
        """
        Recalculate the market value based on economic factors.
        This would typically be called by a market simulation service.
        """
        # Placeholder for market simulation logic
        # This would be implemented by the market mechanics service
        pass


class ResourceInventory(models.Model):
    """
    Tracks resource ownership for players, zones, or other entities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Owner information (using generic foreign keys for flexibility)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.UUIDField()
    
    # Resources
    resources = models.JSONField(default=dict, help_text="Dictionary of resource_code: quantity pairs")
    
    # Maximum capacity
    max_capacity = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    
    # Status tracking
    last_updated = models.DateTimeField(auto_now=True)
    last_transaction_id = models.UUIDField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Resource Inventories"
        unique_together = ['content_type', 'object_id']
    
    def __str__(self):
        return f"Inventory for {self.content_type.model} ({self.object_id})"
    
    @property
    def total_resources(self):
        """Return the total number of resources in the inventory."""
        return sum(self.resources.values())
    
    @property
    def capacity_used_percentage(self):
        """Return the percentage of capacity used."""
        if self.max_capacity == 0:
            return 100
        return min(100, (self.total_resources / self.max_capacity) * 100)
    
    def has_resource(self, resource_code, quantity=1):
        """Check if the inventory has sufficient quantity of a resource."""
        return self.resources.get(resource_code, 0) >= quantity
    
    def add_resource(self, resource_code, quantity):
        """Add a resource to the inventory."""
        if quantity <= 0:
            return False
            
        current_total = self.total_resources
        if current_total + quantity > self.max_capacity:
            return False
            
        current_amount = self.resources.get(resource_code, 0)
        self.resources[resource_code] = current_amount + quantity
        self.save()
        return True
    
    def remove_resource(self, resource_code, quantity):
        """Remove a resource from the inventory."""
        if quantity <= 0:
            return False
            
        current_amount = self.resources.get(resource_code, 0)
        if current_amount < quantity:
            return False
            
        self.resources[resource_code] = current_amount - quantity
        
        # Clean up empty entries
        if self.resources[resource_code] == 0:
            del self.resources[resource_code]
            
        self.save()
        return True
    
    def transfer_resource(self, destination_inventory, resource_code, quantity):
        """Transfer a resource to another inventory."""
        if self.remove_resource(resource_code, quantity):
            if destination_inventory.add_resource(resource_code, quantity):
                return True
            else:
                # Rollback if destination couldn't accept
                self.add_resource(resource_code, quantity)
                return False
        return False


class EconomicTransaction(models.Model):
    """
    Records all economic transactions in the system.
    Used for auditing, analytics, and economic simulation.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('transfer', 'Resource Transfer'),
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('production', 'Resource Production'),
        ('consumption', 'Resource Consumption'),
        ('taxation', 'Taxation'),
        ('reward', 'Reward'),
        ('penalty', 'Penalty'),
        ('investment', 'Investment'),
        ('dividend', 'Dividend'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Transaction details
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPE_CHOICES)
    resources = models.JSONField(help_text="Dictionary of resource_code: quantity pairs")
    value = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Status tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Participants (using generic foreign keys for flexibility)
    # Source
    source_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE,
                                          related_name='source_transactions')
    source_object_id = models.UUIDField()
    source = GenericForeignKey('source_content_type', 'source_object_id')
    
    # Destination
    destination_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, 
                                              related_name='destination_transactions')
    destination_object_id = models.UUIDField()
    destination = GenericForeignKey('destination_content_type', 'destination_object_id')
    
    # Optional reference to inventories
    source_inventory = models.ForeignKey(ResourceInventory, on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name="outgoing_transactions")
    destination_inventory = models.ForeignKey(ResourceInventory, on_delete=models.SET_NULL, 
                                           null=True, blank=True, related_name="incoming_transactions")
    
    # Context
    context_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL,
                                          null=True, blank=True, related_name='context_transactions')
    context_object_id = models.UUIDField(null=True, blank=True)
    context = GenericForeignKey('context_content_type', 'context_object_id')
    context_description = models.CharField(max_length=255, blank=True)
    
    # Facilitation
    facilitated_by_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL,
                                                 null=True, blank=True, related_name='facilitated_transactions')
    facilitated_by_object_id = models.UUIDField(null=True, blank=True)
    facilitated_by = GenericForeignKey('facilitated_by_content_type', 'facilitated_by_object_id')
    
    # Tax
    tax_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tax_recipient_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL,
                                                null=True, blank=True, related_name='tax_recipient_transactions')
    tax_recipient_object_id = models.UUIDField(null=True, blank=True)
    tax_recipient = GenericForeignKey('tax_recipient_content_type', 'tax_recipient_object_id')
    
    # Timing
    initiated_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # System tracking
    transaction_hash = models.CharField(max_length=64, blank=True, help_text="Hash for transaction verification")
    related_transaction = models.ForeignKey('self', on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name="child_transactions")
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Economic Transactions"
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['source_content_type', 'source_object_id']),
            models.Index(fields=['destination_content_type', 'destination_object_id']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['initiated_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.id}: {self.get_transaction_type_display()} ({self.get_status_display()})"
    
    def mark_processing(self):
        """Mark the transaction as processing."""
        if self.status == 'pending':
            self.status = 'processing'
            self.processed_at = timezone.now()
            self.save()
            return True
        return False
    
    def mark_completed(self):
        """Mark the transaction as completed."""
        if self.status in ['pending', 'processing']:
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            return True
        return False
    
    def mark_failed(self, reason=None):
        """Mark the transaction as failed."""
        if self.status in ['pending', 'processing']:
            self.status = 'failed'
            if reason:
                self.notes += f"\nFailure reason: {reason}"
            self.save()
            return True
        return False
    
    def generate_hash(self):
        """Generate a transaction hash for verification."""
        import hashlib
        
        # Create a string with transaction details
        data = f"{self.id}{self.transaction_type}{self.value}{self.source_object_id}{self.destination_object_id}{self.initiated_at}"
        data += str(self.resources)
        
        # Generate hash
        hash_obj = hashlib.sha256(data.encode())
        self.transaction_hash = hash_obj.hexdigest()
        self.save()


class WealthClass(models.Model):
    """
    Defines wealth classes in the economic system.
    Used for economic stratification and class-based mechanics.
    """
    WEALTH_LEVEL_CHOICES = [
        (1, 'Subsistence'),
        (2, 'Working Class'),
        (3, 'Middle Class'),
        (4, 'Upper Middle Class'),
        (5, 'Affluent'),
        (6, 'Wealthy'),
        (7, 'Elite'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic information
    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.IntegerField(choices=WEALTH_LEVEL_CHOICES)
    
    # Requirements and benefits
    wealth_threshold = models.IntegerField(validators=[MinValueValidator(0)], 
                                         help_text="Minimum wealth required to be in this class")
    asset_requirements = models.JSONField(default=dict, blank=True, 
                                       help_text="Resources required to qualify for this class")
    
    # Benefits
    resource_access = models.JSONField(default=list, blank=True, 
                                    help_text="List of resource codes accessible to this class")
    zone_access = models.JSONField(default=list, blank=True, 
                                help_text="List of zone IDs accessible to this class")
    influence_multiplier = models.FloatField(default=1.0, validators=[MinValueValidator(0.1)])
    tax_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Visual representation
    icon = models.CharField(max_length=255, blank=True)
    color_code = models.CharField(max_length=7, default="#FFFFFF")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Wealth Classes"
        ordering = ['level']
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"
    
    @classmethod
    def determine_class(cls, wealth_value, assets=None):
        """
        Determine the wealth class for a given wealth value and assets.
        Returns the highest matching WealthClass instance.
        """
        if assets is None:
            assets = {}
            
        # Get all active wealth classes, ordered by level descending (highest first)
        wealth_classes = cls.objects.filter(is_active=True).order_by('-level')
        
        for wealth_class in wealth_classes:
            # Check if wealth value meets threshold
            if wealth_value < wealth_class.wealth_threshold:
                continue
                
            # Check asset requirements if any
            if wealth_class.asset_requirements:
                meets_asset_requirements = True
                
                for resource_code, required_amount in wealth_class.asset_requirements.items():
                    if assets.get(resource_code, 0) < required_amount:
                        meets_asset_requirements = False
                        break
                        
                if not meets_asset_requirements:
                    continue
                    
            # If we reach here, all requirements are met
            return wealth_class
            
        # If no matching class, return the lowest level class
        return cls.objects.filter(is_active=True).order_by('level').first()


class CommonResource(models.Model):
    """
    Represents shared or common-pool resources.
    These are resources managed collectively by multiple entities.
    """
    GOVERNANCE_TYPE_CHOICES = [
        ('democratic', 'Democratic'),
        ('hierarchical', 'Hierarchical'),
        ('meritocratic', 'Meritocratic'),
        ('rotational', 'Rotational'),
        ('autonomous', 'Autonomous'),
    ]
    
    ACCESS_LEVEL_CHOICES = [
        (1, 'Open Access'),
        (2, 'Common-Pool'),
        (3, 'Member Access'),
        (4, 'Restricted'),
        (5, 'Highly Restricted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic information
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Resource details
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="common_resources")
    current_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_capacity = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Location
    location_description = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    zone = models.ForeignKey('zones.Zone', on_delete=models.SET_NULL, 
                          null=True, blank=True, related_name="common_resources")
    
    # Access and governance
    access_level = models.IntegerField(choices=ACCESS_LEVEL_CHOICES, default=2)
    governance_type = models.CharField(max_length=15, choices=GOVERNANCE_TYPE_CHOICES)
    administrators = models.JSONField(default=list, blank=True, 
                                   help_text="List of entity IDs that administer this resource")
    
    # Usage and sustainability
    sustainable_extraction_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    current_extraction_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    is_renewable = models.BooleanField(default=True)
    regeneration_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    
    # Health and status
    health_level = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    crisis_threshold = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Common Resources"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.resource.name})"
    
    @property
    def is_in_crisis(self):
        """Check if the resource is in crisis (health below threshold)."""
        return self.health_level <= self.crisis_threshold
    
    @property
    def percentage_available(self):
        """Return the percentage of the resource available."""
        if self.max_capacity == 0:
            return 0
        return min(100, (self.current_amount / self.max_capacity) * 100)
    
    def extract_resource(self, amount):
        """Extract a specified amount of the resource."""
        if amount <= 0:
            return False
            
        if amount > self.current_amount:
            return False
            
        self.current_amount -= amount
        
        # Update health level based on extraction vs. sustainable rate
        if self.current_extraction_rate > self.sustainable_extraction_rate:
            health_impact = ((self.current_extraction_rate / self.sustainable_extraction_rate) - 1) * 10
            self.health_level = max(0, self.health_level - health_impact)
            
        self.save()
        return True
    
    def regenerate(self):
        """Regenerate the resource based on its regeneration rate."""
        if not self.is_renewable or self.regeneration_rate <= 0:
            return 0
            
        regeneration_amount = int(self.max_capacity * (self.regeneration_rate / 100))
        regeneration_amount = min(regeneration_amount, self.max_capacity - self.current_amount)
        
        if regeneration_amount > 0:
            self.current_amount += regeneration_amount
            
            # Improve health if below 100%
            if self.health_level < 100:
                health_improvement = min(5, 100 - self.health_level)
                self.health_level += health_improvement
                
            self.save()
            
        return regeneration_amount


class Project(models.Model):
    """
    Represents collective endeavors for resource generation or community goals.
    Similar to zone activities but more focused on economic outcomes.
    """
    PROJECT_TYPE_CHOICES = [
        ('resource_generation', 'Resource Generation'),
        ('infrastructure', 'Infrastructure'),
        ('research', 'Research and Development'),
        ('education', 'Education'),
        ('conservation', 'Conservation'),
        ('community', 'Community Development'),
        ('market', 'Market Development'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('planning', 'Planning Phase'),
        ('fundraising', 'Fundraising'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic information
    name = models.CharField(max_length=100)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    goals = models.JSONField(default=list, blank=True)
    
    # Location
    zone = models.ForeignKey('zones.Zone', on_delete=models.SET_NULL, 
                          null=True, blank=True, related_name="projects")
    
    # Status and progress
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='proposed')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Resources
    resource_requirements = models.JSONField(default=dict, blank=True, 
                                          help_text="Dictionary of resource_code: quantity pairs needed")
    current_resources = models.JSONField(default=dict, blank=True, 
                                      help_text="Dictionary of resource_code: quantity pairs committed")
    resource_outputs = models.JSONField(default=dict, blank=True, 
                                     help_text="Dictionary of resource_code: quantity pairs produced")
    
    # Participation
    initiator = models.ForeignKey('core.PlayerProfile', on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name="initiated_projects")
    min_participants = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_participants = models.IntegerField(default=10, validators=[MinValueValidator(1)])
    participants = models.ManyToManyField('core.PlayerProfile', blank=True, 
                                       through='ProjectParticipation', related_name="projects")
    
    # Economics
    total_budget = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    current_funding = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    roi_estimate = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)],
                                  help_text="Estimated return on investment multiplier")
    
    # Timing
    proposed_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    target_completion = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Projects"
        ordering = ['-proposed_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"
    
    @property
    def funding_percentage(self):
        """Return the percentage of funding received."""
        if self.total_budget == 0:
            return 100
        return min(100, (self.current_funding / self.total_budget) * 100)
    
    @property
    def resource_fulfillment_percentage(self):
        """Return the percentage of required resources collected."""
        if not self.resource_requirements:
            return 100
            
        total_required = sum(self.resource_requirements.values())
        total_collected = sum(self.current_resources.values())
        
        if total_required == 0:
            return 100
            
        return min(100, (total_collected / total_required) * 100)
    
    def start_project(self):
        """Start the project if conditions are met."""
        if self.status != 'proposed' and self.status != 'planning' and self.status != 'fundraising':
            return False
            
        # Check if we have minimum participants
        if self.participants.count() < self.min_participants:
            return False
            
        # Check if we have necessary resources
        if self.resource_fulfillment_percentage < 100:
            return False
            
        # Check if we have necessary funding
        if self.funding_percentage < 100:
            return False
            
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
        return True
    
    def complete_project(self):
        """Mark the project as completed."""
        if self.status != 'in_progress':
            return False
            
        self.status = 'completed'
        self.progress = 100
        self.completed_at = timezone.now()
        self.save()
        
        # Logic for distributing outputs would go here
        
        return True


class ProjectParticipation(models.Model):
    """
    Tracks a player's participation in a project.
    Records contributions, roles, and rewards.
    """
    ROLE_CHOICES = [
        ('investor', 'Investor'),
        ('worker', 'Worker'),
        ('manager', 'Manager'),
        ('consultant', 'Consultant'),
        ('stakeholder', 'Stakeholder'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_participations")
    player = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="project_participations")
    
    # Role and status
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='worker')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Contributions
    resource_contributions = models.JSONField(default=dict, blank=True)
    funding_contribution = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    work_contribution = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Rewards
    resource_rewards = models.JSONField(default=dict, blank=True)
    currency_reward = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    ownership_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['project', 'player']]
        verbose_name_plural = "Project Participations"
    
    def __str__(self):
        return f"{self.player} as {self.get_role_display()} in {self.project}"
    
    def leave_project(self):
        """Record when a player leaves a project."""
        if not self.is_active:
            return False
            
        self.is_active = False
        self.left_at = timezone.now()
        self.save()
        return True
    
    def add_resource_contribution(self, resource_code, amount):
        """Record a resource contribution to the project."""
        if amount <= 0:
            return False
            
        current = self.resource_contributions.get(resource_code, 0)
        self.resource_contributions[resource_code] = current + amount
        
        # Update project's current resources
        project_current = self.project.current_resources.get(resource_code, 0)
        self.project.current_resources[resource_code] = project_current + amount
        
        self.save()
        self.project.save()
        return True
