from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import (
    PlayerProfile, 
    PlayerHappiness, 
    UserPreferences, 
    UserLocation
)
from core.services.user_service import UserService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()

class UserServiceTests(TestCase):
    """Tests for the UserService class."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_profile(self):
        """Test creating a user profile with the service."""
        # Create profile with some custom attributes
        profile = UserService.create_user_profile(
            self.user,
            rank=2,
            economic_layer='laws',
            title='Test Title',
            bio='Test Bio'
        )
        
        # Check profile attributes
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.rank, 2)
        self.assertEqual(profile.economic_layer, 'laws')
        self.assertEqual(profile.title, 'Test Title')
        self.assertEqual(profile.bio, 'Test Bio')
        
        # Check that related models were created
        self.assertTrue(hasattr(profile, 'happiness'))
        self.assertTrue(hasattr(profile, 'preferences'))
        self.assertTrue(hasattr(profile, 'location'))
    
    def test_update_happiness(self):
        """Test updating happiness metrics with the service."""
        # Create profile with default attributes
        profile = UserService.create_user_profile(self.user)
        
        # Set initial values for testing
        happiness = profile.happiness
        happiness.wisdom = 50
        happiness.courage = 50
        happiness.temperance = 50
        happiness.justice = 50
        happiness.strength = 50
        happiness.health = 50
        happiness.beauty = 50
        happiness.endurance = 50
        happiness.save()
        
        # Update some virtues
        updated_happiness = UserService.update_happiness(
            profile,
            wisdom=10,  # Add 10
            courage=-5,  # Subtract 5
            temperance=0,  # No change
            health=20  # Add 20
        )
        
        # Check updated values
        self.assertEqual(updated_happiness.wisdom, 60)  # 50 + 10
        self.assertEqual(updated_happiness.courage, 45)  # 50 - 5
        self.assertEqual(updated_happiness.temperance, 50)  # No change
        self.assertEqual(updated_happiness.health, 70)  # 50 + 20
        
        # Check untouched values remain the same
        self.assertEqual(updated_happiness.justice, 50)
        self.assertEqual(updated_happiness.strength, 50)
        self.assertEqual(updated_happiness.beauty, 50)
        self.assertEqual(updated_happiness.endurance, 50)
        
        # Check that virtue history was recorded
        self.assertTrue(isinstance(updated_happiness.virtue_history, list))
        self.assertTrue(len(updated_happiness.virtue_history) > 0)
    
    def test_update_location(self):
        """Test updating user location with the service."""
        # Create profile with default attributes
        profile = UserService.create_user_profile(self.user)
        
        # Update location
        location = UserService.update_location(
            profile,
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=10,
            device_id='test-device'
        )
        
        # Check location attributes
        self.assertEqual(location.latitude, 40.7128)
        self.assertEqual(location.longitude, -74.0060)
        self.assertEqual(location.accuracy_meters, 10)
        self.assertEqual(location.device_id, 'test-device')
        
        # Check profile attributes were also updated
        profile.refresh_from_db()
        self.assertEqual(profile.latitude, 40.7128)
        self.assertEqual(profile.longitude, -74.0060)
        self.assertIsNotNone(profile.last_location_update)
    
    def test_economic_layer_permissions(self):
        """Test getting economic layer permissions."""
        # Create profile with default attributes (Port layer)
        profile = UserService.create_user_profile(self.user)
        
        # Check Port layer permissions
        port_permissions = UserService.get_economic_layer_permissions(profile)
        self.assertTrue(port_permissions['can_trade'])
        self.assertFalse(port_permissions['can_participate_governance'])
        self.assertFalse(port_permissions['can_create_projects'])
        self.assertFalse(port_permissions['can_access_common_resources'])
        
        # Update to Laws layer
        profile.economic_layer = 'laws'
        profile.save()
        
        # Check Laws layer permissions
        laws_permissions = UserService.get_economic_layer_permissions(profile)
        self.assertTrue(laws_permissions['can_trade'])
        self.assertTrue(laws_permissions['can_participate_governance'])
        self.assertFalse(laws_permissions['can_create_projects'])
        self.assertFalse(laws_permissions['can_access_common_resources'])
        
        # Update to Republic layer
        profile.economic_layer = 'republic'
        profile.save()
        
        # Check Republic layer permissions
        republic_permissions = UserService.get_economic_layer_permissions(profile)
        self.assertTrue(republic_permissions['can_trade'])
        self.assertTrue(republic_permissions['can_participate_governance'])
        self.assertTrue(republic_permissions['can_create_projects'])
        self.assertTrue(republic_permissions['can_access_common_resources'])
    
    def test_rank_up_check(self):
        """Test rank-up eligibility check."""
        # Create profile with default attributes
        profile = UserService.create_user_profile(self.user)
        happiness = profile.happiness
        
        # Set initial values - not enough for rank 2
        profile.experience_points = 500
        profile.save()
        
        happiness.wisdom = 40
        happiness.courage = 40
        happiness.temperance = 40
        happiness.justice = 40
        happiness.save()
        
        # Check not eligible yet
        rank_changed, current_rank = UserService.rank_up_check(profile)
        self.assertFalse(rank_changed)
        self.assertEqual(current_rank, 1)
        
        # Make eligible for rank 2
        profile.experience_points = 1500
        profile.save()
        
        happiness.wisdom = 60
        happiness.courage = 60
        happiness.temperance = 60
        happiness.justice = 60
        happiness.save()
        
        # Check now eligible
        rank_changed, current_rank = UserService.rank_up_check(profile)
        self.assertTrue(rank_changed)
        self.assertEqual(current_rank, 2)
        
        # Profile should be updated
        profile.refresh_from_db()
        self.assertEqual(profile.rank, 2)
    
    def test_recommend_experiences(self):
        """Test experience recommendations."""
        # Create profile with default attributes
        profile = UserService.create_user_profile(self.user)
        happiness = profile.happiness
        
        # Set virtues with wisdom as lowest
        happiness.wisdom = 10
        happiness.courage = 50
        happiness.temperance = 50
        happiness.justice = 50
        happiness.strength = 50
        happiness.health = 50
        happiness.beauty = 50
        happiness.endurance = 50
        happiness.save()
        
        # Get recommendations
        recommendations = UserService.recommend_experiences(profile, count=3)
        
        # Check we got the right number
        self.assertEqual(len(recommendations), 3)
        
        # First recommendation should target wisdom
        self.assertEqual(recommendations[0]['target_virtue'], 'wisdom')
        
        # All recommendations should have required attributes
        for rec in recommendations:
            self.assertIn('name', rec)
            self.assertIn('description', rec)
            self.assertIn('target_virtue', rec)
            self.assertIn('current_score', rec)
            self.assertIn('estimated_gain', rec) 