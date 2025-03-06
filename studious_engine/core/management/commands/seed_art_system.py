import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models.art.art import Art, ArtParts, ArtStage, ArtTaxonomy
from core.models.art.tech_tree import TechTree
from core.services.art.art_service import ArtService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class Command(BaseCommand):
    help = 'Seeds the Art System with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Flush existing art data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing art data...'))
            TechTree.objects.all().delete()
            Art.objects.all().delete()
            ArtTaxonomy.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing art data flushed.'))

        self.stdout.write(self.style.NOTICE('Seeding Art Taxonomy...'))
        taxonomies = self._create_taxonomies()
        
        self.stdout.write(self.style.NOTICE('Seeding Arts...'))
        arts = self._create_arts(taxonomies)
        
        self.stdout.write(self.style.NOTICE('Seeding Art Parts...'))
        self._create_art_parts(arts)
        
        self.stdout.write(self.style.NOTICE('Seeding Art Stages...'))
        self._create_art_stages(arts)
        
        self.stdout.write(self.style.NOTICE('Seeding Tech Trees...'))
        self._create_tech_trees(arts)
        
        self.stdout.write(self.style.SUCCESS('Art System seeded successfully!'))

    def _create_taxonomies(self):
        # Create main categories
        categories = [
            {
                'name': 'Intellectual Arts',
                'description': 'Arts focused on developing the mind and intellectual capabilities.',
                'level': 1,
            },
            {
                'name': 'Physical Arts',
                'description': 'Arts focused on developing the body and physical capabilities.',
                'level': 1,
            },
            {
                'name': 'Creative Arts',
                'description': 'Arts focused on creative expression and aesthetic development.',
                'level': 1,
            },
            {
                'name': 'Social Arts',
                'description': 'Arts focused on social interaction and community building.',
                'level': 1,
            },
            {
                'name': 'Spiritual Arts',
                'description': 'Arts focused on spiritual development and inner growth.',
                'level': 1,
            },
        ]
        
        created_categories = []
        for category in categories:
            taxonomy, created = ArtTaxonomy.objects.get_or_create(
                name=category['name'],
                defaults={
                    'description': category['description'],
                    'level': category['level'],
                }
            )
            created_categories.append(taxonomy)
            self.stdout.write(f"{'Created' if created else 'Found'} category: {taxonomy.name}")
        
        # Create subcategories
        subcategories = [
            # Intellectual Arts subcategories
            {
                'name': 'Logic & Reasoning',
                'description': 'Arts focused on logical thinking and reasoning.',
                'level': 2,
                'parent': 'Intellectual Arts',
            },
            {
                'name': 'Languages & Communication',
                'description': 'Arts focused on language acquisition and communication.',
                'level': 2,
                'parent': 'Intellectual Arts',
            },
            {
                'name': 'Sciences',
                'description': 'Arts focused on scientific inquiry and understanding.',
                'level': 2,
                'parent': 'Intellectual Arts',
            },
            
            # Physical Arts subcategories
            {
                'name': 'Martial Arts',
                'description': 'Arts focused on combat and self-defense.',
                'level': 2,
                'parent': 'Physical Arts',
            },
            {
                'name': 'Movement Arts',
                'description': 'Arts focused on body movement and coordination.',
                'level': 2,
                'parent': 'Physical Arts',
            },
            {
                'name': 'Health & Wellness',
                'description': 'Arts focused on maintaining and improving health.',
                'level': 2,
                'parent': 'Physical Arts',
            },
            
            # Creative Arts subcategories
            {
                'name': 'Visual Arts',
                'description': 'Arts focused on visual expression and aesthetics.',
                'level': 2,
                'parent': 'Creative Arts',
            },
            {
                'name': 'Performing Arts',
                'description': 'Arts focused on performance and entertainment.',
                'level': 2,
                'parent': 'Creative Arts',
            },
            {
                'name': 'Literary Arts',
                'description': 'Arts focused on written expression and storytelling.',
                'level': 2,
                'parent': 'Creative Arts',
            },
            
            # Social Arts subcategories
            {
                'name': 'Leadership',
                'description': 'Arts focused on leading and inspiring others.',
                'level': 2,
                'parent': 'Social Arts',
            },
            {
                'name': 'Community Building',
                'description': 'Arts focused on building and strengthening communities.',
                'level': 2,
                'parent': 'Social Arts',
            },
            {
                'name': 'Diplomacy & Negotiation',
                'description': 'Arts focused on resolving conflicts and building consensus.',
                'level': 2,
                'parent': 'Social Arts',
            },
            
            # Spiritual Arts subcategories
            {
                'name': 'Meditation & Mindfulness',
                'description': 'Arts focused on developing awareness and presence.',
                'level': 2,
                'parent': 'Spiritual Arts',
            },
            {
                'name': 'Philosophical Inquiry',
                'description': 'Arts focused on exploring fundamental questions of existence.',
                'level': 2,
                'parent': 'Spiritual Arts',
            },
            {
                'name': 'Ethical Development',
                'description': 'Arts focused on developing moral character and ethical reasoning.',
                'level': 2,
                'parent': 'Spiritual Arts',
            },
        ]
        
        created_subcategories = []
        for subcategory in subcategories:
            parent = ArtTaxonomy.objects.get(name=subcategory['parent'])
            taxonomy, created = ArtTaxonomy.objects.get_or_create(
                name=subcategory['name'],
                defaults={
                    'description': subcategory['description'],
                    'level': subcategory['level'],
                    'parent': parent,
                }
            )
            created_subcategories.append(taxonomy)
            self.stdout.write(f"{'Created' if created else 'Found'} subcategory: {taxonomy.name}")
        
        return created_categories + created_subcategories

    def _create_arts(self, taxonomies):
        arts_data = [
            # Intellectual Arts
            {
                'name': 'Critical Thinking',
                'description': 'The art of analyzing and evaluating thinking with a view to improving it.',
                'taxonomy': 'Logic & Reasoning',
                'difficulty_level': 2,
                'required_virtues': {'wisdom': 10, 'courage': 5},
                'improved_virtues': {'wisdom': 20, 'justice': 10},
                'rank_required': 1,
                'economic_layer_required': 'PORT',
                'practice_method': 'SOLO',
                'is_unlocked_default': True,
            },
            {
                'name': 'Rhetoric',
                'description': 'The art of effective or persuasive speaking or writing.',
                'taxonomy': 'Languages & Communication',
                'difficulty_level': 3,
                'required_virtues': {'wisdom': 15, 'courage': 10},
                'improved_virtues': {'wisdom': 15, 'courage': 15, 'justice': 10},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'PAIR',
            },
            {
                'name': 'Scientific Method',
                'description': 'The art of systematic observation, measurement, and experiment, and the formulation, testing, and modification of hypotheses.',
                'taxonomy': 'Sciences',
                'difficulty_level': 3,
                'required_virtues': {'wisdom': 20, 'temperance': 10},
                'improved_virtues': {'wisdom': 25, 'temperance': 15},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'SOLO',
            },
            
            # Physical Arts
            {
                'name': 'Tai Chi',
                'description': 'An internal Chinese martial art practiced for defense training, health benefits, and meditation.',
                'taxonomy': 'Martial Arts',
                'difficulty_level': 2,
                'required_virtues': {'temperance': 10, 'strength': 5},
                'improved_virtues': {'temperance': 15, 'strength': 10, 'health': 15},
                'rank_required': 1,
                'economic_layer_required': 'PORT',
                'practice_method': 'GROUP',
                'is_unlocked_default': True,
            },
            {
                'name': 'Parkour',
                'description': 'The art of moving through urban environments by running, climbing, and jumping.',
                'taxonomy': 'Movement Arts',
                'difficulty_level': 4,
                'required_virtues': {'courage': 20, 'strength': 15, 'endurance': 15},
                'improved_virtues': {'courage': 25, 'strength': 20, 'endurance': 20},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'PAIR',
            },
            {
                'name': 'Nutrition',
                'description': 'The art of understanding and applying principles of healthy eating.',
                'taxonomy': 'Health & Wellness',
                'difficulty_level': 2,
                'required_virtues': {'wisdom': 10, 'temperance': 15},
                'improved_virtues': {'wisdom': 15, 'temperance': 20, 'health': 25},
                'rank_required': 1,
                'economic_layer_required': 'PORT',
                'practice_method': 'SOLO',
                'is_unlocked_default': True,
            },
            
            # Creative Arts
            {
                'name': 'Drawing',
                'description': 'The art of creating visual representations using lines and shading.',
                'taxonomy': 'Visual Arts',
                'difficulty_level': 2,
                'required_virtues': {'beauty': 10, 'temperance': 5},
                'improved_virtues': {'beauty': 20, 'temperance': 10, 'wisdom': 5},
                'rank_required': 1,
                'economic_layer_required': 'PORT',
                'practice_method': 'SOLO',
                'is_unlocked_default': True,
            },
            {
                'name': 'Dance',
                'description': 'The art of moving rhythmically to music, using prescribed or improvised steps and gestures.',
                'taxonomy': 'Performing Arts',
                'difficulty_level': 3,
                'required_virtues': {'beauty': 15, 'strength': 10, 'endurance': 10},
                'improved_virtues': {'beauty': 20, 'strength': 15, 'endurance': 15},
                'rank_required': 1,
                'economic_layer_required': 'PORT',
                'practice_method': 'GROUP',
            },
            {
                'name': 'Poetry',
                'description': 'The art of expressing emotions, experiences, and ideas through language.',
                'taxonomy': 'Literary Arts',
                'difficulty_level': 3,
                'required_virtues': {'wisdom': 15, 'beauty': 15},
                'improved_virtues': {'wisdom': 20, 'beauty': 20, 'courage': 5},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'SOLO',
            },
            
            # Social Arts
            {
                'name': 'Public Speaking',
                'description': 'The art of speaking effectively to an audience.',
                'taxonomy': 'Leadership',
                'difficulty_level': 3,
                'required_virtues': {'courage': 20, 'wisdom': 10},
                'improved_virtues': {'courage': 25, 'wisdom': 15, 'justice': 10},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'GROUP',
            },
            {
                'name': 'Community Organizing',
                'description': 'The art of bringing people together to address common concerns and achieve shared goals.',
                'taxonomy': 'Community Building',
                'difficulty_level': 4,
                'required_virtues': {'justice': 20, 'courage': 15, 'wisdom': 15},
                'improved_virtues': {'justice': 25, 'courage': 20, 'wisdom': 20},
                'rank_required': 3,
                'economic_layer_required': 'LAWS',
                'practice_method': 'GROUP',
            },
            {
                'name': 'Conflict Resolution',
                'description': 'The art of addressing and resolving disputes between individuals or groups.',
                'taxonomy': 'Diplomacy & Negotiation',
                'difficulty_level': 3,
                'required_virtues': {'justice': 15, 'temperance': 15, 'wisdom': 10},
                'improved_virtues': {'justice': 20, 'temperance': 20, 'wisdom': 15},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'PAIR',
            },
            
            # Spiritual Arts
            {
                'name': 'Mindfulness Meditation',
                'description': 'The art of focusing one\'s awareness on the present moment.',
                'taxonomy': 'Meditation & Mindfulness',
                'difficulty_level': 2,
                'required_virtues': {'temperance': 10, 'wisdom': 5},
                'improved_virtues': {'temperance': 20, 'wisdom': 15, 'health': 10},
                'rank_required': 1,
                'economic_layer_required': 'PORT',
                'practice_method': 'SOLO',
                'is_unlocked_default': True,
            },
            {
                'name': 'Socratic Dialogue',
                'description': 'The art of cooperative argumentative dialogue between individuals, based on asking and answering questions to stimulate critical thinking.',
                'taxonomy': 'Philosophical Inquiry',
                'difficulty_level': 3,
                'required_virtues': {'wisdom': 20, 'courage': 10, 'justice': 10},
                'improved_virtues': {'wisdom': 25, 'courage': 15, 'justice': 15},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'PAIR',
            },
            {
                'name': 'Virtue Ethics',
                'description': 'The art of developing moral character through the cultivation of virtues.',
                'taxonomy': 'Ethical Development',
                'difficulty_level': 3,
                'required_virtues': {'justice': 15, 'wisdom': 15, 'temperance': 10},
                'improved_virtues': {'justice': 20, 'wisdom': 20, 'temperance': 15},
                'rank_required': 2,
                'economic_layer_required': 'PORT',
                'practice_method': 'SOLO',
            },
        ]
        
        created_arts = []
        for art_data in arts_data:
            taxonomy = ArtTaxonomy.objects.get(name=art_data['taxonomy'])
            art, created = Art.objects.get_or_create(
                name=art_data['name'],
                defaults={
                    'description': art_data['description'],
                    'taxonomy': taxonomy,
                    'difficulty_level': art_data['difficulty_level'],
                    'required_virtues': art_data['required_virtues'],
                    'improved_virtues': art_data['improved_virtues'],
                    'rank_required': art_data['rank_required'],
                    'economic_layer_required': art_data['economic_layer_required'],
                    'practice_method': art_data['practice_method'],
                    'is_unlocked_default': art_data.get('is_unlocked_default', False),
                }
            )
            created_arts.append(art)
            self.stdout.write(f"{'Created' if created else 'Found'} art: {art.name}")
        
        return created_arts

    def _create_art_parts(self, arts):
        for art in arts:
            # Each art will have 3-5 parts
            num_parts = random.randint(3, 5)
            
            for i in range(num_parts):
                if i == 0:
                    # First part: Theory
                    name = f"Understanding {art.name}"
                    description = f"Learn the fundamental principles and concepts of {art.name}."
                    practice_method = 'THEORY'
                    practice_description = f"Study the history, principles, and key concepts of {art.name}."
                    validation_method = 'SELF'
                    estimated_hours = random.randint(2, 5)
                elif i == num_parts - 1:
                    # Last part: Teaching or Reflection
                    if random.choice([True, False]):
                        name = f"Teaching {art.name}"
                        description = f"Share your knowledge of {art.name} with others."
                        practice_method = 'TEACHING'
                        practice_description = f"Prepare and deliver a lesson on {art.name} to others."
                        validation_method = 'PEER'
                        estimated_hours = random.randint(3, 6)
                    else:
                        name = f"Reflecting on {art.name}"
                        description = f"Reflect on your journey learning {art.name} and integrate it into your life."
                        practice_method = 'REFLECTION'
                        practice_description = f"Journal about your experiences with {art.name} and how it has changed you."
                        validation_method = 'SELF'
                        estimated_hours = random.randint(2, 4)
                else:
                    # Middle parts: Practice or Creation
                    if random.choice([True, False]):
                        name = f"Practicing {art.name} - Level {i}"
                        description = f"Develop your skills in {art.name} through regular practice."
                        practice_method = 'PRACTICE'
                        practice_description = f"Engage in structured practice sessions to develop your {art.name} skills."
                        validation_method = 'SELF'
                        estimated_hours = random.randint(5, 10)
                    else:
                        name = f"Creating with {art.name} - Project {i}"
                        description = f"Apply your knowledge of {art.name} to create something new."
                        practice_method = 'CREATION'
                        practice_description = f"Complete a project that demonstrates your understanding and skill in {art.name}."
                        validation_method = 'PEER'
                        estimated_hours = random.randint(8, 15)
                
                # Create the art part
                art_part, created = ArtParts.objects.get_or_create(
                    art=art,
                    order_index=i,
                    defaults={
                        'name': name,
                        'description': description,
                        'practice_method': practice_method,
                        'practice_description': practice_description,
                        'validation_method': validation_method,
                        'estimated_hours': estimated_hours,
                        'resources_required': {},
                        'media_references': [],
                    }
                )
                
                self.stdout.write(f"{'Created' if created else 'Found'} art part: {art_part.name}")

    def _create_art_stages(self, arts):
        for art in arts:
            # Each art will have 3-5 stages
            num_stages = random.randint(3, 5)
            
            for i in range(num_stages):
                if i == 0:
                    # First stage: Novice
                    name = f"Novice {art.name}"
                    description = f"The beginning stage of learning {art.name}."
                    mastery_threshold = 10
                    virtue_bonuses = {k: v * 0.2 for k, v in art.improved_virtues.items()}
                elif i == num_stages - 1:
                    # Last stage: Master
                    name = f"Master of {art.name}"
                    description = f"The highest level of mastery in {art.name}."
                    mastery_threshold = 100
                    virtue_bonuses = art.improved_virtues
                else:
                    # Middle stages: Apprentice, Journeyman, etc.
                    stage_names = ["Apprentice", "Journeyman", "Adept", "Expert"]
                    name = f"{stage_names[i-1]} {art.name}"
                    description = f"An intermediate stage of mastery in {art.name}."
                    mastery_threshold = 25 * i
                    virtue_bonuses = {k: v * (0.4 * i) for k, v in art.improved_virtues.items()}
                
                # Create the art stage
                art_stage, created = ArtStage.objects.get_or_create(
                    art=art,
                    order_index=i,
                    defaults={
                        'name': name,
                        'description': description,
                        'mastery_threshold': mastery_threshold,
                        'virtue_bonuses': virtue_bonuses,
                        'unlock_requirements': {},
                    }
                )
                
                self.stdout.write(f"{'Created' if created else 'Found'} art stage: {art_stage.name}")

    def _create_tech_trees(self, arts):
        # Create 3 tech trees
        tech_trees_data = [
            {
                'name': 'Personal Development',
                'description': 'A tech tree focused on developing personal skills and virtues.',
                'level': 1,
                'zone_type_filter': 'ANY',
                'position_x': 0,
                'position_y': 0,
            },
            {
                'name': 'Community Building',
                'description': 'A tech tree focused on developing community and social skills.',
                'level': 2,
                'zone_type_filter': 'SOCIAL',
                'position_x': 10,
                'position_y': 0,
            },
            {
                'name': 'Philosophical Inquiry',
                'description': 'A tech tree focused on developing philosophical understanding and wisdom.',
                'level': 3,
                'zone_type_filter': 'ACADEMIC',
                'position_x': 0,
                'position_y': 10,
            },
        ]
        
        created_tech_trees = []
        for tech_tree_data in tech_trees_data:
            tech_tree, created = TechTree.objects.get_or_create(
                name=tech_tree_data['name'],
                defaults={
                    'description': tech_tree_data['description'],
                    'level': tech_tree_data['level'],
                    'zone_type_filter': tech_tree_data['zone_type_filter'],
                    'position_x': tech_tree_data['position_x'],
                    'position_y': tech_tree_data['position_y'],
                    'required_arts': [],
                    'unlocks_arts': [],
                    'required_resources': {},
                }
            )
            created_tech_trees.append(tech_tree)
            self.stdout.write(f"{'Created' if created else 'Found'} tech tree: {tech_tree.name}")
        
        # Assign arts to tech trees
        for art in arts:
            # Assign each art to a random tech tree
            tech_tree = random.choice(created_tech_trees)
            
            # Add the art to the tech tree's unlocks_arts
            if str(art.id) not in tech_tree.unlocks_arts:
                tech_tree.unlocks_arts.append(str(art.id))
                tech_tree.save()
                self.stdout.write(f"Added {art.name} to {tech_tree.name} tech tree") 