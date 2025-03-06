from django.db import models
import uuid

class PhysicsSimulation(models.Model):
    """
    Represents a physics simulation that can be used for educational purposes,
    visualizations, or game mechanics within the Atlantis Go system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    
    # Simulation type
    SIMULATION_TYPE_CHOICES = [
        ('particle', 'Particle System'),
        ('rigid_body', 'Rigid Body Dynamics'),
        ('fluid', 'Fluid Dynamics'),
        ('cloth', 'Cloth Simulation'),
        ('soft_body', 'Soft Body Dynamics'),
        ('gravity', 'Gravitational Simulation'),
        ('electromagnetic', 'Electromagnetic Simulation'),
        ('custom', 'Custom Physics')
    ]
    type = models.CharField(max_length=20, choices=SIMULATION_TYPE_CHOICES)
    
    # Physics components
    entities = models.JSONField(default=dict, help_text="Objects with physics properties")
    forces = models.JSONField(default=dict)
    constraints = models.JSONField(default=dict)
    
    # Simulation parameters
    iteration_rate = models.FloatField(default=60.0, help_text="Iterations per second")
    
    # Visual effects
    visual_effects = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def initialize_entities(self):
        """Initialize the entities JSON structure with default values."""
        if not self.entities:
            self.entities = {
                'objects': [],
                'properties': {
                    'gravity': {'x': 0, 'y': -9.8, 'z': 0},
                    'air_resistance': 0.01,
                    'bounds': {'min_x': -100, 'max_x': 100, 'min_y': -100, 'max_y': 100, 'min_z': -100, 'max_z': 100}
                }
            }
            self.save()
    
    def add_entity(self, entity_data):
        """Add a new entity to the simulation."""
        if not self.entities or 'objects' not in self.entities:
            self.initialize_entities()
            
        entity_id = str(uuid.uuid4())
        entity_data['id'] = entity_id
        
        # Ensure required properties exist
        if 'position' not in entity_data:
            entity_data['position'] = {'x': 0, 'y': 0, 'z': 0}
        if 'velocity' not in entity_data:
            entity_data['velocity'] = {'x': 0, 'y': 0, 'z': 0}
        if 'mass' not in entity_data:
            entity_data['mass'] = 1.0
            
        # Add to entities
        entities = self.entities.copy()
        entities['objects'].append(entity_data)
        self.entities = entities
        self.save()
        
        return entity_id
    
    def add_force(self, force_data):
        """Add a new force to the simulation."""
        if not self.forces:
            self.forces = {'forces': []}
            
        force_id = str(uuid.uuid4())
        force_data['id'] = force_id
        
        # Add to forces
        forces = self.forces.copy()
        forces['forces'].append(force_data)
        self.forces = forces
        self.save()
        
        return force_id
    
    def add_constraint(self, constraint_data):
        """Add a new constraint to the simulation."""
        if not self.constraints:
            self.constraints = {'constraints': []}
            
        constraint_id = str(uuid.uuid4())
        constraint_data['id'] = constraint_id
        
        # Add to constraints
        constraints = self.constraints.copy()
        constraints['constraints'].append(constraint_data)
        self.constraints = constraints
        self.save()
        
        return constraint_id
    
    class Meta:
        ordering = ['-created_at']


class PhysicsInteraction(models.Model):
    """
    Represents a user's interaction with a physics simulation.
    This can be used to track educational progress or game mechanics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    simulation = models.ForeignKey(PhysicsSimulation, on_delete=models.CASCADE, related_name="interactions")
    user = models.ForeignKey('core.PlayerProfile', on_delete=models.CASCADE, related_name="physics_interactions")
    
    # Interaction data
    interaction_data = models.JSONField(default=dict)
    
    # Learning outcomes
    learning_objectives = models.JSONField(default=list, blank=True)
    objectives_achieved = models.JSONField(default=list, blank=True)
    
    # Session information
    session_duration = models.IntegerField(default=0, help_text="Duration in seconds")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user}'s interaction with {self.simulation}"
    
    def end_session(self):
        """End the interaction session and calculate duration."""
        from django.utils import timezone
        
        if not self.ended_at:
            self.ended_at = timezone.now()
            # Calculate duration in seconds
            duration = (self.ended_at - self.started_at).total_seconds()
            self.session_duration = int(duration)
            self.save()
    
    class Meta:
        ordering = ['-started_at']
