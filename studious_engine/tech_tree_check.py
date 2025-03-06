#!/usr/bin/env python
import os
import sys
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Import necessary components
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

# Import the view function
from core.views.art import TechTreeView

# Get user
User = get_user_model()
user = User.objects.get(username='alexander')
print(f"User: {user.username}, is_authenticated: {user.is_authenticated}")

# Create a request factory
factory = RequestFactory()

# Create a request object
request = factory.get('/game/tech-tree/')

# Add session and auth to request
middleware = SessionMiddleware(lambda req: None)
middleware.process_request(request)
request.session.save()

# Process the request through auth middleware
auth_middleware = AuthenticationMiddleware(lambda req: None)
auth_middleware.process_request(request)

# Set the user on the request
request.user = user

# Process the request through message middleware
message_middleware = MessageMiddleware(lambda req: None)
message_middleware.process_request(request)

# Call the view
view = TechTreeView.as_view()
response = view(request)

# Check if the view rendered successfully
print(f"Response status code: {response.status_code}")

# Check if tech tree data is in the context
if hasattr(response, 'context_data'):
    context = response.context_data
    print("Context keys:", context.keys())
    
    if 'tech_tree_levels' in context:
        tech_tree_levels = context['tech_tree_levels']
        print(f"Tech tree levels: {len(tech_tree_levels)} items")
        
        # Output the first level
        if tech_tree_levels:
            level = tech_tree_levels[0]
            print(f"Level {level.get('level')}: {len(level.get('nodes', []))} nodes")
            
            # Output the first node
            if level.get('nodes'):
                node = level['nodes'][0]
                print(f"Sample node: {node.get('name')}")
                print(f"- Completed: {node.get('completed')}")
                print(f"- Available: {node.get('available')}")
                print(f"- Has prereqs: {'prerequisites' in node}")
                
                # Save the data to a file
                with open('tech_tree_data.json', 'w') as f:
                    json.dump(tech_tree_levels, f, indent=2, default=str)
                print("Tech tree data saved to tech_tree_data.json")
    else:
        print("No tech_tree_levels in context!")
        
    # Check for other data
    if 'tech_tree_stats' in context:
        stats = context['tech_tree_stats']
        print(f"Tech tree stats: {stats}")
else:
    print("No context data available in response!")
    
print("Done!") 