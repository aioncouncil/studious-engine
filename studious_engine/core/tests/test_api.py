from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    PlayerProfile, 
    PlayerHappiness, 
    UserPreferences, 
    UserLocation,
    MarketItem,
    Wishlist
)
from core.services.user_service import UserService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()

class PlayerProfileAPITests(TestCase):
    """Tests for the PlayerProfile API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create profile
        self.profile = UserService.create_user_profile(
            self.user,
            rank=1,
            economic_layer='port',
            title='Test Title',
            bio='Test Bio'
        )
        
        # Set happiness metrics
        happiness = self.profile.happiness
        happiness.wisdom = 50
        happiness.courage = 60
        happiness.temperance = 70
        happiness.justice = 80
        happiness.save()
    
    def test_get_profile(self):
        """Test retrieving a profile."""
        url = reverse('api:playerprofile-detail', args=[self.profile.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['rank'], 1)
        self.assertEqual(response.data['economic_layer'], 'port')
        self.assertEqual(response.data['title'], 'Test Title')
        self.assertEqual(response.data['bio'], 'Test Bio')
        
        # Check nested happiness data
        happiness_data = response.data['happiness_data']
        self.assertEqual(happiness_data['wisdom'], 50)
        self.assertEqual(happiness_data['courage'], 60)
        self.assertEqual(happiness_data['temperance'], 70)
        self.assertEqual(happiness_data['justice'], 80)
        self.assertIn('happiness', happiness_data)
        self.assertIn('good_score', happiness_data)
        self.assertIn('prosperity_score', happiness_data)
    
    def test_get_happiness(self):
        """Test retrieving happiness metrics."""
        url = reverse('api:playerprofile-happiness', args=[self.profile.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['wisdom'], 50)
        self.assertEqual(response.data['courage'], 60)
        self.assertEqual(response.data['temperance'], 70)
        self.assertEqual(response.data['justice'], 80)
    
    def test_update_virtues(self):
        """Test updating virtue metrics."""
        url = reverse('api:playerprofile-update-virtues', args=[self.profile.id])
        data = {
            'wisdom': 10,  # Will add 10
            'courage': -5,  # Will subtract 5
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['wisdom'], 60)  # 50 + 10
        self.assertEqual(response.data['courage'], 55)  # 60 - 5
        self.assertEqual(response.data['temperance'], 70)  # Unchanged
        self.assertEqual(response.data['justice'], 80)  # Unchanged
    
    def test_get_preferences(self):
        """Test retrieving user preferences."""
        # Set some preferences first
        preferences = self.profile.preferences
        preferences.interface_settings = {'theme': 'dark'}
        preferences.save()
        
        url = reverse('api:playerprofile-preferences', args=[self.profile.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['interface_settings']['theme'], 'dark')
    
    def test_update_preferences(self):
        """Test updating user preferences."""
        url = reverse('api:playerprofile-preferences', args=[self.profile.id])
        data = {
            'interface_settings': {'theme': 'light', 'fontSize': 'large'},
            'language_preference': 'fr'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['interface_settings']['theme'], 'light')
        self.assertEqual(response.data['interface_settings']['fontSize'], 'large')
        self.assertEqual(response.data['language_preference'], 'fr')
    
    def test_get_location(self):
        """Test retrieving user location."""
        # Set location first
        location = self.profile.location
        location.latitude = 40.7128
        location.longitude = -74.0060
        location.save()
        
        url = reverse('api:playerprofile-location', args=[self.profile.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['latitude'], 40.7128)
        self.assertEqual(response.data['longitude'], -74.0060)
    
    def test_update_location(self):
        """Test updating user location."""
        url = reverse('api:playerprofile-location', args=[self.profile.id])
        data = {
            'latitude': 34.0522,
            'longitude': -118.2437,
            'accuracy_meters': 10,
            'device_id': 'test-device'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['latitude'], 34.0522)
        self.assertEqual(response.data['longitude'], -118.2437)
        self.assertEqual(response.data['accuracy_meters'], 10)
        self.assertEqual(response.data['device_id'], 'test-device')
    
    def test_get_economic_permissions(self):
        """Test retrieving economic layer permissions."""
        url = reverse('api:playerprofile-economic-permissions', args=[self.profile.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_trade'])
        self.assertFalse(response.data['can_participate_governance'])
        self.assertFalse(response.data['can_create_projects'])
        self.assertFalse(response.data['can_access_common_resources'])
        
        # Update to Republic layer
        self.profile.economic_layer = 'republic'
        self.profile.save()
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_trade'])
        self.assertTrue(response.data['can_participate_governance'])
        self.assertTrue(response.data['can_create_projects'])
        self.assertTrue(response.data['can_access_common_resources'])
    
    def test_get_recommended_experiences(self):
        """Test retrieving recommended experiences."""
        url = reverse('api:playerprofile-recommended-experiences', args=[self.profile.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 3)  # Default is 3
        
        # Test with query parameter
        url = f"{url}?count=2"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Requested 2

class MarketItemAPITests(TestCase):
    """Tests for the MarketItem API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create profile
        self.profile = UserService.create_user_profile(
            self.user,
            rank=2,
            economic_layer='laws'
        )
        
        # Create market items
        self.item1 = MarketItem.objects.create(
            name="Item 1",
            description="Description 1",
            economic_layer="outer",
            price="100",
            price_type="credits",
            category="physical",
            min_rank_required=1
        )
        
        self.item2 = MarketItem.objects.create(
            name="Item 2",
            description="Description 2",
            economic_layer="middle",
            price="200",
            price_type="merit",
            category="digital",
            min_rank_required=2
        )
        
        self.item3 = MarketItem.objects.create(
            name="Item 3",
            description="Description 3",
            economic_layer="inner",
            price="300",
            price_type="contribution",
            category="experience",
            min_rank_required=3
        )
    
    def test_list_available_items(self):
        """Test listing available items based on economic layer and rank."""
        url = reverse('api:marketitem-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Laws layer user with rank 2 should see outer and middle items
        self.assertEqual(len(response.data), 2)
        item_names = [item['name'] for item in response.data]
        self.assertIn("Item 1", item_names)
        self.assertIn("Item 2", item_names)
        self.assertNotIn("Item 3", item_names)  # Rank 3 required
    
    def test_filter_by_category(self):
        """Test filtering items by category."""
        url = reverse('api:marketitem-list') + '?category=digital'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Item 2")
    
    def test_add_to_wishlist(self):
        """Test adding an item to wishlist."""
        url = reverse('api:marketitem-add-to-wishlist', args=[self.item1.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item'], self.item1.id)
        self.assertEqual(response.data['user'], self.user.id)
        
        # Check wishlist entry was created
        wishlist_exists = Wishlist.objects.filter(
            user=self.user,
            item=self.item1
        ).exists()
        self.assertTrue(wishlist_exists)
    
    def test_remove_from_wishlist(self):
        """Test removing an item from wishlist."""
        # First add to wishlist
        Wishlist.objects.create(user=self.user, item=self.item1)
        
        url = reverse('api:marketitem-remove-from-wishlist', args=[self.item1.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check wishlist entry was deleted
        wishlist_exists = Wishlist.objects.filter(
            user=self.user,
            item=self.item1
        ).exists()
        self.assertFalse(wishlist_exists)

class WishlistAPITests(TestCase):
    """Tests for the Wishlist API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create items
        self.item1 = MarketItem.objects.create(
            name="Item 1",
            description="Description 1",
            economic_layer="outer",
            price="100",
            category="physical"
        )
        
        self.item2 = MarketItem.objects.create(
            name="Item 2",
            description="Description 2",
            economic_layer="outer",
            price="200",
            category="digital"
        )
        
        # Add items to wishlist
        self.wishlist1 = Wishlist.objects.create(user=self.user, item=self.item1)
        self.wishlist2 = Wishlist.objects.create(user=self.user, item=self.item2)
    
    def test_list_wishlist(self):
        """Test listing user's wishlist items."""
        url = reverse('api:wishlist-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        item_names = [item['item_details']['name'] for item in response.data]
        self.assertIn("Item 1", item_names)
        self.assertIn("Item 2", item_names) 