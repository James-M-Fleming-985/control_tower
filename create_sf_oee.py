import json
import requests
import base64
import os

# Load configuration
with open("repos.json", "r") as f:
    repos = json.load(f)

github_token = os.environ.get("GITHUB_TOKEN")

def create_file_in_repo(repo_name, file_path, content):
    """
    Create a new file in a GitHub repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        file_path (str): Path to the file in the repository
        content (str): Content for the file
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Encode content
    encoded_content = base64.b64encode(content.encode()).decode()
    
    # Create file
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    
    data = {
        "message": f"Create {file_path} via Control Tower",
        "content": encoded_content
    }
    
    try:
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ Successfully created {file_path}")
            return True
        else:
            print(f"❌ Failed to create {file_path}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {file_path}: {str(e)}")
        return False

# Create SF OEE and OLE tasks.csv
print("🔄 Creating SF OEE and OLE tasks.csv...")

# Read the new content
with open("temp_sf_oee_update.csv", "r") as f:
    new_content = f.read()

# Create the file
repo_name = "jfleming963/contract_projects"
target_path = "projects/Safran/1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training/SF_OEE_and_OLE/tasks.csv"

success = create_file_in_repo(repo_name, target_path, new_content)

if success:
    print("✅ SF OEE and OLE tasks.csv created successfully!")
else:
    print("❌ SF OEE and OLE tasks.csv creation failed!")

# Clean up temp file
os.remove("temp_sf_oee_update.csv")
