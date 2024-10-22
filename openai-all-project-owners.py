import requests

# Define the base URL and headers for the API
base_url = "https://api.openai.com/v1/organization"
headers = {
    "Authorization": "$$$ YOUR OPENAI API KEY $$$",
    "Content-Type": "application/json"
}

# Function to get all projects with manual pagination
def get_projects():
    projects = []
    limit = 100  # Fetch the maximum number of projects per request
    after = None

    while True:
        params = {
            "limit": limit,
            "include_archived": False
        }
        if after:
            params["after"] = after

        response = requests.get(f"{base_url}/projects", headers=headers, params=params)
        response.raise_for_status()  # Raise exception if the request failed
        data = response.json()

        # Add retrieved projects to the list
        projects.extend(data['data'])

        # Check if there are more projects to retrieve by manually setting the 'after' cursor
        if len(data['data']) < limit:
            # No more projects to retrieve
            break

        # Manually set the 'after' cursor to the last project ID in the current batch
        after = data['data'][-1]['id']
        print(f"Retrieved {len(projects)} projects so far. Continuing with after={after}...")

    print(f"Total projects retrieved: {len(projects)}")  # Final project count
    return projects

# Function to get project members and filter project owners
def get_project_owners(project_id, project_name):
    owners = []
    after = None
    limit = 100  # Fetch the maximum number of users per request

    print(f"Processing project: {project_name} (ID: {project_id})")  # Debug info
    
    while True:
        params = {
            "limit": limit
        }
        if after:
            params["after"] = after  # Use the cursor to paginate

        response = requests.get(f"{base_url}/projects/{project_id}/users", headers=headers, params=params)
        response.raise_for_status()  # Raise exception if the request failed
        data = response.json()

        # Filter users with role 'owner'
        for user in data['data']:
            if user['role'] == 'owner':
                owners.append(user['email'])

        # Log the 'after' value for pagination
        after = data.get('after')
        print(f"'after' cursor for next user request: {after}")

        if not after:
            break

    return owners

# Main logic to retrieve all projects and collect unique project owners
def main():
    all_owners = set()  # Use a set to avoid duplicates
    projects = get_projects()

    for project in projects:
        project_id = project['id']
        project_name = project['name']
        owners = get_project_owners(project_id, project_name)
        all_owners.update(owners)

    # Print the list of unique owners as a comma-separated string
    print(', '.join(all_owners))

if __name__ == "__main__":
    main()
