"""
UserService provides business logic for user-related operations in the EudaimoniaGo system.
This service helps maintain separation between business logic and models/views.
"""

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
import json
import random

from core.models import PlayerProfile, PlayerHappiness, UserPreferences, UserLocation

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()


class UserService:
    """Service class for user-related operations."""
    
    @staticmethod
    def create_user_profile(user, **kwargs):
        """
        Create a complete user profile with all related models.
        
        Args:
            user: The Django User instance to create a profile for
            **kwargs: Additional attributes to set on the profile
            
        Returns:
            PlayerProfile: The created or updated profile instance
        """
        with transaction.atomic():
            # Create or update profile
            profile, _ = PlayerProfile.objects.get_or_create(user=user)
            
            # Update profile with provided data
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.save()
            
            # Create happiness metrics
            happiness, _ = PlayerHappiness.objects.get_or_create(player=profile)
            happiness.save()
            
            # Create user preferences
            preferences, _ = UserPreferences.objects.get_or_create(player=profile)
            preferences.save()
            
            # Create location tracking
            location, _ = UserLocation.objects.get_or_create(player=profile)
            location.save()
            
            return profile
    
    @staticmethod
    def update_happiness(player_profile, **virtue_updates):
        """
        Update a player's virtue metrics and track history.
        
        Args:
            player_profile: The PlayerProfile instance to update
            **virtue_updates: Dict of virtue names and their delta values
            
        Returns:
            PlayerHappiness: The updated happiness instance
        """
        happiness = player_profile.happiness
        
        # Record current values in history
        history_entry = {
            'timestamp': timezone.now().isoformat(),
            'values': {
                'wisdom': happiness.wisdom,
                'courage': happiness.courage,
                'temperance': happiness.temperance,
                'justice': happiness.justice,
                'strength': happiness.strength,
                'health': happiness.health,
                'beauty': happiness.beauty,
                'endurance': happiness.endurance,
            },
            'overall': {
                'happiness': happiness.happiness,
                'good_score': happiness.good_score,
                'prosperity_score': happiness.prosperity_score
            }
        }
        
        # Update virtues
        for virtue, value in virtue_updates.items():
            if hasattr(happiness, virtue):
                current_value = getattr(happiness, virtue)
                # For small increments, ensure we don't exceed bounds
                new_value = min(max(current_value + value, 0), 100)
                setattr(happiness, virtue, new_value)
        
        # Add to history
        if not isinstance(happiness.virtue_history, list):
            # Initialize as list if empty or not a list
            history = []
        else:
            history = happiness.virtue_history.copy()
            
        history.append(history_entry)
        
        # Keep only the last 100 entries
        happiness.virtue_history = history[-100:]
        
        # Save changes
        happiness.save()
        return happiness
    
    @staticmethod
    def update_location(player_profile, latitude, longitude, accuracy=None, device_id=None):
        """
        Update a player's location and track zone changes.
        
        Args:
            player_profile: The PlayerProfile instance to update
            latitude: The user's latitude coordinate
            longitude: The user's longitude coordinate
            accuracy: Optional accuracy in meters
            device_id: Optional device identifier
            
        Returns:
            UserLocation: The updated location instance
        """
        # Get or create location record
        location, created = UserLocation.objects.get_or_create(player=player_profile)
        
        # Update location data
        location.latitude = latitude
        location.longitude = longitude
        
        if accuracy is not None:
            location.accuracy_meters = accuracy
        if device_id is not None:
            location.device_id = device_id
            
        # Store current location for backward compatibility
        player_profile.latitude = latitude
        player_profile.longitude = longitude
        player_profile.last_location_update = timezone.now()
        player_profile.save(update_fields=['latitude', 'longitude', 'last_location_update'])
            
        # Find current zone based on coordinates
        # Zone detection logic will be implemented in the future
        # For now, we'll just update the timestamps
        
        # Track previous zone if changed
        if location.current_zone_id and location.current_zone_id not in location.previous_zones:
            zones = location.previous_zones
            if not isinstance(zones, list):
                zones = []
            zones.append(str(location.current_zone_id))
            # Keep only the 10 most recent zones
            location.previous_zones = zones[-10:]
            
        location.last_updated = timezone.now()
        location.save()
        return location
    
    @staticmethod
    def get_economic_layer_permissions(player_profile):
        """
        Determine what actions are permitted based on economic layer.
        
        Args:
            player_profile: The PlayerProfile to check permissions for
            
        Returns:
            dict: A dictionary of permission flags
        """
        permissions = {
            'can_trade': False,
            'can_participate_governance': False,
            'can_create_projects': False,
            'can_access_common_resources': False,
        }
        
        # Port layer - basic trading
        if player_profile.economic_layer == 'port':
            permissions['can_trade'] = True
            
        # Laws layer - trading + governance
        elif player_profile.economic_layer == 'laws':
            permissions['can_trade'] = True
            permissions['can_participate_governance'] = True
            
        # Republic layer - all permissions
        elif player_profile.economic_layer == 'republic':
            permissions['can_trade'] = True
            permissions['can_participate_governance'] = True
            permissions['can_create_projects'] = True
            permissions['can_access_common_resources'] = True
            
        return permissions
    
    @staticmethod
    def rank_up_check(player_profile):
        """
        Check if a player is eligible for ranking up and perform if needed.
        
        Args:
            player_profile: The PlayerProfile to check
            
        Returns:
            tuple: (bool indicating if rank changed, new rank)
        """
        current_rank = player_profile.rank
        happiness = player_profile.happiness
        
        # Define requirements for each rank
        rank_requirements = {
            # Rank 2 requires at least 50 in all basic virtues
            2: {
                'min_virtues': {
                    'wisdom': 50,
                    'courage': 50,
                    'temperance': 50,
                    'justice': 50,
                },
                'min_experience': 1000
            },
            # Rank 3 requires at least 70 in all virtues
            3: {
                'min_virtues': {
                    'wisdom': 70,
                    'courage': 70,
                    'temperance': 70,
                    'justice': 70,
                    'strength': 50,
                    'health': 50,
                    'beauty': 50,
                    'endurance': 50,
                },
                'min_experience': 5000
            },
            # Rank 4 requires at least 85 in all virtues
            4: {
                'min_virtues': {
                    'wisdom': 85,
                    'courage': 85,
                    'temperance': 85,
                    'justice': 85,
                    'strength': 70,
                    'health': 70,
                    'beauty': 70,
                    'endurance': 70,
                },
                'min_experience': 10000
            }
        }
        
        # Check for next rank up
        next_rank = current_rank + 1
        if next_rank <= 4:  # Max rank is 4
            requirements = rank_requirements.get(next_rank)
            
            # Check experience points
            if player_profile.experience_points < requirements['min_experience']:
                return False, current_rank
                
            # Check virtue requirements
            for virtue, min_value in requirements['min_virtues'].items():
                if getattr(happiness, virtue, 0) < min_value:
                    return False, current_rank
                    
            # If we get here, all requirements are met
            player_profile.rank = next_rank
            player_profile.save(update_fields=['rank'])
            return True, next_rank
            
        return False, current_rank
    
    @staticmethod
    def recommend_experiences(player_profile, count=3):
        """
        Generate experience recommendations based on player profile.
        
        Args:
            player_profile: The PlayerProfile to generate recommendations for
            count: Number of recommendations to generate
            
        Returns:
            list: List of recommended experience dictionaries
        """
        # This is a placeholder until we implement the Experience model
        # It will generate mock recommendations based on player's lowest virtues
        
        happiness = player_profile.happiness
        
        # Get virtue scores
        virtue_scores = {
            'wisdom': happiness.wisdom,
            'courage': happiness.courage,
            'temperance': happiness.temperance,
            'justice': happiness.justice,
            'strength': happiness.strength,
            'health': happiness.health,
            'beauty': happiness.beauty,
            'endurance': happiness.endurance
        }
        
        # Sort virtues by score (lowest first)
        sorted_virtues = sorted(virtue_scores.items(), key=lambda x: x[1])
        
        # Create recommendations for lowest virtues
        recommendations = []
        
        # Example experience templates
        experience_templates = {
            'wisdom': [
                {"name": "Philosophy Study Group", "description": "Join a discussion on classical philosophy texts"},
                {"name": "Library Research", "description": "Research a topic of interest at the campus library"},
                {"name": "Mentor a Student", "description": "Share your knowledge by mentoring a younger student"}
            ],
            'courage': [
                {"name": "Public Speaking", "description": "Give a short presentation on a topic you're passionate about"},
                {"name": "Try New Activity", "description": "Sign up for an activity you've never tried before"},
                {"name": "Defend a Principle", "description": "Stand up for something you believe in during a discussion"}
            ],
            'temperance': [
                {"name": "Meditation Session", "description": "Join a guided meditation session"},
                {"name": "Delayed Gratification", "description": "Set a goal and reward for completing a task"},
                {"name": "Digital Detox", "description": "Take a break from social media for a day"}
            ],
            'justice': [
                {"name": "Volunteer Work", "description": "Volunteer for a community service project"},
                {"name": "Conflict Resolution", "description": "Help mediate a dispute between colleagues"},
                {"name": "Equal Participation", "description": "Ensure everyone gets a chance to speak in a group setting"}
            ],
            'strength': [
                {"name": "Strength Training", "description": "Join a campus gym session focusing on strength"},
                {"name": "Campus 5K", "description": "Participate in a campus running event"},
                {"name": "Group Fitness", "description": "Join a group fitness class"}
            ],
            'health': [
                {"name": "Healthy Meal Prep", "description": "Learn to prepare nutritious meals for the week"},
                {"name": "Sleep Challenge", "description": "Maintain a consistent sleep schedule for a week"},
                {"name": "Health Checkup", "description": "Schedule a routine health checkup"}
            ],
            'beauty': [
                {"name": "Art Appreciation", "description": "Visit an art exhibition and reflect on what you see"},
                {"name": "Creative Expression", "description": "Create something artistic that expresses your feelings"},
                {"name": "Campus Beautification", "description": "Join a project to improve campus aesthetics"}
            ],
            'endurance': [
                {"name": "Endurance Training", "description": "Participate in a longer workout session"},
                {"name": "Project Marathon", "description": "Work on a project consistently over several days"},
                {"name": "Study Stamina", "description": "Practice focused study techniques for extended periods"}
            ]
        }
        
        # Generate recommendations based on lowest virtues
        for virtue, score in sorted_virtues[:count]:
            if virtue in experience_templates:
                # Pick a random experience from templates for this virtue
                experience = random.choice(experience_templates[virtue]).copy()
                experience['target_virtue'] = virtue
                experience['current_score'] = score
                experience['estimated_gain'] = round(min(5, (100 - score) * 0.1), 1)
                recommendations.append(experience)
                
        # If we don't have enough recommendations, add random ones
        while len(recommendations) < count:
            virtue = random.choice(list(experience_templates.keys()))
            experience = random.choice(experience_templates[virtue]).copy()
            experience['target_virtue'] = virtue
            experience['current_score'] = virtue_scores[virtue]
            experience['estimated_gain'] = round(min(3, (100 - virtue_scores[virtue]) * 0.05), 1)
            
            # Check if this experience is already in recommendations
            if not any(r['name'] == experience['name'] for r in recommendations):
                recommendations.append(experience)
        
        return recommendations 