from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import TechTree, UserTechTreeProgress
from datetime import datetime

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class Command(BaseCommand):
    help = 'Creates test tech trees with hierarchical relationships'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        
        if not user:
            self.stdout.write(self.style.ERROR('No users found in the database'))
            return
            
        # Create base level tech trees
        self.stdout.write(self.style.SUCCESS('Creating base level tech trees...'))
        
        # Level 1 trees
        personal_dev, _ = TechTree.objects.get_or_create(
            name="Personal Development",
            defaults={
                'description': "Foundation for all growth and learning in the city",
                'level': 1,
                'unlock_message': "You have unlocked the foundation for personal growth"
            }
        )
        
        communication, _ = TechTree.objects.get_or_create(
            name="Communication",
            defaults={
                'description': "Basic communication skills and technologies",
                'level': 1,
                'unlock_message': "You have unlocked basic communication skills"
            }
        )
        
        # Level 2 trees (require level 1 trees)
        critical_thinking, _ = TechTree.objects.get_or_create(
            name="Critical Thinking",
            defaults={
                'description': "Advanced reasoning and analytical skills",
                'level': 2,
                'unlock_message': "You have unlocked advanced reasoning skills"
            }
        )
        critical_thinking.parent_nodes.add(personal_dev)
        critical_thinking.save()
        
        social_dynamics, _ = TechTree.objects.get_or_create(
            name="Social Dynamics",
            defaults={
                'description': "Understanding group behavior and social structures",
                'level': 2,
                'unlock_message': "You have unlocked understanding of social structures"
            }
        )
        social_dynamics.parent_nodes.add(communication)
        social_dynamics.save()
        
        # Level 3 trees (require multiple prerequisites)
        systems_thinking, _ = TechTree.objects.get_or_create(
            name="Systems Thinking",
            defaults={
                'description': "Understanding complex interconnected systems",
                'level': 3,
                'unlock_message': "You have unlocked systems thinking capabilities"
            }
        )
        systems_thinking.parent_nodes.add(critical_thinking)
        systems_thinking.parent_nodes.add(social_dynamics)
        systems_thinking.save()
        
        leadership, _ = TechTree.objects.get_or_create(
            name="Leadership",
            defaults={
                'description': "Guiding groups toward shared objectives",
                'level': 3,
                'unlock_message': "You have unlocked leadership capabilities"
            }
        )
        leadership.parent_nodes.add(personal_dev)
        leadership.parent_nodes.add(social_dynamics)
        leadership.save()
        
        # Create progress entries for the user
        self.stdout.write(self.style.SUCCESS(f'Creating progress entries for user: {user.username}'))
        
        # Completed first level tree
        UserTechTreeProgress.objects.update_or_create(
            user=user,
            tech_tree=personal_dev,
            defaults={
                'progress_percentage': 100,
                'is_unlocked': True,
                'unlocked_date': datetime.now()
            }
        )
        
        # Unlocked but in progress second level tree
        UserTechTreeProgress.objects.update_or_create(
            user=user,
            tech_tree=critical_thinking,
            defaults={
                'progress_percentage': 30,
                'is_unlocked': True,
                'unlocked_date': datetime.now()
            }
        )
        
        # Locked tree (no progress)
        UserTechTreeProgress.objects.update_or_create(
            user=user,
            tech_tree=systems_thinking,
            defaults={
                'progress_percentage': 0,
                'is_unlocked': False
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created tech trees and progress entries'
            )
        ) 