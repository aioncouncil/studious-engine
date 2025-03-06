#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Import Django test client
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Get the user and make sure it has a valid password
User = get_user_model()
user = User.objects.get(username='alexander')

# Set a known password if not already set
if not user.check_password('testpassword'):
    user.set_password('testpassword')
    user.save()
    print("Password set for alexander")
else:
    print("Password already set for alexander")

# Create a client and log in
client = Client()
login_success = client.login(username='alexander', password='testpassword')
print(f"Login successful: {login_success}")

if login_success:
    # Get the tech tree page
    tech_tree_url = reverse('core:tech_tree')  
    response = client.get(tech_tree_url)
    
    print(f"Tech Tree Status Code: {response.status_code}")
    
    # Check for error messages
    if response.status_code != 200:
        print(f"Error: {response.context.get('error', 'Unknown error')}")
    else:
        print("Successfully accessed tech tree page!")
        
        # Check if tech tree visualization is present
        if "tech-tree-visualization" in response.content.decode('utf-8'):
            print("Tech Tree Visualization Found in HTML!")
        else:
            print("Tech Tree Visualization NOT Found in HTML!")
            
        # Check if tech tree data is being passed to the template
        if "tech-tree-data" in response.content.decode('utf-8'):
            print("Tech Tree Data Found in HTML!")
        else:
            print("Tech Tree Data NOT Found in HTML!")
            
        # Write the HTML to a file for inspection
        with open('tech_tree_page.html', 'w') as f:
            f.write(response.content.decode('utf-8'))
        print("HTML written to tech_tree_page.html for inspection")
else:
    print("Could not log in. Check user credentials.") 