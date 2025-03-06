#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Import models
from django.contrib.auth import get_user_model
from core.services.art.tech_tree_service import TechTreeService

# Get user
User = get_user_model()
user = User.objects.get(username='alexander')

# Get tech tree data
tech_tree_data = TechTreeService.get_tech_tree_by_levels(user)

print(f'Tech tree data has {len(tech_tree_data)} elements')

# Analyze the data structure
for level_idx, level_data in enumerate(tech_tree_data):
    print(f'Level {level_idx + 1} data:')
    
    # Check if this is a list of nodes
    if isinstance(level_data, list):
        nodes = level_data
        print(f'  Contains {len(nodes)} nodes')
        
        # Look at first node in each level for details
        if nodes:
            sample_node = nodes[0]
            print(f'  Sample node: {sample_node.get("name", "N/A")}')
            print(f'  - ID: {sample_node.get("id", "N/A")}')
            print(f'  - Completed: {sample_node.get("completed", "N/A")}')
            print(f'  - Available: {sample_node.get("available", "N/A")}')
            print(f'  - Has prereqs: {"prerequisites" in sample_node}')
            
            # If it has prerequisites, print the first one
            if "prerequisites" in sample_node and sample_node["prerequisites"]:
                prereq = sample_node["prerequisites"][0]
                print(f'  - First prerequisite: {prereq.get("name", "N/A")}')
                print(f'  - Prereq completed: {prereq.get("completed", "N/A")}')
    else:
        print(f'  Data type: {type(level_data)}')
        print(f'  Content: {level_data}')

# Check user progress
user_progress = TechTreeService.get_user_progress(user)
print("\nUser Tech Tree Progress:")
for progress in user_progress:
    tree_name = progress.tech_tree.name if progress.tech_tree else "Unknown"
    print(f"Tech Tree: {tree_name}")
    print(f"- Progress: {progress.progress_percentage}%")
    print(f"- Unlocked: {progress.is_unlocked}")
    print(f"- Unlock Date: {progress.unlocked_date}")
    
print("\nDone!") 