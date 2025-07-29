import requests
import base64
import json
import os

def update_github_file(repo, path, content, commit_message, token, branch="main"):
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Get the SHA of the existing file (if it exists)
    r = requests.get(api_url, headers=headers, params={"ref": branch})
    if r.status_code == 200:
        sha = r.json()["sha"]
    else:
        sha = None
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
    else:
        print(f"Failed to update file: {response.status_code} {response.text}")

if __name__ == "__main__":
    # Example usage
    # Set your GitHub token here or use an environment variable
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or "YOUR_GITHUB_TOKEN_HERE"
    # Example values (replace as needed)
    repo = "James-M-Fleming-985/contract_projects"
    path = "ZnNi line Stabilization/table 1/task.csv"
    with open("contract_projects/line stabilization critical documentation and training/table 1/task.csv", "r") as f:
        content = f.read()
    commit_message = "Update task.csv from control tower"
    update_github_file(repo, path, content, commit_message, GITHUB_TOKEN)
