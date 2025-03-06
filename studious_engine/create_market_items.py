import os
import sys
import django
import random
from datetime import timedelta

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.utils import timezone
from core.models import MarketItem
from django.contrib.auth import get_user_model

# [REF:44e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9:ECONOMIC_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the economic_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()

# Sample data for market items
ITEM_NAMES = {
    'physical': [
        'Handcrafted Artifact',
        'Eco-friendly Notebook',
        'Sustainable Water Bottle',
        'Handmade Jewelry Set',
        'Artisan Coffee Set',
        'Organic Textile Kit',
    ],
    'service': [
        'Coding Mentorship',
        'Financial Planning Session',
        'Fitness Coaching Package',
        'Language Tutoring',
        'Digital Marketing Consultation',
        'Resume Review Service',
    ],
    'digital': [
        'Premium Digital Art Pack',
        'E-book Collection',
        'Software Development Tools',
        'Educational Video Series',
        'Design Template Bundle',
        'Music Production Kit',
    ],
    'investment': [
        'Sustainable Investment Share',
        'Community Project Stake',
        'Innovation Fund Contribution',
        'Campus Improvement Bond',
        'Research Initiative Backing',
        'Startup Incubator Investment',
    ],
    'skill': [
        'Advanced Programming Course',
        'Public Speaking Workshop',
        'Data Analysis Masterclass',
        'Creative Writing Seminar',
        'Leadership Development Program',
        'Critical Thinking Workshop',
    ],
    'experience': [
        'Philosophy Symposium',
        'Cultural Exchange Week',
        'Virtual Reality Experience',
        'Culinary Masterclass',
        'Outdoor Expedition',
        'Music Production Workshop',
    ],
    'collaboration': [
        'Research Collaboration',
        'Community Project Partnership',
        'Startup Co-founding Opportunity',
        'Open Source Project Contribution',
        'Group Art Installation',
        'Collaborative Writing Project',
    ],
    'resource': [
        'Shared Workshop Access',
        'Citizen Plot Ownership',
        'Equipment Lending Program',
        'Studio Space Time-Share',
        'Co-working Space Membership',
        'Community Garden Plot',
    ],
}

DESCRIPTIONS = {
    'physical': "Tangible products crafted with care and sustainability in mind. Each item is designed to enhance your daily life while minimizing environmental impact.",
    'service': "Expert services provided by qualified professionals in our community. These offerings help you develop skills and solve problems.",
    'digital': "Digital assets and resources that can be accessed and utilized immediately. These items enhance your productivity and creativity.",
    'investment': "Investment opportunities that contribute to both community development and personal returns. Each option has been vetted for sustainability and impact.",
    'skill': "Knowledge and skill development opportunities taught by experienced instructors. These programs help you grow personally and professionally.",
    'experience': "Curated experiences designed to broaden horizons and create meaningful memories. Each experience offers unique perspectives and engagement.",
    'collaboration': "Partnership opportunities that allow you to work with others on meaningful projects. These collaborations build community while creating value.",
    'resource': "Shared resources that provide access to valuable tools, spaces, and equipment. These sharing arrangements maximize utility while minimizing waste."
}

PRICE_BY_LAYER = {
    'outer': lambda: f"{random.randint(10, 100)} Credits",
    'middle': lambda: f"{random.choice(['Class II', 'Class III', 'Class IV'])} Required" if random.random() > 0.5 else f"{random.randint(20, 200)} Credits",
    'inner': lambda: random.choice(["Merit Access", "Contribution Based", "Open Access"])
}

PRICE_TYPE_BY_LAYER = {
    'outer': 'credits',
    'middle': lambda: random.choice(['credits', 'merit']),
    'inner': lambda: random.choice(['merit', 'contribution'])
}

def create_sample_items():
    """Create sample market items for different categories and layers."""
    print("Creating sample market items...")
    
    # Count existing items to avoid duplicates
    existing_count = MarketItem.objects.count()
    if existing_count > 0:
        print(f"Found {existing_count} existing market items. Checking what needs to be created...")
    
    created_count = 0
    
    # Create items for each category and layer
    for category, names in ITEM_NAMES.items():
        for name in names:
            # Create one version of this item for each economic layer
            for layer in ['outer', 'middle', 'inner']:
                # Check if this item already exists
                if MarketItem.objects.filter(name=name, economic_layer=layer).exists():
                    continue
                
                # Set price and price type based on layer
                price = PRICE_BY_LAYER[layer]()
                
                if callable(PRICE_TYPE_BY_LAYER[layer]):
                    price_type = PRICE_TYPE_BY_LAYER[layer]()
                else:
                    price_type = PRICE_TYPE_BY_LAYER[layer]
                
                # Create the item
                item = MarketItem(
                    name=name,
                    description=f"{name}: {DESCRIPTIONS[category]} This particular offering is available in the {layer} economic layer.",
                    economic_layer=layer,
                    price=price,
                    price_type=price_type,
                    category=category,
                    is_available=True,
                    quantity=random.randint(1, 10) if layer != 'inner' else None,
                    min_rank_required=1 if layer == 'outer' else (2 if layer == 'middle' else 3),
                    is_featured=random.random() > 0.8,  # 20% chance of being featured
                    recommendation_score=random.uniform(0, 10),
                )
                
                # Some items have a limited availability time
                if random.random() > 0.7:  # 30% chance
                    days_available = random.randint(1, 30)
                    item.available_until = timezone.now() + timedelta(days=days_available)
                
                item.save()
                created_count += 1
                print(f"Created: {item.name} ({item.economic_layer} layer)")
    
    print(f"Created {created_count} new market items.")
    print(f"Total market items: {existing_count + created_count}")

if __name__ == "__main__":
    create_sample_items() 