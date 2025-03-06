import requests
from bs4 import BeautifulSoup

# Create a session to maintain cookies
session = requests.Session()

# Get the login page to get the CSRF token
login_url = 'http://localhost:8080/accounts/login/'
login_response = session.get(login_url)
login_soup = BeautifulSoup(login_response.text, 'html.parser')

# Extract the CSRF token
csrf_token = login_soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
print(f"CSRF Token: {csrf_token}")

# Log in with the credentials
login_data = {
    'csrfmiddlewaretoken': csrf_token,
    'username': 'alexander',
    'password': 'testpassword',
    'next': '/game/tech-tree/'
}

login_post_response = session.post(login_url, data=login_data, headers={
    'Referer': login_url
})

print(f"Login Status Code: {login_post_response.status_code}")
print(f"Login URL: {login_post_response.url}")

# If login was successful and redirected to tech tree, we're already there
# Otherwise, explicitly navigate to tech tree
if '/game/tech-tree/' not in login_post_response.url:
    tech_tree_url = 'http://localhost:8080/game/tech-tree/'
    tech_tree_response = session.get(tech_tree_url)
    print(f"Tech Tree Status Code: {tech_tree_response.status_code}")
    print(f"Tech Tree URL: {tech_tree_response.url}")
    
    # Parse the tech tree HTML
    tech_tree_soup = BeautifulSoup(tech_tree_response.text, 'html.parser')
    
    # Check if we have the tech tree visualization element
    tech_tree_viz = tech_tree_soup.find(id='tech-tree-visualization')
    if tech_tree_viz:
        print("Tech Tree Visualization Found!")
    else:
        print("Tech Tree Visualization Not Found!")
    
    # Check if we have nodes in the list view
    tech_tree_nodes_list = tech_tree_soup.find(id='tech-tree-list-view')
    if tech_tree_nodes_list:
        print("Tech Tree List View Found!")
        nodes = tech_tree_nodes_list.find_all('div', class_='node-card')
        print(f"Number of nodes in list: {len(nodes)}")
        
        # Check node statuses
        completed_nodes = tech_tree_nodes_list.find_all('div', class_='node-completed')
        available_nodes = tech_tree_nodes_list.find_all('div', class_='node-available')
        locked_nodes = tech_tree_nodes_list.find_all('div', class_='node-locked')
        
        print(f"Completed nodes: {len(completed_nodes)}")
        print(f"Available nodes: {len(available_nodes)}")
        print(f"Locked nodes: {len(locked_nodes)}")
    else:
        print("Tech Tree List View Not Found!") 