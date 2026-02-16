#!/bin/bash
# Auto-generate CLAUDE.md with detected tool versions

CLAUDE_MD="/home/vscode/.claude/CLAUDE.md"

# Ensure .claude directory exists
mkdir -p /home/vscode/.claude

# Detect versions
OS_VERSION=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
KERNEL_VERSION=$(uname -r)
ARCH=$(uname -m)

GIT_VERSION=$(git --version 2>/dev/null | awk '{print $3}')
NODE_VERSION=$(node --version 2>/dev/null | sed 's/v//')
NPM_VERSION=$(npm --version 2>/dev/null)
PYTHON_VERSION=$(python --version 2>/dev/null | awk '{print $2}')
PIP_VERSION=$(pip --version 2>/dev/null | awk '{print $2}')
DOCKER_VERSION=$(docker --version 2>/dev/null | awk '{print $3}' | sed 's/,//')
GH_VERSION=$(gh --version 2>/dev/null | head -1 | awk '{print $3}')
JQ_VERSION=$(jq --version 2>/dev/null | sed 's/jq-//')
CLAUDE_VERSION=$(claude --version 2>/dev/null | head -1)
PLAYWRIGHT_VERSION=$(npm list -g playwright 2>/dev/null | grep playwright@ | awk -F@ '{print $2}')

# Generate CLAUDE.md
cat > "$CLAUDE_MD" << 'EOF'
# Devcontainer Environment

## System Information

- **OS**: $OS_VERSION
- **Kernel**: $KERNEL_VERSION
- **Architecture**: $ARCH
- **Environment**: VSCode Devcontainer (Docker-outside-of-Docker enabled)
- **User**: vscode (with sudo access)
- **Home**: /home/vscode
- **Workspace**: /workspace
- **Shell**: /bin/bash

## Development Tools & Versions

### Version Control
- **Git**: $GIT_VERSION

### Node.js Ecosystem
- **Node.js**: v$NODE_VERSION
- **npm**: $NPM_VERSION
- **NODE_PATH**: `/usr/lib/node_modules` (set in .bashrc for global package access)

### Python
- **Python**: $PYTHON_VERSION
- **pip**: $PIP_VERSION

### Containers
- **Docker CLI**: $DOCKER_VERSION (Docker-outside-of-Docker - uses host daemon)
- **Docker Compose**: Available via Docker Compose Plugin

### GitHub
- **GitHub CLI (gh)**: $GH_VERSION

### Utilities
- **jq**: $JQ_VERSION (JSON processor)
- **curl**: Installed
- **wget**: Installed
- **vim**: Installed
- **xdg-utils**: Installed (xdg-open, etc.)
- **build-essential**: Installed (gcc, g++, make)

### Web Automation
- **Playwright**: $PLAYWRIGHT_VERSION (pre-installed globally with stealth plugins)
  - playwright-extra
  - puppeteer-extra-plugin-stealth
  - puppeteer-extra-plugin-user-preferences
  - puppeteer-extra-plugin-user-data-dir
- **Chromium browser**: Pre-installed and cached

### Claude Code
- **Claude Code CLI**: $CLAUDE_VERSION
- **Claude Code Extension**: Installed in VSCode
- **Authentication**: Persisted via ~/.cache/claude mount

## Docker-outside-of-Docker (DooD)

This container has access to the **host's Docker daemon** via the mounted Docker socket at `/var/run/docker.sock`.

**What this means:**
- You can run `docker` commands inside this container
- Containers you create will run on the **host**, not inside this devcontainer
- Docker images and volumes are shared with the host
- This is more efficient than Docker-in-Docker (DinD)

**Important:**
- Built images are visible on the host
- Running containers appear in host's `docker ps`
- Be cautious with `docker system prune` as it affects the host

## X11 Graphics Support

This devcontainer is configured to display graphical applications using WSL's X11 server.

**Configuration:**
- X11 dependencies installed (x11-apps, x11-utils, xauth, etc.)
- DISPLAY environment variable set to connect to host's X server
- Wayland disabled to ensure X11 usage

**Testing X11:**
```bash
# Test with a simple X11 application
xeyes
```

**Requirements:**
- WSL must have an X server running (WSLg on Windows 11, or VcXsrv/X410 on Windows 10)
- If applications don't display, verify DISPLAY variable: `echo $DISPLAY`
- On Windows 11 with WSLg, X11 forwarding should work automatically

**Common X11 Applications:**
- GUI-based browsers (for Playwright headed mode)
- Image viewers
- Any graphical development/debugging tools

## Playwright Browser Profiles

A dedicated Docker volume is mounted for Playwright browser profiles and cache.

**Volume Details:**
- **Volume Name**: `playwright-browsers` (named Docker volume)
- **Mount Point**: `/home/vscode/.cache/ms-playwright`
- **Purpose**: Persist downloaded browser binaries across container rebuilds

**What this means:**
- Playwright browsers (Chromium, Firefox, WebKit) are downloaded once and persisted
- Faster container startup after initial browser installation
- No need to re-download browsers after rebuilding the devcontainer
- Browser profiles and cache survive container recreations

**Managing the volume:**
```bash
# View volume details (from host or container)
docker volume inspect playwright-browsers

# If you need to clear the cache and re-download browsers
docker volume rm playwright-browsers
# Then rebuild the devcontainer
```

**Playwright is Pre-installed:**
Playwright and all dependencies are pre-installed globally. You can use Playwright scripts immediately without installation.

```bash
# Playwright is already available globally with NODE_PATH set in .bashrc
# Just run your scripts directly:
node my-playwright-script.js

# Or use the /playwright skill to generate scripts
/playwright

# For project-specific Playwright installation (optional):
npm install -D playwright

# Additional browsers can be installed if needed:
npx playwright install firefox
npx playwright install webkit
```

## Volume Mounts

- **Project**: `/workspace` ← mounted from host (read-write, cached)
- **Docker Socket**: `/var/run/docker.sock` ← host Docker daemon
- **Claude Cache**: `/home/vscode/.cache/claude` ← persisted authentication
- **Playwright Browsers**: `/home/vscode/.cache/ms-playwright` ← persistent volume `playwright-browsers`

## Claude Code Directory Structure

The `~/.claude/` directory contains symlinks to the claude-monorepo repository:

\`\`\`
~/.claude/
├── skills -> ~/claude-monorepo/claude/skills/
├── commands -> ~/claude-monorepo/claude/commands/
├── hooks -> ~/claude-monorepo/claude/hooks/
└── templates -> ~/claude-monorepo/claude/templates/
\`\`\`

**Repository**: https://github.com/nickweedon/claude-monorepo.git
**Important**: Skills, commands, hooks, and templates are symlinked. Any changes to files in these directories will be reflected in the repository.

## User Permissions

The `vscode` user has:
- Full sudo access (passwordless)
- Access to Docker socket (via group membership)
- Ownership of /workspace and /home/vscode

## Network Configuration

- **Network Mode**: Host network
- Container shares the host's network stack
- Services running in container are accessible on host's localhost

## Best Practices

1. **Git Configuration**: Configure git with your name and email:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **Claude Code**: Already authenticated via cache mount. Use `/` commands normally.

3. **Docker Usage**: Remember that `docker run` creates containers on the host, not inside this devcontainer.

4. **Python Virtual Environments**: Create project-specific venvs:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

5. **Node Packages**: Install packages normally with npm or npx.
   - Global packages are accessible via NODE_PATH (set automatically in .bashrc)
   - Playwright and plugins are pre-installed globally

6. **X11 Applications**: Test X11 with `xeyes` before running complex graphical applications.
   - Use `xdg-open <file>` to open files with default applications

7. **Playwright**: Pre-installed globally with Chromium browser.
   - Use the `/playwright` skill to generate automation scripts
   - Browsers are cached in persistent volume (no re-download on rebuild)
   - Additional browsers (Firefox, WebKit) can be installed on demand

## Environment Notes

- This environment mirrors the Ubuntu 24.04 LTS setup
- All tools are accessible to the vscode user
- The workspace directory is the project root
- Changes to /workspace persist to the host
- Changes outside /workspace (except mounted volumes) are ephemeral
- Playwright browsers are persisted in a named Docker volume
EOF

# Substitute variables
sed -i "s|\$OS_VERSION|$OS_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$KERNEL_VERSION|$KERNEL_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$ARCH|$ARCH|g" "$CLAUDE_MD"
sed -i "s|\$GIT_VERSION|$GIT_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$NODE_VERSION|$NODE_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$NPM_VERSION|$NPM_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$PYTHON_VERSION|$PYTHON_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$PIP_VERSION|$PIP_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$DOCKER_VERSION|$DOCKER_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$GH_VERSION|$GH_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$JQ_VERSION|$JQ_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$CLAUDE_VERSION|$CLAUDE_VERSION|g" "$CLAUDE_MD"
sed -i "s|\$PLAYWRIGHT_VERSION|$PLAYWRIGHT_VERSION|g" "$CLAUDE_MD"

echo "✓ Generated $CLAUDE_MD"
