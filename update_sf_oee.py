import json
import requests
import base64
import os

# Load configuration
with open("repos.json", "r") as f:
    repos = json.load(f)

github_token = os.environ.get("GITHUB_TOKEN")

def safe_file_update(repo_name, target_file_path, new_content):
    """
    Safely update a file in a GitHub repository.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        target_file_path (str): Path to the file in the repository
        new_content (str): New content for the file
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get current file to get SHA
    get_url = f"https://api.github.com/repos/{repo_name}/contents/{target_file_path}"
    
    try:
        get_response = requests.get(get_url, headers=headers)
        
        if get_response.status_code == 200:
            current_file = get_response.json()
            file_sha = current_file["sha"]
            
            # Encode new content
            encoded_content = base64.b64encode(new_content.encode()).decode()
            
            # Update file
            update_data = {
                "message": f"Update {target_file_path} via Control Tower",
                "content": encoded_content,
                "sha": file_sha
            }
            
            put_response = requests.put(get_url, json=update_data, headers=headers)
            
            if put_response.status_code == 200:
                print(f"✅ Successfully updated {target_file_path}")
                return True
            else:
                print(f"❌ Failed to update {target_file_path}: {put_response.status_code}")
                print(f"Response: {put_response.text}")
                return False
        else:
            print(f"❌ Could not find file {target_file_path}")
            print(f"Response: {get_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {target_file_path}: {str(e)}")
        return False

# Update SF OEE and OLE tasks.csv
print("🔄 Updating SF OEE and OLE tasks.csv...")

# Read the new content
with open("temp_sf_oee_update.csv", "r") as f:
    new_content = f.read()

# Update the file
repo_name = "jfleming963/contract_projects"
target_path = "projects/Safran/1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training/SF_OEE_and_OLE/tasks.csv"

success = safe_file_update(repo_name, target_path, new_content)

if success:
    print("✅ SF OEE and OLE tasks.csv update completed successfully!")
else:
    print("❌ SF OEE and OLE tasks.csv update failed!")

# Clean up temp file
os.remove("temp_sf_oee_update.csv")
