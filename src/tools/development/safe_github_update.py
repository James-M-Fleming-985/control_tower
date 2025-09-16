import requests
import base64
import json
import os

def search_files_in_repo(repo, filename, token):
    """Search for files with the given name in the repository"""
    api_url = f"https://api.github.com/search/code?q={filename}+in:file+repo:{repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])
    return []

def get_repo_contents(repo, path, token):
    """Get contents of a directory in the repository"""
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def update_github_file(repo, path, content, commit_message, token, branch="main"):
    """Update a file in GitHub repository"""
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get the SHA of the existing file (if it exists)
    r = requests.get(api_url, headers=headers, params={"ref": branch})
    if r.status_code == 200:
        sha = r.json()["sha"]
        print(f"Found existing file at: {path}")
    else:
        sha = None
        print(f"Creating new file at: {path}")
    
    data = {
        "message": commit_message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch
    }
    if sha:
        data["sha"] = sha
    
    response = requests.put(api_url, headers=headers, data=json.dumps(data))
    if response.status_code in [200, 201]:
        print(f"File '{path}' updated successfully in repo '{repo}'.")
        return True
    else:
        print(f"Failed to update file: {response.status_code} {response.text}")
        return False

def safe_file_update(repo, target_path, filename, content, commit_message, token):
    """Safely update a file, searching for existing matches first"""
    
    # First, try the exact path
    exact_path_result = get_repo_contents(repo, target_path, token)
    if exact_path_result is not None:
        print(f"Found exact path: {target_path}")
        full_path = f"{target_path}/{filename}" if not target_path.endswith(filename) else target_path
        return update_github_file(repo, full_path, content, commit_message, token)
    
    # Search for existing files with the same name
    print(f"Exact path '{target_path}' not found. Searching for existing '{filename}' files...")
    existing_files = search_files_in_repo(repo, filename, token)
    
    if existing_files:
        print(f"Found {len(existing_files)} existing '{filename}' file(s):")
        for i, file in enumerate(existing_files):
            print(f"  {i+1}. {file['path']}")
        
        print("\nWARNING: Multiple files found. Please specify the exact path to avoid creating duplicates.")
        print(f"Suggested exact paths:")
        for file in existing_files:
            print(f"  - {file['path']}")
        return False
    
    # No existing files found
    print(f"No existing '{filename}' files found in repository '{repo}'.")
    print(f"Would create new file at: {target_path}/{filename}")
    print("WARNING: This will create a new directory structure.")
    print("Please confirm the exact path or update an existing file instead.")
    return False

if __name__ == "__main__":
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or "YOUR_GITHUB_TOKEN_HERE"
    
    # Configuration
    repo = "James-M-Fleming-985/contract_projects"
    target_path = "line stabilization critical documentation and training/table 1"
    filename = "task.csv"
    
    with open("contract_projects/line stabilization critical documentation and training/table 1/task.csv", "r") as f:
        content = f.read()
    
    commit_message = "Update task.csv from control tower"
    
    # Use safe update
    safe_file_update(repo, target_path, filename, content, commit_message, GITHUB_TOKEN)
