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
    help = 'Creates a test tech tree progress entry for the first user'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        
        if not user:
            self.stdout.write(self.style.ERROR('No users found in the database'))
            return
            
        tech_trees = TechTree.objects.all()
        
        if not tech_trees.exists():
            self.stdout.write(self.style.ERROR('No tech trees found in the database'))
            return
            
        # Display available tech trees
        self.stdout.write(self.style.SUCCESS(f'Found user: {user.username}'))
        self.stdout.write(self.style.SUCCESS(f'Found {tech_trees.count()} tech trees:'))
        
        for i, tree in enumerate(tech_trees):
            self.stdout.write(f'{i+1}. {tree.name}')
            
        # Create progress for the first tech tree
        if tech_trees.count() > 0:
            tree = tech_trees.first()
            progress, created = UserTechTreeProgress.objects.update_or_create(
                user=user,
                tech_tree=tree,
                defaults={
                    'progress_percentage': 50,
                    'is_unlocked': True,
                    'unlocked_date': datetime.now()
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(
                    f'{action} progress entry for "{user.username}" - "{tree.name}" '
                    f'(50% Progress, Unlocked: {progress.is_unlocked})'
                )
            )
            
        # If there's a second tree, create progress with different values
        if tech_trees.count() > 1:
            tree = tech_trees[1]
            progress, created = UserTechTreeProgress.objects.update_or_create(
                user=user,
                tech_tree=tree,
                defaults={
                    'progress_percentage': 25,
                    'is_unlocked': False
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(
                    f'{action} progress entry for "{user.username}" - "{tree.name}" '
                    f'(25% Progress, Unlocked: {progress.is_unlocked})'
                )
            ) 