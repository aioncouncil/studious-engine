from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

from core.models import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    PlayerProfile, 
    PlayerHappiness, 
    UserPreferences, 
    UserLocation,
    MarketItem,
    Wishlist,
)

User = get_user_model()

class PlayerProfileModelTests(TestCase):
    """Tests for the PlayerProfile model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            rank=1,
            experience_points=100,
            economic_layer='port',
            title="Campus Explorer",
            bio="Test bio"
        )
    
    def test_profile_creation(self):
        """Test that profile is created correctly."""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.rank, 1)
        self.assertEqual(self.profile.economic_layer, 'port')
        self.assertEqual(self.profile.title, "Campus Explorer")
        self.assertEqual(self.profile.bio, "Test bio")
    
    def test_profile_level_calculation(self):
        """Test level property calculates correctly."""
        # Test level 1
        self.profile.experience_points = 50
        self.assertEqual(self.profile.level, 1)
        
        # Test level 2
        self.profile.experience_points = 200
        self.assertEqual(self.profile.level, 2)
        
        # Test higher level
        self.profile.experience_points = 10000
        self.assertTrue(self.profile.level > 5)

class PlayerHappinessTests(TestCase):
    """Tests for the PlayerHappiness model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            rank=1
        )
        self.happiness = PlayerHappiness.objects.create(
            player=self.profile,
            wisdom=50,
            courage=60,
            temperance=70,
            justice=80,
            strength=40,
            health=30,
            beauty=20,
            endurance=10
        )
    
    def test_happiness_creation(self):
        """Test that happiness metrics are created correctly."""
        self.assertEqual(self.happiness.wisdom, 50)
        self.assertEqual(self.happiness.courage, 60)
        self.assertEqual(self.happiness.temperance, 70)
        self.assertEqual(self.happiness.justice, 80)
        self.assertEqual(self.happiness.strength, 40)
        self.assertEqual(self.happiness.health, 30)
        self.assertEqual(self.happiness.beauty, 20)
        self.assertEqual(self.happiness.endurance, 10)
    
    def test_score_calculation(self):
        """Test that good and prosperity scores are calculated correctly."""
        self.happiness.save()  # This should trigger score calculations
        
        # Good score = (wisdom + courage + temperance + justice) / 4
        expected_good = (50 + 60 + 70 + 80) / 4
        self.assertEqual(self.happiness.good_score, expected_good)
        
        # Prosperity score = (strength + health + beauty + endurance) / 4
        expected_prosperity = (40 + 30 + 20 + 10) / 4
        self.assertEqual(self.happiness.prosperity_score, expected_prosperity)
        
        # Happiness = (good + prosperity) / 2
        expected_happiness = (expected_good + expected_prosperity) / 2
        self.assertEqual(self.happiness.happiness, expected_happiness)

class UserPreferencesTests(TestCase):
    """Tests for the UserPreferences model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            rank=1
        )
        self.preferences = UserPreferences.objects.create(
            player=self.profile,
            language_preference='en'
        )
    
    def test_preferences_creation(self):
        """Test that preferences are created with defaults."""
        self.assertEqual(self.preferences.language_preference, 'en')
        
        # Test default values are set on save
        self.preferences.save()
        self.assertIn('theme', self.preferences.interface_settings)
        self.assertIn('enabled', self.preferences.ai_guide_settings)
        self.assertIn('profileVisibility', self.preferences.privacy_settings)
    
    def test_preferences_update(self):
        """Test updating preferences."""
        self.preferences.interface_settings = {
            'theme': 'dark',
            'fontSize': 'large'
        }
        self.preferences.save()
        
        # Reload from DB
        self.preferences.refresh_from_db()
        self.assertEqual(self.preferences.interface_settings['theme'], 'dark')
        self.assertEqual(self.preferences.interface_settings['fontSize'], 'large')

class UserLocationTests(TestCase):
    """Tests for the UserLocation model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            rank=1
        )
        self.location = UserLocation.objects.create(
            player=self.profile,
            latitude=40.7128,
            longitude=-74.0060,
            accuracy_meters=10,
            device_id='test-device'
        )
    
    def test_location_creation(self):
        """Test that location data is stored correctly."""
        self.assertEqual(self.location.latitude, 40.7128)
        self.assertEqual(self.location.longitude, -74.0060)
        self.assertEqual(self.location.accuracy_meters, 10)
        self.assertEqual(self.location.device_id, 'test-device')
    
    def test_location_update(self):
        """Test updating location."""
        self.location.update_location(
            latitude=34.0522,
            longitude=-118.2437,
            accuracy=5,
            device_id='new-device'
        )
        
        # Reload from DB
        self.location.refresh_from_db()
        self.assertEqual(self.location.latitude, 34.0522)
        self.assertEqual(self.location.longitude, -118.2437)
        self.assertEqual(self.location.accuracy_meters, 5)
        self.assertEqual(self.location.device_id, 'new-device')
        
        # Check that profile location was also updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.latitude, 34.0522)
        self.assertEqual(self.profile.longitude, -118.2437)
        self.assertIsNotNone(self.profile.last_location_update)

class MarketItemTests(TestCase):
    """Tests for the MarketItem model."""
    
    def setUp(self):
        """Set up test data."""
        self.item = MarketItem.objects.create(
            name="Test Item",
            description="A test item",
            economic_layer="outer",
            price="100",
            price_type="credits",
            category="physical",
            min_rank_required=1
        )
    
    def test_item_creation(self):
        """Test that market item is created correctly."""
        self.assertEqual(self.item.name, "Test Item")
        self.assertEqual(self.item.description, "A test item")
        self.assertEqual(self.item.economic_layer, "outer")
        self.assertEqual(self.item.price, "100")
        self.assertEqual(self.item.price_type, "credits")
        self.assertEqual(self.item.category, "physical")
        self.assertEqual(self.item.min_rank_required, 1)
        self.assertTrue(self.item.is_available)
    
    def test_economic_layer_properties(self):
        """Test economic layer properties."""
        self.assertTrue(self.item.is_outer_layer)
        self.assertFalse(self.item.is_middle_layer)
        self.assertFalse(self.item.is_inner_layer)
        
        # Update layer
        self.item.economic_layer = "middle"
        self.item.save()
        
        self.assertFalse(self.item.is_outer_layer)
        self.assertTrue(self.item.is_middle_layer)
        self.assertFalse(self.item.is_inner_layer)

class WishlistTests(TestCase):
    """Tests for the Wishlist model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.item = MarketItem.objects.create(
            name="Test Item",
            description="A test item",
            economic_layer="outer",
            price="100",
            price_type="credits",
            category="physical",
            min_rank_required=1
        )
    
    def test_wishlist_creation(self):
        """Test that wishlist entry is created correctly."""
        wishlist = Wishlist.objects.create(
            user=self.user,
            item=self.item
        )
        
        self.assertEqual(wishlist.user, self.user)
        self.assertEqual(wishlist.item, self.item)
        self.assertIsNotNone(wishlist.added_at)
    
    def test_wishlist_uniqueness(self):
        """Test that a user can't add the same item twice."""
        Wishlist.objects.create(
            user=self.user,
            item=self.item
        )
        
        # Trying to create a duplicate should raise an error
        with self.assertRaises(Exception):
            Wishlist.objects.create(
                user=self.user,
                item=self.item
            ) 