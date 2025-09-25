# Control Tower Dev Container Configuration

This dev container is specifically designed for the **Control Tower Multi-Repository Management Pattern**, where you code from the control tower and push to multiple target repositories under your account.

## 🏗️ Container Features

### Core Environment
- **Python 3.12** with full development tools
- **Git** with advanced multi-repo support
- **GitHub CLI** for seamless repo management
- **Node.js LTS** for web-based tooling
- **Docker-in-Docker** for containerized deployments

### Development Tools
- **VS Code Extensions**: Python, PyTest, GitHub integration, GitLens, Copilot
- **Python Tools**: pytest, black, flake8, pylint, coverage
- **Multi-Repo Utilities**: Custom scripts and aliases

## 🔧 Multi-Repo Management Features

### Environment Variables
- `CONTROL_TOWER_MODE=true` - Identifies this as control tower workspace
- `MULTI_REPO_WORKSPACE=/workspaces/control_tower` - Root workspace path
- `PYTHONPATH` - Configured for control tower module imports

### Custom Aliases
```bash
ct-status      # Show control tower git status
ct-repos       # List managed repositories  
ct-sync        # Sync all repositories
ct-test        # Run TDD tests
ct-clean       # Clean Python cache files
tdd-red        # Run failing tests (RED phase)
tdd-green      # Open implementation (GREEN phase)  
tdd-refactor   # Code quality tools (REFACTOR phase)
```

### Management Scripts
- `manage_repos.sh` - Clone, sync, and push to target repositories
- `control_tower_status.py` - Dashboard showing all repo statuses

## 🚀 Quick Start

After container creation:

1. **Authenticate with GitHub:**
   ```bash
   gh auth login --web
   ```

2. **Configure Git (if needed):**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

3. **View status dashboard:**
   ```bash
   python3 control_tower_status.py
   ```

4. **Clone target repositories:**
   ```bash
   ./manage_repos.sh clone https://github.com/yourusername/target-repo.git
   ```

## 📁 Directory Structure

```
/workspaces/control_tower/
├── .devcontainer/          # Dev container configuration
├── repos/                  # Cloned target repositories
├── projects/               # TDD project hierarchy
├── src/                    # Control tower source code
├── tests/                  # Test suites
├── Prompts/                # TDD prompts and workflows
├── temp_clones/            # Temporary repo clones
├── sync_status/            # Repository sync tracking
└── deployment_targets/     # Deployment configurations
```

## 🔄 Workflow Pattern

1. **Code in Control Tower** - Develop features in the centralized workspace
2. **Test with TDD** - Use streamlined test suites for rapid development  
3. **Push to Targets** - Deploy code to specific target repositories
4. **Manage Multiple Repos** - Coordinate changes across your repository portfolio

## 🛠️ Troubleshooting

### Recovery Mode Issues
- This configuration should prevent recovery mode problems
- All dependencies are explicitly declared
- Post-create script handles environment setup

### Multi-Repo Sync Issues
- Use `ct-sync` alias to fetch from all remotes
- Check `./manage_repos.sh status` for repository states
- Verify GitHub CLI authentication with `gh auth status`

### Python/Testing Issues  
- Use `ct-test` for TDD workflow testing
- Run `ct-clean` to clear Python cache
- Check PYTHONPATH with `echo $PYTHONPATH`

## 📊 Ports

- **8080** - TDD Mobile API server
- **3000** - Web UI development
- **5000** - Flask development server
- **8000** - Python HTTP server

## 🔐 Security

- GitHub CLI authentication required for repo access
- SSH keys automatically mounted from host
- Docker socket mounted for containerized workflows
- Environment variables isolated to container

---

**This dev container transforms your codespace into a powerful multi-repository development hub while maintaining the TDD workflow capabilities of your Control Tower system.**