import json
import requests
import os

# Load configuration
with open("repos.json", "r") as f:
    repos = json.load(f)

github_token = os.environ.get("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

# Check what's in the SF_OEE_and_OLE directory
repo_name = "jfleming963/contract_projects"
directory_path = "projects/Safran/1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training/SF_OEE_and_OLE"

url = f"https://api.github.com/repos/{repo_name}/contents/{directory_path}"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    contents = response.json()
    print(f"Contents of {directory_path}:")
    for item in contents:
        print(f"  {item['type']}: {item['name']}")
else:
    print(f"Could not access directory: {response.status_code}")
    print(f"Response: {response.text}")
