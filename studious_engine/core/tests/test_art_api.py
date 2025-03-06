import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from studious_engine.core.models import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    Art,
    ArtParts,
    ArtStage,
    ArtTaxonomy,
    TechTree,
    ArtMastery,
    PlayerProfile,
    PlayerHappiness,
)


User = get_user_model()


class ArtAPITests(TestCase):
    """Tests for the Art API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create profile
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            rank=2,
            experience_points=1000,
            economic_layer='laws'
        )
        
        # Create happiness metrics
        self.happiness = PlayerHappiness.objects.create(
            player=self.profile,
            wisdom=60,
            courage=70,
            temperance=50,
            justice=65
        )
        
        # Create taxonomy
        self.taxonomy = ArtTaxonomy.objects.create(
            name="Test Taxonomy",
            description="A test taxonomy",
            level=1
        )
        
        # Create an art
        self.art = Art.objects.create(
            name="Test Art",
            description="A test art",
            taxonomy=self.taxonomy,
            difficulty_level=2,
            rank_required=1,
            economic_layer_required="PORT",
            improved_virtues={"wisdom": 10, "courage": 5}
        )
        
        # Create art parts
        self.art_part1 = ArtParts.objects.create(
            art=self.art,
            name="Test Part 1",
            description="First test part",
            order_index=0,
            practice_method="THEORY",
            practice_description="Study the theory",
            validation_method="SELF",
            estimated_hours=5
        )
        
        self.art_part2 = ArtParts.objects.create(
            art=self.art,
            name="Test Part 2",
            description="Second test part",
            order_index=1,
            practice_method="PRACTICE",
            practice_description="Practice regularly",
            validation_method="PEER",
            estimated_hours=10
        )
        
        # Create art stages
        self.art_stage = ArtStage.objects.create(
            art=self.art,
            name="Beginner",
            description="Beginner stage",
            order_index=0,
            mastery_threshold=20
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_arts(self):
        """Test retrieving the list of arts."""
        url = reverse('api:art-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Art')
    
    def test_retrieve_art_detail(self):
        """Test retrieving detailed art information."""
        url = reverse('api:art-detail', kwargs={'pk': self.art.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Art')
        self.assertTrue('parts' in response.data)
        self.assertTrue('stages' in response.data)
        self.assertEqual(len(response.data['parts']), 2)
        self.assertEqual(len(response.data['stages']), 1)
    
    def test_discover_art(self):
        """Test discovering/starting to master an art."""
        url = reverse('api:art-discover', kwargs={'pk': self.art.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['art']['name'], 'Test Art')
        self.assertEqual(response.data['mastery_level'], 0)
        
        # Check that a mastery record was created
        mastery = ArtMastery.objects.filter(user=self.user, art=self.art).first()
        self.assertIsNotNone(mastery)
        self.assertEqual(mastery.mastery_level, 0)
    
    def test_featured_arts(self):
        """Test retrieving featured arts."""
        # Mark the art as featured
        self.art.is_featured = True
        self.art.save()
        
        url = reverse('api:art-featured')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: this test may need adjustment based on how featured arts are determined
    
    def test_arts_by_virtue(self):
        """Test retrieving arts by virtue improvement."""
        url = reverse('api:art-by-virtue') + '?virtue=wisdom'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Art')


class ArtTaxonomyAPITests(TestCase):
    """Tests for the Art Taxonomy API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create taxonomy hierarchy
        self.parent_taxonomy = ArtTaxonomy.objects.create(
            name="Parent Taxonomy",
            description="A parent taxonomy",
            level=1
        )
        
        self.child_taxonomy = ArtTaxonomy.objects.create(
            name="Child Taxonomy",
            description="A child taxonomy",
            parent=self.parent_taxonomy,
            level=2
        )
        
        # Create arts in the taxonomies
        self.art1 = Art.objects.create(
            name="Art in Parent",
            description="An art in parent taxonomy",
            taxonomy=self.parent_taxonomy,
            difficulty_level=1
        )
        
        self.art2 = Art.objects.create(
            name="Art in Child",
            description="An art in child taxonomy",
            taxonomy=self.child_taxonomy,
            difficulty_level=2
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_taxonomies(self):
        """Test retrieving the list of taxonomies."""
        url = reverse('api:art-taxonomy-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_taxonomies_by_level(self):
        """Test filtering taxonomies by level."""
        url = reverse('api:art-taxonomy-list') + '?level=1'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Parent Taxonomy')
    
    def test_filter_taxonomies_by_parent(self):
        """Test filtering taxonomies by parent."""
        url = reverse('api:art-taxonomy-list') + f'?parent={self.parent_taxonomy.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Child Taxonomy')
    
    def test_list_arts_in_taxonomy(self):
        """Test retrieving arts in a taxonomy."""
        url = reverse('api:art-taxonomy-arts', kwargs={'pk': self.parent_taxonomy.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Art in Parent')


class ArtMasteryAPITests(TestCase):
    """Tests for the Art Mastery API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create profile
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            rank=2,
            experience_points=1000,
            economic_layer='laws'
        )
        
        # Create happiness metrics
        self.happiness = PlayerHappiness.objects.create(
            player=self.profile,
            wisdom=60,
            courage=70,
            temperance=50,
            justice=65
        )
        
        # Create an art
        self.art = Art.objects.create(
            name="Test Art",
            description="A test art",
            difficulty_level=2
        )
        
        # Create art parts
        self.art_part = ArtParts.objects.create(
            art=self.art,
            name="Test Part",
            description="Test part description",
            order_index=0,
            practice_method="PRACTICE",
            practice_description="Practice description",
            validation_method="SELF",
            estimated_hours=5
        )
        
        # Create art mastery
        self.mastery = ArtMastery.objects.create(
            user=self.user,
            art=self.art,
            mastery_level=1,
            current_part=self.art_part
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_masteries(self):
        """Test retrieving the list of user's art masteries."""
        url = reverse('api:art-mastery-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['art']['name'], 'Test Art')
    
    def test_log_practice(self):
        """Test logging a practice session."""
        url = reverse('api:art-mastery-practice', kwargs={'pk': self.mastery.id})
        data = {
            'art_id': str(self.art.id),
            'part_id': str(self.art_part.id),
            'duration_minutes': 45,
            'notes': 'Test practice session'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('mastery' in response.data)
        self.assertTrue('session' in response.data)
        
        # Check that the practice session was recorded
        self.mastery.refresh_from_db()
        self.assertEqual(len(self.mastery.practice_history), 1)
        
        # Check that XP was awarded
        self.profile.refresh_from_db()
        self.assertGreater(self.profile.experience_points, 1000)
    
    def test_validate_practice(self):
        """Test validating practice."""
        # First log a practice session
        self.mastery.log_practice_session(
            part=self.art_part,
            duration_minutes=60,
            notes="Session to validate",
            validated=False
        )
        self.mastery.save()
        
        url = reverse('api:art-mastery-validate', kwargs={'pk': self.mastery.id})
        data = {
            'art_id': str(self.art.id),
            'part_id': str(self.art_part.id)
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('mastery' in response.data)
        self.assertTrue('validated' in response.data)
        
        # Since this is SELF validation, it should be validated
        self.assertTrue(response.data['validated'])
        
        # Check that the part is now in completed parts
        self.mastery.refresh_from_db()
        self.assertIn(str(self.art_part.id), self.mastery.completed_parts)
    
    def test_get_practice_stats(self):
        """Test retrieving practice statistics."""
        # Log some practice sessions
        self.mastery.log_practice_session(
            part=self.art_part,
            duration_minutes=30,
            notes="Session 1",
            validated=False
        )
        self.mastery.log_practice_session(
            part=self.art_part,
            duration_minutes=45,
            notes="Session 2",
            validated=True
        )
        self.mastery.save()
        
        url = reverse('api:art-mastery-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('total_sessions' in response.data)
        self.assertEqual(response.data['total_sessions'], 2)
        self.assertEqual(response.data['total_minutes'], 75)


class TechTreeAPITests(TestCase):
    """Tests for the Tech Tree API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create profile
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            rank=2,
            experience_points=1000,
            economic_layer='laws'
        )
        
        # Create tech trees
        self.tech_tree1 = TechTree.objects.create(
            name="Basic Tree",
            description="A basic tech tree",
            level=1,
            achievement_bonus={"xp": 100, "wisdom": 5}
        )
        
        self.tech_tree2 = TechTree.objects.create(
            name="Advanced Tree",
            description="An advanced tech tree",
            level=2
        )
        
        # Setup prerequisite relationship
        self.tech_tree2.parent_nodes.add(self.tech_tree1)
        
        # Create an art
        self.art = Art.objects.create(
            name="Test Art",
            description="A test art",
            difficulty_level=2
        )
        
        # Add art to tech tree
        self.tech_tree1.arts.add(self.art)
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_tech_trees(self):
        """Test retrieving the list of tech trees."""
        url = reverse('api:tech-tree-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_tech_trees_by_level(self):
        """Test filtering tech trees by level."""
        url = reverse('api:tech-tree-list') + '?level=1'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Basic Tree')
    
    def test_get_available_tech_trees(self):
        """Test retrieving available tech trees."""
        url = reverse('api:tech-tree-available')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Basic Tree should be available, Advanced Tree requires Basic Tree to be completed
        available_tree_ids = [tree['id'] for tree in response.data]
        self.assertIn(str(self.tech_tree1.id), available_tree_ids)
    
    def test_get_tech_tree_prerequisites(self):
        """Test checking prerequisites for a tech tree."""
        url = reverse('api:tech-tree-prerequisites', kwargs={'pk': self.tech_tree2.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['prerequisites_met'])  # Should be false initially
        self.assertEqual(len(response.data['prerequisites']), 1)
        self.assertEqual(response.data['prerequisites'][0]['tech_tree_name'], 'Basic Tree')
    
    def test_update_tech_tree_progress(self):
        """Test updating progress for a tech tree."""
        # Create an art mastery at maximum level
        mastery = ArtMastery.objects.create(
            user=self.user,
            art=self.art,
            mastery_level=5  # Max level
        )
        
        url = reverse('api:tech-tree-update-progress', kwargs={'pk': self.tech_tree1.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('progress', response.data)
        
        # The progress should now be 100% since we've mastered the only art
        progress_data = response.data['progress']
        self.assertEqual(progress_data['percent_complete'], 100)
        
        # The profile should have gained XP from the achievement bonus
        self.profile.refresh_from_db()
        self.assertGreater(self.profile.experience_points, 1000) 