from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, Optional, List, Tuple
import uuid
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from core.models import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    TechTree,
    UserTechTreeProgress,
    Art,
    ArtMastery,
    PlayerProfile
)

User = get_user_model()

class TechTreeService:
    """
    Service for managing tech tree progression.
    """
    
    @staticmethod
    def create_tech_tree(name, description, prerequisite_trees=None, arts=None, achievement_bonus=None):
        """
        Create a new tech tree.
        
        Args:
            name: The name of the tech tree
            description: The description of the tech tree
            prerequisite_trees: Optional list of prerequisite TechTree objects or IDs
            arts: Optional list of Art objects or IDs associated with this tree
            achievement_bonus: Optional dict of bonuses for completing the tree
            
        Returns:
            TechTree: The created tech tree
        """
        with transaction.atomic():
            tech_tree = TechTree.objects.create(
                name=name,
                description=description,
                achievement_bonus=achievement_bonus or {}
            )
            
            # Add prerequisite trees
            if prerequisite_trees:
                for tree in prerequisite_trees:
                    if not isinstance(tree, TechTree):
                        try:
                            tree = TechTree.objects.get(id=tree)
                        except TechTree.DoesNotExist:
                            continue
                    tech_tree.parent_nodes.add(tree)
            
            # Add arts
            if arts:
                for art in arts:
                    TechTreeService.add_art_to_tree(tech_tree, art)
                    
            return tech_tree
    
    @staticmethod
    def add_art_to_tree(tech_tree, art, required_for_completion=True, order_index=None):
        """
        Add an art to a tech tree.
        
        Args:
            tech_tree: The TechTree object or ID
            art: The Art object or ID
            required_for_completion: Whether this art is required to complete the tech tree
            order_index: Optional order index for display purposes
            
        Returns:
            TechTree: The updated tech tree
        """
        if not isinstance(tech_tree, TechTree):
            try:
                tech_tree = TechTree.objects.get(id=tech_tree)
            except TechTree.DoesNotExist:
                raise ValueError(f"TechTree with ID {tech_tree} does not exist")
        
        if not isinstance(art, Art):
            try:
                art = Art.objects.get(id=art)
            except Art.DoesNotExist:
                raise ValueError(f"Art with ID {art} does not exist")
        
        # Add the art to the tech tree
        tech_tree.arts.add(art)
        
        # Update the through table attributes
        through = tech_tree.arts.through.objects.get(techtree=tech_tree, art=art)
        through.required_for_completion = required_for_completion
        if order_index is not None:
            through.order_index = order_index
        through.save()
        
        return tech_tree
    
    @staticmethod
    def get_user_progress(user, tech_tree=None):
        """
        Get a user's progress in a tech tree or all tech trees.
        
        Args:
            user: The User object or ID
            tech_tree: Optional TechTree object or ID
            
        Returns:
            UserTechTreeProgress or queryset: The user's progress
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        if tech_tree:
            if not isinstance(tech_tree, TechTree):
                try:
                    tech_tree = TechTree.objects.get(id=tech_tree)
                except TechTree.DoesNotExist:
                    raise ValueError(f"TechTree with ID {tech_tree} does not exist")
            
            progress, created = UserTechTreeProgress.objects.get_or_create(
                user=user,
                tech_tree=tech_tree,
                defaults={'progress': {}, 'completed': False, 'completion_date': None}
            )
            return progress
        else:
            return UserTechTreeProgress.objects.filter(user=user)
    
    @staticmethod
    def update_progress(user, tech_tree):
        """
        Update a user's progress in a tech tree based on their art masteries.
        
        Args:
            user: The User object or ID
            tech_tree: The TechTree object or ID
            
        Returns:
            UserTechTreeProgress: The updated progress
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        if not isinstance(tech_tree, TechTree):
            try:
                tech_tree = TechTree.objects.get(id=tech_tree)
            except TechTree.DoesNotExist:
                raise ValueError(f"TechTree with ID {tech_tree} does not exist")
        
        # Get user progress
        progress = TechTreeService.get_user_progress(user, tech_tree)
        
        # Get the arts in this tech tree
        tree_arts = tech_tree.arts.through.objects.filter(techtree=tech_tree)
        required_arts = [ta.art_id for ta in tree_arts if ta.required_for_completion]
        
        # Get user's masteries for these arts
        masteries = ArtMastery.objects.filter(user=user, art__in=required_arts)
        
        # Calculate progress percentage
        total_arts = len(required_arts)
        if total_arts == 0:
            percent_complete = 0
        else:
            # Calculate mastery level percentage for each required art
            art_progress = {}
            total_progress = 0
            
            for mastery in masteries:
                # Calculate percentage mastery (0-100)
                if mastery.mastery_level >= 5:  # Max mastery level
                    art_percent = 100
                else:
                    art_percent = (mastery.mastery_level / 5) * 100
                
                art_progress[str(mastery.art.id)] = {
                    'mastery_level': mastery.mastery_level,
                    'percent_complete': art_percent,
                    'completed': mastery.mastery_level >= 5
                }
                
                total_progress += art_percent
            
            percent_complete = total_progress / total_arts if total_arts > 0 else 0
            
            # Update progress record
            progress.progress = {
                'percent_complete': percent_complete,
                'arts': art_progress,
                'last_updated': timezone.now().isoformat()
            }
            
            # Check if all required arts are completed
            completed = all(
                art_progress.get(str(art_id), {}).get('completed', False) 
                for art_id in required_arts
            )
            
            # If newly completed, apply achievement bonus
            if completed and not (progress and progress.progress_percentage >= 100):
                progress.progress_percentage = 100
                progress.completion_date = timezone.now()
                
                # Apply achievement bonus if any
                if tech_tree.achievement_bonus:
                    try:
                        profile = PlayerProfile.objects.get(user=user)
                        
                        # Apply XP bonus
                        if 'xp' in tech_tree.achievement_bonus:
                            profile.experience_points += tech_tree.achievement_bonus['xp']
                        
                        # Apply virtue bonuses
                        virtues = ['wisdom', 'courage', 'temperance', 'justice']
                        for virtue in virtues:
                            if virtue in tech_tree.achievement_bonus:
                                current = getattr(profile.happiness_metrics, virtue)
                                bonus = tech_tree.achievement_bonus[virtue]
                                setattr(profile.happiness_metrics, virtue, min(100, current + bonus))
                        
                        profile.save()
                    except PlayerProfile.DoesNotExist:
                        pass
            
            progress.save()
        
        return progress
    
    @staticmethod
    def check_prerequisites(user, tech_tree):
        """
        Check if a user meets the prerequisites for a tech tree.
        
        Args:
            user: The User object or ID
            tech_tree: The TechTree object or ID
            
        Returns:
            Tuple[bool, List[Dict]]: (prerequisites_met, prerequisite_status)
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
                
        if not isinstance(tech_tree, TechTree):
            try:
                tech_tree = TechTree.objects.get(id=tech_tree)
            except TechTree.DoesNotExist:
                raise ValueError(f"TechTree with ID {tech_tree} does not exist")
        
        # Get all prerequisites
        prerequisites = tech_tree.parent_nodes.all()
        
        if not prerequisites.exists():
            # No prerequisites, so they're automatically met
            return True, []
        
        # Get user progress for prerequisite trees
        user_progress = {
            p.tech_tree_id: p 
            for p in UserTechTreeProgress.objects.filter(
                user=user,
                tech_tree_id__in=prerequisites.values_list('id', flat=True)
            )
        }
        
        prereq_status = []
        all_met = True
        
        for prereq in prerequisites:
            progress = user_progress.get(prereq.id)
            is_completed = progress and progress.progress_percentage >= 100
            
            prereq_status.append({
                'id': prereq.id,
                'name': prereq.name,
                'completed': is_completed
            })
            
            if not is_completed:
                all_met = False
        
        return all_met, prereq_status
    
    @staticmethod
    def get_available_tech_trees(user):
        """
        Get tech trees that are available to a user based on their prerequisites.
        
        Args:
            user: The User object or ID
            
        Returns:
            List[Dict]: Available tech trees with status info
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        # Get all tech trees
        all_trees = TechTree.objects.all()
        
        # Get user progress for all trees
        user_progress = {
            p.tech_tree_id: p 
            for p in UserTechTreeProgress.objects.filter(user=user)
        }
        
        available_trees = []
        
        for tree in all_trees:
            # Check if user has progress for this tree
            progress = user_progress.get(tree.id)
            
            # Check prerequisites
            prereqs_met, prereq_status = TechTreeService.check_prerequisites(user, tree)
            
            # Build status info
            tree_info = {
                'id': tree.id,
                'name': tree.name,
                'description': tree.description,
                'available': prereqs_met,
                'completed': progress and progress.progress_percentage >= 100 if progress else False,
                'percent_complete': progress.progress_percentage if progress else 0,
                'prerequisites': prereq_status,
                'arts_count': tree.arts.count(),
                'has_achievement_bonus': bool(tree.achievement_bonus)
            }
            
            available_trees.append(tree_info)
        
        return available_trees
    
    @staticmethod
    def get_tech_tree_by_levels(user):
        """
        Get tech trees organized by levels for display in a tech tree visualization.
        
        Args:
            user: The User object or ID
            
        Returns:
            List[Dict]: Tech trees organized by levels with status information
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        # Get all tech trees
        all_trees = TechTree.objects.all().prefetch_related('parent_nodes')
        
        # Get user progress for all trees
        user_progress = {
            p.tech_tree_id: p 
            for p in UserTechTreeProgress.objects.filter(user=user)
        }
        
        # Build a directed graph of tech trees based on prerequisites
        tree_graph = {}
        for tree in all_trees:
            tree_graph[tree.id] = {
                'id': tree.id,
                'name': tree.name,
                'description': tree.description,
                'prerequisites': [p.id for p in tree.parent_nodes.all()],
                'completed': user_progress.get(tree.id) is not None and user_progress[tree.id].is_unlocked,
                'percent_complete': user_progress.get(tree.id) and user_progress[tree.id].progress_percentage or 0,
                'children': []
            }
        
        # Populate children lists based on prerequisites
        for tree_id, tree_info in tree_graph.items():
            for prereq_id in tree_info['prerequisites']:
                if prereq_id in tree_graph:
                    tree_graph[prereq_id]['children'].append(tree_id)
        
        # Arrange trees into levels (BFS traversal)
        levels = []
        visited = set()
        
        # First level: trees with no prerequisites
        current_level = [
            tree_id for tree_id, tree_info in tree_graph.items() 
            if not tree_info['prerequisites']
        ]
        
        level_counter = 1
        
        while current_level:
            level_trees = []
            next_level = []
            
            for tree_id in current_level:
                if tree_id in visited:
                    continue
                    
                visited.add(tree_id)
                tree_info = tree_graph[tree_id]
                
                # Check if prerequisites are met for availability
                prereqs_met = all(prereq_id in visited for prereq_id in tree_info['prerequisites'])
                
                # Add this tree to the current level
                level_trees.append({
                    'id': tree_info['id'],
                    'name': tree_info['name'],
                    'description': tree_info['description'],
                    'completed': tree_info['completed'],
                    'percent_complete': tree_info['percent_complete'],
                    'prerequisites': tree_info['prerequisites'],
                    'available': prereqs_met
                })
                
                # Add children to the next level
                next_level.extend(tree_info['children'])
            
            if level_trees:
                levels.append({
                    'level': level_counter,
                    'nodes': level_trees
                })
                level_counter += 1
            
            current_level = next_level
        
        return levels
    
    @staticmethod
    def get_tech_tree_stats(user):
        """
        Get statistics about a user's tech tree progress.
        
        Args:
            user: The User object or ID
            
        Returns:
            Dict: Statistics about tech tree progress
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        # Get all tech trees
        total_trees = TechTree.objects.count()
        
        # Get user progress
        progress_entries = UserTechTreeProgress.objects.filter(user=user)
        completed_trees = progress_entries.filter(is_unlocked=True).count()
        
        # Calculate total progress using progress_percentage
        total_progress = sum(entry.progress_percentage for entry in progress_entries)
        
        avg_progress = total_progress / total_trees if total_trees > 0 else 0
        
        return {
            'total_trees': total_trees,
            'completed_trees': completed_trees,
            'in_progress_trees': progress_entries.count() - completed_trees,
            'overall_progress': avg_progress,
            'completion_percentage': (completed_trees / total_trees * 100) if total_trees > 0 else 0,
            'completed_nodes': completed_trees,  # Alias for completed_trees for template compatibility
            'unlocked_nodes': progress_entries.count()  # Total unlocked nodes is the count of all progress entries
        }
    
    @staticmethod
    def get_recommended_tech_trees(user, count=3):
        """
        Get recommended tech trees for a user based on their progress and prerequisites.
        
        Args:
            user: The User object or ID
            count: Number of recommendations to return
            
        Returns:
            List[Dict]: Recommended tech trees with status info
        """
        available_trees = TechTreeService.get_available_tech_trees(user)
        
        # Filter to trees that are available but not completed
        recommendations = [
            tree for tree in available_trees 
            if tree['available'] and not tree['completed']
        ]
        
        # Sort by percent complete (descending) to recommend trees they've already started
        recommendations.sort(key=lambda x: x['percent_complete'], reverse=True)
        
        return recommendations[:count]
        
    @staticmethod
    def is_tech_tree_unlocked(user, tech_tree):
        """
        Check if a tech tree is unlocked for a specific user.
        
        Args:
            user: The User object or ID
            tech_tree: The TechTree object or ID
            
        Returns:
            bool: True if the tech tree is unlocked, False otherwise
        """
        # Check prerequisites
        prereqs_met, _ = TechTreeService.check_prerequisites(user, tech_tree)
        
        # If prerequisites are met, the tech tree is unlocked
        return prereqs_met 