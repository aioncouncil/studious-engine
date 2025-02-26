# studious_engine/core/management/commands/seed_eudaimonia.py
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

# Fix import paths to match project structure
try:
    # Try direct imports first
    from core.models import PlayerProfile, PlayerHappiness
    from zones.models import Sector, Zone, ZoneHappiness
    from experiences.models import Power, Experience
    from innovations.models import TechTreeNode
except ImportError:
    # Fall back to prefixed imports if needed
    from studious_engine.core.models import PlayerProfile, PlayerHappiness
    from studious_engine.zones.models import Sector, Zone, ZoneHappiness
    from studious_engine.experiences.models import Power, Experience
    from studious_engine.innovations.models import TechTreeNode

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial EudaimoniaGo content'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding the database with EudaimoniaGo content...')
        
        # Create sectors
        self.create_sectors()
        
        # Create sample zones
        self.create_zones()
        
        # Create powers
        self.create_powers()
        
        # Create experiences
        self.create_experiences()
        
        # Create tech tree nodes
        self.create_tech_tree()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))
    
    def create_sectors(self):
        """Create the 12 primary sectors of the city."""
        self.stdout.write('Creating sectors...')
        
        sectors = [
            (1, "Instruments", "Sector focused on tool creation and refinement."),
            (2, "Defenses", "Sector responsible for city protection and security measures."),
            (3, "Materials", "Sector specializing in resource gathering and processing."),
            (4, "Health", "Sector dedicated to medical care and wellbeing."),
            (5, "Ornaments", "Sector focused on arts, culture, and beautification."),
            (6, "Vessels", "Sector responsible for containers and storage solutions."),
            (7, "Vehicles", "Sector specializing in transportation and mobility."),
            (8, "Labor", "Sector dedicated to workforce management and optimization."),
            (9, "Commerce", "Sector focused on trade, economics, and resource distribution."),
            (10, "Scripts", "Sector responsible for education, record-keeping, and documentation."),
            (11, "Analysis", "Sector specializing in research, data analysis, and planning."),
            (12, "Direction", "Sector dedicated to leadership and governance."),
        ]
        
        for number, name, description in sectors:
            Sector.objects.get_or_create(
                number=number,
                defaults={
                    'name': name,
                    'description': description,
                    'is_governing': (number == 12),  # Direction sector starts as governing
                    'governing_start_date': timezone.now() if number == 12 else None
                }
            )
        
        self.stdout.write(f'Created {len(sectors)} sectors')
    
    def create_zones(self):
        """Create sample zones for each sector."""
        self.stdout.write('Creating zones...')
        
        sectors = Sector.objects.all()
        
        # For demonstration, we'll create just a few zones per sector
        area_choices = ['agora', 'polis', 'chora']
        zone_types = [
            "Philosophy", "Mathematics", "Agriculture", "Medicine", 
            "Craftsmanship", "Music", "Literature", "Athletics",
            "Architecture", "Astronomy", "Military Training", "Law",
            "Commerce", "Navigation", "Mining", "Woodworking",
            "Pottery", "Textiles", "Metallurgy", "Oration",
            "Diplomacy", "Governance", "Education", "Cooking"
        ]
        
        zones_created = 0
        
        for sector in sectors:
            # Create 5 sample zones per sector for demonstration
            for i in range(1, 6):
                zone_type = f"{random.choice(zone_types)} {i}"
                area = random.choice(area_choices)
                
                zone, created = Zone.objects.get_or_create(
                    sector=sector,
                    zone_number=i,
                    defaults={
                        'zone_type': zone_type,
                        'area': area,
                        'rank': random.randint(1, 4)
                    }
                )
                
                if created:
                    zones_created += 1
                    
                    # Create happiness metrics for the zone
                    ZoneHappiness.objects.get_or_create(
                        zone=zone,
                        defaults={
                            'wisdom': random.randint(20, 80),
                            'courage': random.randint(20, 80),
                            'temperance': random.randint(20, 80),
                            'justice': random.randint(20, 80),
                            'strength': random.randint(20, 80),
                            'wealth': random.randint(20, 80),
                            'beauty': random.randint(20, 80),
                            'health': random.randint(20, 80),
                            'resources': random.randint(20, 80),
                            'friendships': random.randint(20, 80),
                            'honors': random.randint(20, 80),
                            'glory': random.randint(20, 80)
                        }
                    )
        
        self.stdout.write(f'Created {zones_created} zones')
    
    def create_powers(self):
        """Create sample powers for the game."""
        self.stdout.write('Creating powers...')
        
        sectors = Sector.objects.all()
        
        powers = [
            ("Logical Thinking", "The ability to analyze problems systematically.", "idea", 3, 5, 11),
            ("Artistic Expression", "The ability to create beautiful works of art.", "skill", 4, 6, 5),
            ("Physical Strength", "Enhanced physical capabilities.", "skill", 2, 4, 8),
            ("Agricultural Knowledge", "Understanding of farming and crop management.", "idea", 3, 5, 3),
            ("Medicinal Herbs", "Knowledge of healing plants and their applications.", "idea", 5, 7, 4),
            ("Pottery Making", "Skill in creating ceramic vessels.", "skill", 2, 4, 6),
            ("Metallurgy", "Knowledge of metal working and forging.", "skill", 6, 8, 3),
            ("Navigation", "Ability to navigate efficiently.", "skill", 4, 6, 7),
            ("Governance", "Understanding of leadership principles.", "idea", 7, 9, 12),
            ("Mathematics", "Knowledge of numbers and calculations.", "idea", 5, 8, 11),
            ("Oration", "Skill in public speaking and persuasion.", "skill", 3, 6, 10),
            ("Architecture", "Knowledge of building design and construction.", "idea", 6, 8, 5),
            ("Weaving", "Skill in creating textiles.", "skill", 2, 4, 6),
            ("Astronomy", "Knowledge of celestial bodies and their movements.", "idea", 7, 9, 11),
            ("Combat Training", "Skill in various fighting techniques.", "skill", 5, 7, 2),
            ("Trade Negotiation", "Ability to make favorable business deals.", "skill", 4, 6, 9),
            ("Writing", "Skill in clear and effective communication through text.", "skill", 3, 5, 10),
            ("Tool Making", "Ability to craft useful implements.", "skill", 3, 5, 1),
        ]
        
        powers_created = 0
        
        for name, description, power_type, rarity, complexity, sector_num in powers:
            sector = sectors.filter(number=sector_num).first()
            
            power, created = Power.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'power_type': power_type,
                    'rarity': rarity,
                    'complexity': complexity,
                    'sector': sector,
                    'is_public': True
                }
            )
            
            if created:
                powers_created += 1
        
        self.stdout.write(f'Created {powers_created} powers')
    
    def create_experiences(self):
        """Create sample experiences for the game."""
        self.stdout.write('Creating experiences...')
        
        matrix_positions = ['soul_out', 'soul_in', 'body_out', 'body_in']
        experience_types = ['quest', 'challenge', 'collaboration', 'innovation', 'reflection']
        art_types = ['imitation', 'production', 'usage']
        good_types = ['present', 'present_future', 'future']
        
        experiences = [
            ("City Cleanup", "Help maintain the beauty of the city by cleaning up public spaces.", 'quest', 'body_out', 'production', 'present', 2, 30, 5, 10),
            ("Philosophical Debate", "Engage in a structured debate about virtue and knowledge.", 'challenge', 'soul_out', 'imitation', 'present_future', 6, 60, 15, 20),
            ("Pottery Workshop", "Learn and practice the art of pottery making.", 'collaboration', 'body_out', 'production', 'present', 3, 90, 10, 15),
            ("Agricultural Planning", "Plan the seasonal crop rotation for maximum yield.", 'innovation', 'soul_out', 'usage', 'future', 5, 45, 20, 25),
            ("Community Storytelling", "Share and listen to stories that preserve cultural knowledge.", 'reflection', 'soul_in', 'imitation', 'present', 1, 60, 5, 10),
            ("Bridge Construction", "Collaborate to build a bridge connecting two areas.", 'collaboration', 'body_out', 'production', 'present_future', 7, 120, 25, 30),
            ("Market Arithmetic", "Practice mathematical skills in a market setting.", 'challenge', 'body_in', 'usage', 'present', 4, 30, 10, 15),
            ("Historical Research", "Investigate and document historical events.", 'quest', 'soul_in', 'imitation', 'future', 5, 90, 15, 20),
            ("Medicinal Plant Collection", "Gather and identify plants with healing properties.", 'quest', 'body_out', 'usage', 'present', 3, 60, 10, 15),
            ("Festival Planning", "Design and organize a community celebration.", 'innovation', 'soul_out', 'production', 'future', 6, 120, 20, 25),
        ]
        
        experiences_created = 0
        powers = list(Power.objects.all())
        zones = list(Zone.objects.all())
        
        for name, description, exp_type, matrix, art, good, difficulty, duration, happiness, xp in experiences:
            exp, created = Experience.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'experience_type': exp_type,
                    'matrix_position': matrix,
                    'art_type': art,
                    'good_type': good,
                    'difficulty': difficulty,
                    'duration_minutes': duration,
                    'happiness_reward': happiness,
                    'experience_reward': xp,
                    'is_active': True,
                    'minimum_rank': 1,
                    'definition': f"Definition of {name}",
                    'end': f"Purpose of {name}",
                    'parts': f"Components of {name}",
                    'matter': f"Materials for {name}",
                    'instrument': f"Tools for {name}"
                }
            )
            
            if created:
                experiences_created += 1
                
                # Assign random powers as requirements (1-3)
                req_powers = random.sample(powers, random.randint(1, min(3, len(powers))))
                exp.required_powers.set(req_powers)
                
                # Assign random zones (1-2)
                associated_zones = random.sample(zones, random.randint(1, min(2, len(zones))))
                exp.associated_zones.set(associated_zones)
        
        self.stdout.write(f'Created {experiences_created} experiences')
    
    def create_tech_tree(self):
        """Create a basic tech tree for the city."""
        self.stdout.write('Creating tech tree...')
        
        sectors = Sector.objects.all()
        
        tech_tree_nodes = [
            ("Basic Tools", "Fundamental tools for daily tasks.", 1, 1, 0, 0, True),
            ("Agriculture", "Knowledge of farming techniques.", 1, 3, 1, 1, True),
            ("Simple Shelters", "Basic building construction techniques.", 1, 5, 2, 0, True),
            ("Fire Making", "Ability to create and control fire.", 1, 7, 3, 0, True),
            ("Basic Medicine", "Simple healing techniques and remedies.", 1, 4, 4, 0, True),
            
            ("Advanced Tools", "More sophisticated tools for specialized tasks.", 2, 1, 0, 1, False),
            ("Irrigation", "Water management systems for agriculture.", 2, 3, 1, 1, False),
            ("Architecture", "Advanced building designs and techniques.", 2, 5, 2, 1, False),
            ("Metallurgy", "Metal working and forging techniques.", 2, 7, 3, 1, False),
            ("Herbalism", "Advanced knowledge of medicinal plants.", 2, 4, 4, 1, False),
            
            ("Mechanical Devices", "Simple machines that multiply force.", 3, 1, 0, 2, False),
            ("Crop Rotation", "Sustainable farming through strategic planting.", 3, 3, 1, 2, False),
            ("Public Buildings", "Community structures for gatherings and governance.", 3, 5, 2, 2, False),
            ("Advanced Metallurgy", "Creating stronger alloys and specialized metals.", 3, 7, 3, 2, False),
            ("Surgical Techniques", "Procedures for advanced medical treatment.", 3, 4, 4, 2, False),
        ]
        
        nodes_created = 0
        
        for name, description, level, sector_num, x_pos, y_pos, is_unlocked in tech_tree_nodes:
            sector = sectors.filter(number=sector_num).first() if sector_num else None
            
            node, created = TechTreeNode.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'sector': sector,
                    'level': level,
                    'is_unlocked': is_unlocked,
                    'unlocked_at': timezone.now() if is_unlocked else None,
                    'icon': f"{name.lower().replace(' ', '_')}.png",
                    'position_x': x_pos,
                    'position_y': y_pos
                }
            )
            
            if created:
                nodes_created += 1
        
        # Set up prerequisites for level 2 nodes
        if nodes_created > 0:
            level1_nodes = TechTreeNode.objects.filter(level=1)
            level2_nodes = TechTreeNode.objects.filter(level=2)
            
            for node in level2_nodes:
                # Find corresponding level 1 node in same sector
                prereq = level1_nodes.filter(sector=node.sector).first()
                if prereq:
                    node.prerequisites.add(prereq)
            
            # Set up prerequisites for level 3 nodes
            level3_nodes = TechTreeNode.objects.filter(level=3)
            
            for node in level3_nodes:
                # Find corresponding level 2 node in same sector
                prereq = level2_nodes.filter(sector=node.sector).first()
                if prereq:
                    node.prerequisites.add(prereq)
        
        self.stdout.write(f'Created {nodes_created} tech tree nodes')