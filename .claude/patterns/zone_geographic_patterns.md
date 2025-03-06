# Zone Geographic Patterns

## Overview

The Zone System in Atlantis Go provides a geographical framework for user experiences and activities. Zones represent specific physical or virtual areas with distinct purposes, attributes, and relationships to the Matrix Flow. This pattern document explains how to implement and utilize geographic zones across the system.

## Zone Types

Atlantis Go defines several primary zone types that serve different purposes:

1. **Education Zones**: Areas focused on learning and wisdom development (Soul Out)
2. **Exercise Zones**: Areas focused on physical activity and strength building (Body Out)
3. **Reflection Zones**: Areas focused on contemplation and balance (Soul In)
4. **Arts Zones**: Areas focused on creative expression and aesthetics (Body In)
5. **Market Zones**: Areas focused on economic activities and exchanges
6. **Community Zones**: Areas focused on social interaction and community building
7. **Wilderness Zones**: Natural areas with discovery opportunities
8. **Custom Zones**: User-defined areas for personal or group activities

## Common Patterns

### Pattern 1: Zone Definition and Geometry

**Purpose**: Define geographic zones with proper geometry and properties.

**Implementation**:

```python
class Zone(models.Model):
    """Geographic zone model with attributes and boundaries."""
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Zone type and classification
    zone_type = models.CharField(
        max_length=50,
        choices=[
            ('EDUCATION', 'Education Zone'),
            ('EXERCISE', 'Exercise Zone'),
            ('REFLECTION', 'Reflection Zone'),
            ('ARTS', 'Arts Zone'),
            ('MARKET', 'Market Zone'),
            ('COMMUNITY', 'Community Zone'),
            ('WILDERNESS', 'Wilderness Zone'),
            ('CUSTOM', 'Custom Zone'),
        ]
    )
    
    # Matrix quadrant association
    matrix_quadrant = models.CharField(
        max_length=2,
        choices=[
            ('SO', 'Soul Out'),
            ('BO', 'Body Out'),
            ('SI', 'Soul In'),
            ('BI', 'Body In'),
        ],
        default='SO'
    )
    
    # Geographic data
    boundary = models.PolygonField(
        help_text="Geographic boundary of the zone"
    )
    center_point = models.PointField(
        help_text="Center point of the zone"
    )
    
    # Zone hierarchy
    parent_zone = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subzones'
    )
    
    # Access control
    public = models.BooleanField(
        default=True,
        help_text="Whether the zone is accessible to all users"
    )
    access_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Required user level to access this zone (1-10)"
    )
    
    # Discoverability
    discoverable = models.BooleanField(
        default=True,
        help_text="Whether the zone can be discovered by users"
    )
    discovery_radius_meters = models.IntegerField(
        default=100,
        help_text="How close a user must be to discover the zone"
    )
    
    # Capacity and scaling
    capacity = models.IntegerField(
        default=0,  # 0 means unlimited
        help_text="Maximum number of users in the zone (0 for unlimited)"
    )
    
    # Metadata and stats
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # GIS index
    objects = models.Manager()
    geo_objects = models.GeoManager()
    
    class Meta:
        indexes = [
            models.Index(fields=['zone_type']),
            models.Index(fields=['matrix_quadrant']),
            # Note: Spatial indices are created in a migration
        ]
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Override save to ensure center_point is calculated."""
        if self.boundary and not self.center_point:
            self.center_point = self.boundary.centroid
        super().save(*args, **kwargs)
    
    @property
    def area_square_meters(self):
        """Calculate the area of the zone in square meters."""
        from django.contrib.gis.db.models.functions import Area
        from django.db.models import F
        
        # Query to get area
        result = Zone.geo_objects.filter(id=self.id).annotate(
            area=Area('boundary')
        ).values('area').first()
        
        return result['area'] if result else 0
    
    @property
    def subzone_count(self):
        """Count the number of immediate subzones."""
        return self.subzones.count()
    
    def contains_point(self, point):
        """Check if a point is contained within this zone."""
        return self.boundary.contains(point)
    
    def get_all_subzones(self, include_self=False):
        """
        Recursively get all subzones beneath this zone.
        Returns a QuerySet of Zones.
        """
        # Start with immediate subzones
        subzone_ids = list(self.subzones.values_list('id', flat=True))
        
        # Recursively add all child subzones
        for subzone in self.subzones.all():
            child_ids = subzone.get_all_subzones().values_list('id', flat=True)
            subzone_ids.extend(child_ids)
            
        # Optionally include self
        if include_self:
            subzone_ids.append(self.id)
            
        return Zone.objects.filter(id__in=subzone_ids)
    
    def get_nearby_zones(self, max_distance_meters=1000):
        """
        Get zones that are near this zone.
        Returns zones ordered by distance.
        """
        from django.contrib.gis.db.models.functions import Distance
        from django.contrib.gis.measure import D
        
        return Zone.geo_objects.exclude(
            id=self.id
        ).filter(
            center_point__distance_lte=(self.center_point, D(m=max_distance_meters))
        ).annotate(
            distance=Distance('center_point', self.center_point)
        ).order_by('distance')
    
    def get_experiences(self):
        """Get experiences available in this zone."""
        from experience.models import Experience
        
        return Experience.objects.filter(
            location_required=True,
            location_point__intersects=self.boundary
        )
```

**Key Points**:
- Zones can have complex polygon geometries
- Hierarchy allows for nested zones (zones within zones)
- Spatial operations utilize GeoDjango's GIS capabilities
- Matrix quadrant association connects zones to the flow system

**When to Use**:
- When defining physical or virtual spaces
- For location-based discovery and activities
- When implementing the geographic layer of the application

**When to Avoid**:
- For ephemeral or non-spatial groupings
- When spatial context isn't relevant

### Pattern 2: Zone Discovery and User Location

**Purpose**: Track user location and discover zones based on proximity.

**Implementation**:

```python
class UserLocation(models.Model):
    """Model for tracking user's current and historical locations."""
    
    # Relationships
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='current_location'
    )
    
    # Current location
    point = models.PointField(
        help_text="User's current geographic location"
    )
    accuracy_meters = models.FloatField(
        default=10.0,
        help_text="Accuracy of the location in meters"
    )
    
    # Zone association
    current_zone = models.ForeignKey(
        'Zone', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users'
    )
    
    # Tracking
    last_updated = models.DateTimeField(auto_now=True)
    location_history = models.JSONField(
        default=list,
        help_text="Historical record of locations [{'timestamp': '...', 'lat': '...', 'lng': '...', 'zone_id': '...'}]"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['last_updated']),
            # Spatial index created in migration
        ]
    
    def __str__(self):
        return f"Location for {self.user.username}"
    
    def update_location(self, latitude, longitude, accuracy=None):
        """
        Update the user's location and check for zone changes.
        Returns dict with discovered zones and other relevant info.
        """
        from django.contrib.gis.geos import Point
        from django.utils import timezone
        
        # Create point from coordinates
        new_point = Point(longitude, latitude, srid=4326)
        
        # Check if significantly different from current location
        significant_change = True
        if self.point:
            # Calculate distance in meters
            distance = self.point.distance(new_point) * 111000  # Approx conversion to meters
            # If less than 10m movement, may not be significant
            significant_change = distance > 10
        
        # If no significant change, just update timestamp and return
        if not significant_change:
            self.last_updated = timezone.now()
            self.save(update_fields=['last_updated'])
            return {
                'location_updated': False,
                'message': 'Location unchanged'
            }
        
        # Update the location
        self.point = new_point
        if accuracy is not None:
            self.accuracy_meters = accuracy
            
        # Record in history
        history_entry = {
            'timestamp': timezone.now().isoformat(),
            'lat': latitude,
            'lng': longitude,
            'accuracy': self.accuracy_meters
        }
        
        # Find containing zone
        result = self._update_current_zone()
        history_entry['zone_id'] = str(self.current_zone.id) if self.current_zone else None
        
        # Append to history (limited to last 100 entries)
        history = self.location_history.copy()
        history.append(history_entry)
        if len(history) > 100:
            history = history[-100:]
        self.location_history = history
        
        # Save changes
        self.save()
        
        return result
    
    def _update_current_zone(self):
        """
        Find the zone containing the current point and update.
        Returns dict with result information.
        """
        from zone.models import Zone
        
        # Find zones containing the point, prioritizing smallest area
        containing_zones = Zone.geo_objects.filter(
            boundary__contains=self.point
        ).annotate(
            area=models.functions.Area('boundary')
        ).order_by('area')
        
        # Check for discovered zones
        from zone.models import UserZoneDiscovery
        user_discovered = set(UserZoneDiscovery.objects.filter(
            user=self.user
        ).values_list('zone_id', flat=True))
        
        newly_discovered = []
        
        # Find the most specific zone (smallest containing zone)
        new_current_zone = None
        if containing_zones.exists():
            new_current_zone = containing_zones.first()
            
            # Check for all containing zones that might be discovered
            for zone in containing_zones:
                if zone.discoverable and zone.id not in user_discovered:
                    # Check if within discovery radius of center
                    distance_to_center = zone.center_point.distance(self.point) * 111000  # meters
                    if distance_to_center <= zone.discovery_radius_meters:
                        # Discover the zone
                        UserZoneDiscovery.objects.create(
                            user=self.user,
                            zone=zone
                        )
                        newly_discovered.append({
                            'id': str(zone.id),
                            'name': zone.name,
                            'type': zone.zone_type
                        })
                        
        # Check for zone change
        zone_changed = (
            (self.current_zone is None and new_current_zone is not None) or
            (self.current_zone is not None and new_current_zone is None) or
            (self.current_zone is not None and new_current_zone is not None and 
             self.current_zone.id != new_current_zone.id)
        )
        
        old_zone = self.current_zone
        self.current_zone = new_current_zone
        
        return {
            'location_updated': True,
            'zone_changed': zone_changed,
            'old_zone': {
                'id': str(old_zone.id),
                'name': old_zone.name
            } if old_zone else None,
            'new_zone': {
                'id': str(new_current_zone.id),
                'name': new_current_zone.name
            } if new_current_zone else None,
            'newly_discovered_zones': newly_discovered
        }


class UserZoneDiscovery(models.Model):
    """Tracks which zones a user has discovered."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='discovered_zones'
    )
    zone = models.ForeignKey(
        'Zone',
        on_delete=models.CASCADE,
        related_name='discovered_by'
    )
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'zone')
        ordering = ['-discovered_at']
    
    def __str__(self):
        return f"{self.user.username} discovered {self.zone.name}"
```

**Key Points**:
- User location is tracked with history
- Zone discovery is based on proximity to zone center
- Hierarchical zone containment is respected
- Historical location data is preserved with space constraints

**When to Use**:
- For location-aware applications
- When implementing discovery mechanics
- For proximity-based experiences and activities

**When to Avoid**:
- When precise location isn't needed
- For privacy-sensitive contexts without proper consent

### Pattern 3: Zone-Based Experience Filtering

**Purpose**: Filter and recommend experiences based on zone location.

**Implementation**:

```python
class ZoneExperienceService:
    """Service for finding and filtering experiences based on zones."""
    
    @staticmethod
    def get_zone_experiences(zone, user=None, limit=10):
        """
        Get experiences available in a specific zone,
        optionally filtered for a specific user.
        """
        from experience.models import Experience
        from django.db.models import Q
        
        # Base query - experiences in this zone
        query = Q(
            location_required=True,
            location_point__intersects=zone.boundary
        )
        
        # If a specific matrix quadrant is dominant for this zone
        if zone.matrix_quadrant:
            # Boost experiences that match the zone's quadrant
            # But don't exclude others entirely
            pass  # This would be handled in the ordering
            
        # Get base queryset
        experiences = Experience.objects.filter(query)
        
        # Filter for user if provided
        if user:
            # Exclude experiences user has completed
            completed_ids = user.experiences.filter(
                status__in=['COMPLETED', 'MASTERED']
            ).values_list('experience_id', flat=True)
            
            experiences = experiences.exclude(id__in=completed_ids)
            
            # Filter for access level
            experiences = experiences.filter(min_level__lte=user.level)
            
            # Check virtue requirements
            # This is complex and would require filtering in Python
            # or a more sophisticated query
            
        # Limit results
        experiences = experiences[:limit]
        
        return experiences
    
    @staticmethod
    def get_experiences_by_proximity(user, radius_meters=1000, limit=10):
        """
        Get experiences near the user's current location.
        Returns experiences ordered by distance.
        """
        from experience.models import Experience
        from django.contrib.gis.db.models.functions import Distance
        from django.contrib.gis.measure import D
        
        # Get user's location
        try:
            location = user.current_location.point
        except AttributeError:
            return []
            
        # Get user's completed experiences to exclude
        completed_ids = user.experiences.filter(
            status__in=['COMPLETED', 'MASTERED']
        ).values_list('experience_id', flat=True)
        
        # Find nearby experiences
        experiences = Experience.objects.filter(
            location_required=True,
            location_point__distance_lte=(location, D(m=radius_meters))
        ).exclude(
            id__in=completed_ids
        ).annotate(
            distance=Distance('location_point', location)
        ).order_by('distance')[:limit]
        
        return experiences
    
    @staticmethod
    def get_zone_quest_line(starting_zone, quest_length=5):
        """
        Create a quest line through connected zones.
        Returns a list of zones that form a path.
        """
        from zone.models import Zone
        from django.contrib.gis.db.models.functions import Distance
        
        result = [starting_zone]
        current_zone = starting_zone
        
        # Simple greedy algorithm to find a path
        # Could be improved with more sophisticated pathfinding
        while len(result) < quest_length:
            # Find adjacent zones not already in the path
            adjacent = Zone.geo_objects.filter(
                boundary__touches=current_zone.boundary
            ).exclude(
                id__in=[z.id for z in result]
            ).annotate(
                distance=Distance('center_point', current_zone.center_point)
            ).order_by('distance')
            
            # If no more adjacent zones, try nearby non-adjacent zones
            if not adjacent.exists():
                nearby = Zone.geo_objects.filter(
                    center_point__distance_lte=(current_zone.center_point, D(m=1000))
                ).exclude(
                    id__in=[z.id for z in result]
                ).annotate(
                    distance=Distance('center_point', current_zone.center_point)
                ).order_by('distance')
                
                if not nearby.exists():
                    # No more zones to add to the path
                    break
                    
                # Add the closest nearby zone
                next_zone = nearby.first()
            else:
                # Add the closest adjacent zone
                next_zone = adjacent.first()
                
            result.append(next_zone)
            current_zone = next_zone
            
        return result
        
    @staticmethod
    def get_balanced_zone_distribution(area_polygon, count=4):
        """
        Generate a balanced distribution of zones in a geographic area,
        with one zone for each matrix quadrant.
        """
        from django.contrib.gis.geos import Point
        import random
        from zone.models import Zone
        
        # Generate random points within the polygon
        points = []
        min_x, min_y, max_x, max_y = area_polygon.extent
        
        while len(points) < count:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            point = Point(x, y)
            
            if point.within(area_polygon):
                points.append(point)
        
        # Create one zone for each quadrant
        quadrants = ['SO', 'BO', 'SI', 'BI']
        zone_types = {
            'SO': 'EDUCATION',
            'BO': 'EXERCISE',
            'SI': 'REFLECTION',
            'BI': 'ARTS'
        }
        
        # Size of zone (approximately 100m radius)
        from django.contrib.gis.geos import Polygon, LinearRing
        
        zones = []
        for i, point in enumerate(points[:4]):
            quadrant = quadrants[i]
            
            # Create a simple circular-ish polygon around the point
            # Note: This is an approximation and not a true circle
            # For a proper circle, would use buffer on the point
            coords = []
            for angle in range(0, 360, 10):
                # Convert angle to radians
                radians = math.radians(angle)
                # Calculate point on circle (100m radius)
                # Note: This is a rough approximation, needs proper projection
                dx = math.cos(radians) * 0.001  # Approx 100m in degrees
                dy = math.sin(radians) * 0.001
                coords.append((point.x + dx, point.y + dy))
            
            # Close the polygon
            coords.append(coords[0])
            
            # Create polygon
            poly = Polygon(coords)
            
            zone = Zone.objects.create(
                name=f"{quadrant} Zone",
                description=f"A zone focused on {quadrant} development",
                zone_type=zone_types[quadrant],
                matrix_quadrant=quadrant,
                boundary=poly,
                center_point=point
            )
            zones.append(zone)
        
        return zones
```

**Key Points**:
- Experiences can be filtered based on zone location
- Proximity queries use GIS distance calculations
- Zone quest lines create paths through connected zones
- Balanced zone distribution ensures matrix quadrant coverage

**When to Use**:
- For creating location-based activities
- When implementing geographic exploration features
- For balanced geographic design

**When to Avoid**:
- When location isn't a primary factor for experiences
- For purely virtual contexts without geographic relevance

## Uncertainty Handling

When implementing Zone Geographic patterns, several forms of uncertainty may arise:

1. **Location Accuracy Issues**:
   - When GPS or location data has poor accuracy
   - Solution: Use accuracy radius for containment checks

2. **Boundary Overlap Conflicts**:
   - When multiple zones cover the same area
   - Solution: Prioritize based on zone specificity (area size)

3. **Temporal Boundary Changes**:
   - When zone boundaries change over time 
   - Solution: Track boundary history and version zones

Example handling code:

```python
def handle_location_uncertainty(point, accuracy_meters):
    """
    Handle uncertainty in location data by finding all
    potentially containing zones based on accuracy.
    """
    from django.contrib.gis.db.models.functions import Distance
    from django.contrib.gis.measure import D
    from zone.models import Zone
    
    # Find zones that might contain the point, considering accuracy
    potential_zones = Zone.geo_objects.filter(
        boundary__distance_lte=(point, D(m=accuracy_meters))
    ).annotate(
        distance=Distance('center_point', point)
    )
    
    # Classify zones by likelihood
    definitely_containing = []
    possibly_containing = []
    
    for zone in potential_zones:
        if zone.boundary.contains(point):
            definitely_containing.append(zone)
        else:
            possibly_containing.append(zone)
            
    return {
        'definitely_containing': definitely_containing,
        'possibly_containing': possibly_containing,
        'accuracy_meters': accuracy_meters
    }
```

## Error Recovery

Common errors in Zone Geographic implementation include:

1. **Invalid Geometries**:
   - Problem: Non-closed polygons or self-intersecting boundaries
   - Resolution: Geometry validation and repair functions

2. **Orphaned Subzones**:
   - Problem: Subzones with deleted parent zones
   - Resolution: Cascade handling or reparenting routines

3. **Zone Containment Errors**:
   - Problem: Users in zones they shouldn't have access to
   - Resolution: Periodic location validation

Example error recovery code:

```python
def repair_zone_geometry(zone):
    """Fix common issues with zone geometries."""
    from django.contrib.gis.geos import Polygon, LinearRing
    
    boundary = zone.boundary
    
    # Check if polygon is valid
    if not boundary.valid:
        # Attempt to fix with buffer technique
        # This can resolve many common topology issues
        fixed_boundary = boundary.buffer(0)
        
        if fixed_boundary and fixed_boundary.valid:
            zone.boundary = fixed_boundary
            zone.center_point = fixed_boundary.centroid
            zone.save()
            return {
                'status': 'fixed',
                'message': 'Zone geometry repaired successfully'
            }
        else:
            return {
                'status': 'error',
                'message': 'Could not repair zone geometry'
            }
    
    # Check if center point is inside boundary
    if not boundary.contains(zone.center_point):
        # Update center point to be the centroid
        zone.center_point = boundary.centroid
        zone.save(update_fields=['center_point'])
        return {
            'status': 'fixed', 
            'message': 'Center point updated to be within boundary'
        }
        
    return {'status': 'ok', 'message': 'Zone geometry is valid'}
```

## Performance Considerations

Zone Geographic implementations should consider:

1. **Spatial Indices**:
   - Ensure proper spatial indexing for all geometric fields
   - Consider using different SRIDs based on query patterns

2. **Query Optimization**:
   - Use bounding box queries before precise geometry checks
   - Limit frequent queries to center points rather than full boundaries

3. **Geometry Simplification**:
   - Simplify complex polygons for faster querying
   - Use different resolution versions for different zoom levels

Example performance optimization:

```python
class ZoneQueryOptimization:
    """Optimizations for zone queries."""
    
    @staticmethod
    def simplified_zones_for_map(bounds, zoom_level):
        """
        Get zones for map display with appropriate simplification.
        Simplifies geometries based on zoom level for performance.
        """
        from django.contrib.gis.db.models.functions import Simplify
        from django.contrib.gis.geos import Polygon
        from zone.models import Zone
        
        # Create polygon from bounds
        bbox = Polygon.from_bbox(bounds)
        
        # Determine tolerance based on zoom level
        # Higher zoom = less simplification
        simplification_tolerance = 0.001 / (zoom_level / 10)
        
        # Get zones intersecting the bounds
        zones = Zone.geo_objects.filter(
            boundary__intersects=bbox
        ).annotate(
            simplified_boundary=Simplify(
                'boundary', 
                tolerance=simplification_tolerance,
                preserve_topology=True
            )
        ).values(
            'id', 
            'name', 
            'zone_type', 
            'matrix_quadrant',
            'simplified_boundary'
        )
        
        return zones
    
    @staticmethod
    def contains_point_cached(zone_id, point):
        """
        Check if a zone contains a point, with caching.
        Much faster than repeated DB queries for the same zone.
        """
        from django.core.cache import cache
        from zone.models import Zone
        
        # Check if geometry is in cache
        cache_key = f"zone_geometry:{zone_id}"
        boundary = cache.get(cache_key)
        
        if boundary is None:
            # Get from database
            zone = Zone.objects.get(id=zone_id)
            boundary = zone.boundary
            
            # Cache for 1 hour
            cache.set(cache_key, boundary, 60*60)
            
        # Do containment check
        return boundary.contains(point)
```

## Related Patterns

- [Matrix Flow](matrix_flow.md)
- [Experience Progression](experience_progression.md)
- [User Location Tracking](user_location_tracking.md) 