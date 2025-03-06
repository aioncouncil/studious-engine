from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import random
from zones.models import Zone, Sector
from experiences.models import Experience

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class Command(BaseCommand):
    help = 'Set up test data for zones and experiences with coordinates'

    def handle(self, *args, **options):
        # Base coordinates (approximate location of UMKC)
        base_lat = 39.0345
        base_lng = -94.5764
        
        # Setting up zones with coordinates
        self.stdout.write(self.style.NOTICE('Setting up zone coordinates...'))
        
        zones_updated = 0
        try:
            # Update the first 5 zones with different coordinates around the base
            zones = Zone.objects.all()[:5]
            
            for i, zone in enumerate(zones):
                # Create a different offset for each zone
                lat_offset = random.uniform(-0.005, 0.005)
                lng_offset = random.uniform(-0.005, 0.005)
                
                # Update the zone's city coordinates
                zone.city_latitude = base_lat + lat_offset
                zone.city_longitude = base_lng + lng_offset
                zone.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f'Updated Zone {zone.id}: {zone.zone_type} at {zone.city_latitude}, {zone.city_longitude}'
                ))
                zones_updated += 1
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating zones: {str(e)}'))
        
        # Setting up experiences with coordinates
        self.stdout.write(self.style.NOTICE('Setting up experience coordinates...'))
        
        experiences_updated = 0
        experiences_created = 0
        
        try:
            # Update existing experiences with coordinates
            experiences = Experience.objects.filter(latitude__isnull=True)[:5]
            
            for i, exp in enumerate(experiences):
                # Create a different offset for each experience
                lat_offset = random.uniform(-0.003, 0.003)
                lng_offset = random.uniform(-0.003, 0.003)
                
                # Update the experience coordinates
                exp.latitude = base_lat + lat_offset
                exp.longitude = base_lng + lng_offset
                exp.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f'Updated Experience {exp.id}: {exp.name} at {exp.latitude}, {exp.longitude}'
                ))
                experiences_updated += 1
            
            # Create some new experiences with coordinates if there are fewer than 5 experiences
            if Experience.objects.count() < 5:
                # Get a random zone to associate with the new experiences
                zones = Zone.objects.all()
                zone = zones[0] if zones.exists() else None
                
                # Names for the new experiences
                experience_names = [
                    'Mathematics Challenge',
                    'Physics Exploration',
                    'History Research Quest',
                    'Literature Analysis',
                    'Computer Science Project'
                ]
                
                # Types for the new experiences
                types = ['quest', 'challenge', 'collaboration', 'innovation', 'reflection']
                
                for i in range(min(5, 5 - Experience.objects.count())):
                    # Create a different offset for each experience
                    lat_offset = random.uniform(-0.002, 0.002)
                    lng_offset = random.uniform(-0.002, 0.002)
                    
                    # Create a new experience
                    exp = Experience.objects.create(
                        name=experience_names[i],
                        description=f'Description for {experience_names[i]}',
                        experience_type=types[i % len(types)],
                        matrix_position='soul_out',
                        art_type='production',
                        good_type='present_future',
                        latitude=base_lat + lat_offset,
                        longitude=base_lng + lng_offset,
                        difficulty=random.randint(3, 8),
                        duration_minutes=random.choice([15, 30, 45, 60]),
                        happiness_reward=random.randint(10, 30),
                        experience_reward=random.randint(50, 100),
                        definition=f'Definition of {experience_names[i]}',
                        end=f'Purpose of {experience_names[i]}',
                        parts=f'Components of {experience_names[i]}',
                        matter=f'Materials for {experience_names[i]}',
                        instrument=f'Tools for {experience_names[i]}',
                        is_active=True,
                        minimum_rank=random.randint(1, 3)
                    )
                    
                    # Associate with a zone if available
                    if zone:
                        exp.associated_zones.add(zone)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Created Experience {exp.id}: {exp.name} at {exp.latitude}, {exp.longitude}'
                    ))
                    experiences_created += 1
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up experiences: {str(e)}'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'Setup complete! Updated {zones_updated} zones, updated {experiences_updated} experiences, created {experiences_created} experiences.'
        )) 