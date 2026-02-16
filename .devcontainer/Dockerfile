FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set up locales to avoid locale warnings
RUN apt-get update && apt-get install -y locales && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    git \
    curl \
    wget \
    ca-certificates \
    gnupg \
    lsb-release \
    sudo \
    vim \
    nano \
    # JSON processing
    jq \
    # Network tools
    iputils-ping \
    net-tools \
    # Process tools
    procps \
    # X11 dependencies for graphical applications
    x11-apps \
    x11-utils \
    xauth \
    xvfb \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    # Required for Claude Code
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libgbm1 \
    libasound2t64 \
    # Additional libraries for Playwright browsers
    libglib2.0-0 \
    libnotify4 \
    libsecret-1-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    # xdg-utils for xdg-open and other utilities
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for Docker-outside-of-Docker)
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 22 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.12
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3.12 /usr/bin/python && \
    ln -sf /usr/bin/python3.12 /usr/bin/python3

# Install Playwright and dependencies globally (for /playwright skill)
# This makes Playwright available system-wide and avoids redundant installations
RUN npm install -g \
    playwright \
    playwright-extra \
    puppeteer-extra-plugin-stealth \
    puppeteer-extra-plugin-user-preferences \
    puppeteer-extra-plugin-user-data-dir

# Install markdownlint CLI globally for linting markdown files
RUN npm install -g markdownlint-cli2

# Create docker group and vscode user with UID 1000 to match host user
# Remove ubuntu user if it exists (typically has UID 1000)
RUN groupadd docker && \
    (userdel -r ubuntu 2>/dev/null || true) && \
    useradd -m -s /bin/bash -u 1000 -G sudo,docker vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to vscode user
USER vscode
WORKDIR /home/vscode

# Install Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | bash

# Ensure Claude Code is in PATH
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Create .claude directory and symlinks for claude-monorepo
RUN mkdir -p /home/vscode/.claude && \
    ln -sf /home/vscode/claude-monorepo/claude/skills /home/vscode/.claude/skills && \
    ln -sf /home/vscode/claude-monorepo/claude/commands /home/vscode/.claude/commands && \
    ln -sf /home/vscode/claude-monorepo/claude/hooks /home/vscode/.claude/hooks && \
    ln -sf /home/vscode/claude-monorepo/claude/templates /home/vscode/.claude/templates

# Copy minimal Claude Code state file with userID and workspace trust
# This allows Claude CLI to skip the trust dialog for /workspace
COPY --chown=vscode:vscode claude.json /home/vscode/.claude.json
RUN chmod 600 /home/vscode/.claude.json

# Copy Claude settings (model preference, etc.)
COPY --chown=vscode:vscode claude-settings.json /home/vscode/.claude/settings.json
RUN chmod 644 /home/vscode/.claude/settings.json

# Set up bash aliases for vscode user
RUN echo 'alias claude="claude --dangerously-skip-permissions"' >> /home/vscode/.bash_aliases && \
    chown vscode:vscode /home/vscode/.bash_aliases

# Set up NODE_PATH for globally installed npm packages
RUN echo 'export NODE_PATH=/usr/lib/node_modules' >> /home/vscode/.bashrc && \
    chown vscode:vscode /home/vscode/.bashrc

# Create Playwright cache directory (will be mounted as volume)
RUN mkdir -p /home/vscode/.cache/ms-playwright

# Install Playwright browser binaries (Chromium by default)
# Browsers are stored in the persistent playwright-browsers volume
RUN npx playwright install chromium --with-deps

# Generate CLAUDE.md during build to avoid race condition with VSCode extension
COPY generate-claude-md.sh /tmp/generate-claude-md.sh
RUN bash /tmp/generate-claude-md.sh

# Set up workspace directory
RUN sudo mkdir -p /workspace && sudo chown vscode:vscode /workspace

WORKDIR /workspace

# Reset DEBIAN_FRONTEND
ENV DEBIAN_FRONTEND=

CMD ["/bin/bash"]
