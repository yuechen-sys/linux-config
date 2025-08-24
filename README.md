# Linux Development Environment Configuration

🚀 **Automated setup script for development environments across multiple machines**

A comprehensive, Python-based configuration management system that automates the setup of essential development tools, shell environments, and personal configurations. Perfect for quickly setting up new machines or maintaining consistency across multiple development environments.


## 🎯 Quick Start

After cloning this repository:

```bash
# Clone the repository
git clone https://github.com/yuechen-sys/linux-config.git
cd linux-config

# Make the config script executable
chmod +x config

# Install everything with one command
./config install all
```

## Features

### 🚀 Automated Configuration
- **Oh My Zsh**: Shell framework with plugins (syntax highlighting, autosuggestions)
- **Claude Code**: AI-powered CLI tool with MCP plugins
- **Dotfiles**: Symlinked configuration files (.zshrc, .gitconfig, etc.)

### 🔧 Modular Architecture
- **Python-based**: Easy to maintain and extend
- **Component isolation**: Each tool has its own installer module
- **Smart prerequisites**: Checks dependencies and provides installation instructions
- **Backup system**: Automatic backup of existing configurations

### 📦 Prerequisite Checking
- **Environment validation**: Checks for required software before installation
- **Clear instructions**: Provides specific commands for installing missing dependencies
- **Multiple options**: Supports different installation methods (system packages, NVM, etc.)
- **Safe operation**: Won't modify system without proper dependencies

## Prerequisites

Before using this configuration system, make sure you have the required dependencies:

### For Oh My Zsh
```bash
# Ubuntu/Debian
sudo apt install zsh curl git

# CentOS/RHEL/Fedora  
sudo yum install zsh curl git
# or: sudo dnf install zsh curl git

# macOS
brew install zsh curl git
```

### For Claude Code
**Option 1 - Node Version Manager (Recommended):**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc  # or restart terminal
nvm install --lts
nvm use --lts
```

**Option 2 - System Package Manager:**
```bash
# Ubuntu/Debian
sudo apt install nodejs npm

# CentOS/RHEL/Fedora
sudo yum install nodejs npm
# or: sudo dnf install nodejs npm

# macOS
brew install node
```

## Usage

### Basic Commands

```bash
# List all available components and their status
./config list

# Install all components
./config install all

# Install specific component
./config install oh-my-zsh
./config install claude-code
./config install dotfiles

# Update components
./config update claude-code
```

### Advanced Options

```bash
# Verbose output for debugging
./config -v install all

# Check system prerequisites
python3 scripts/utils/system.py

# View dotfiles differences
python3 -c "from scripts.installers.dotfiles import DotfilesInstaller; import logging; d = DotfilesInstaller(logging.getLogger()); d.diff()"
```

## Components

### Oh My Zsh
- Requires: `zsh`, `curl`, `git`
- Sets up Oh My Zsh framework with agnoster theme
- Installs required plugins:
  - `zsh-syntax-highlighting`: Command syntax highlighting
  - `zsh-autosuggestions`: Command autocompletion suggestions
- Provides instructions for setting zsh as default shell
- Handles plugin updates

### Claude Code
- Requires: `node`, `npm` (via NVM or system packages)
- Installs Claude Code CLI globally via npm
- Configures MCP plugins:
  - `context7`: Documentation lookup
  - `grep`: Code search capabilities
  - `spec-workflow-mcp`: Specification workflow management
- Falls back to curl installation if npm fails

### Dotfiles
- Creates symlinks in home directory to configuration files:
  - `.zshrc`: Shell configuration
  - `.gitconfig`: Git configuration
  - `custom-CLAUDE.md`: Claude Code custom instructions
- Creates backups before symlinking
- Keeps configurations synchronized automatically via symlinks

## 📁 Project Structure

```
linux-config/
├── config                     # 🎯 Main executable entry point
├── scripts/                   # 🐍 Python package for configuration management
│   ├── config.py             #     Main configuration manager
│   ├── installers/           #     Component installers
│   │   ├── base.py           #     Base installer class
│   │   ├── oh_my_zsh.py      #     Oh My Zsh installer
│   │   ├── claude_code.py    #     Claude Code installer
│   │   └── dotfiles.py       #     Dotfiles installer
│   └── utils/                #     Utility modules
│       ├── logger.py         #     Logging utilities
│       └── system.py         #     System information
├── configs/                   # 📋 Configuration templates
│   └── default/              #     Default configuration files
│       ├── .zshrc            #     Zsh shell configuration
│       ├── .gitconfig        #     Git configuration
│       └── custom-CLAUDE.md  #     Claude Code instructions
├── .gitignore                # 📝 Git ignore rules
├── LICENSE                   # 📄 MIT License
└── README.md                 # 📚 This file
```

## 🎨 Customization

### Adding Your Own Configurations

1. **Create a personal config directory:**
   ```bash
   mkdir -p configs/personal
   cp configs/default/.zshrc configs/personal/
   # Edit configs/personal/.zshrc with your customizations
   ```

2. **The installer creates symlinks with priority:**
   ```bash
   # Priority order:
   # 1. configs/personal/ (your customizations)
   # 2. configs/default/ (fallback defaults)
   # All changes to source files are immediately reflected via symlinks
   ```

## System Requirements

- **Linux or macOS**: Primary support for Linux distributions, macOS compatibility
- **Python 3.6+**: For running the configuration scripts
- **Internet connection**: For downloading tools and dependencies
- **Basic tools**: `curl`, `git` (auto-installed if missing on most systems)

## Supported Systems

- **Ubuntu/Debian**: Full support with apt package manager
- **CentOS/RHEL/Fedora**: Support via yum/dnf package managers
- **Arch Linux**: Support via pacman
- **macOS**: Support via Homebrew
- **WSL**: Full support for Windows Subsystem for Linux

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure the config script is executable: `chmod +x config`
2. **Prerequisites not met**: Install required dependencies as shown in the Prerequisites section
3. **Command not found**: Check if required tools are in PATH:
   ```bash
   # Check if tools are available
   which zsh node npm claude
   
   # For NVM users, make sure to source the environment
   source ~/.bashrc  # or restart terminal
   ```
4. **Network issues**: Verify internet connection for downloading components

### Logs and Debugging

```bash
# Enable verbose logging
./config -v install all

# Check log files
ls ~/.local/share/config-manager/

# View system information
python3 scripts/utils/system.py
```

### Manual Recovery

If something goes wrong, backups are stored in `~/.config-backups/` with timestamps.

```bash
# List available backups
ls ~/.config-backups/

# Restore a specific backup
cp ~/.config-backups/.zshrc.backup_20240324_120000 ~/.zshrc
```

## Development

### Adding New Components

1. Create new installer in `scripts/installers/`
2. Inherit from `BaseInstaller`
3. Implement required methods: `is_installed()`, `install()`
4. Register in `scripts/config.py`

### Testing

```bash
# Test individual components
python3 -c "from scripts.installers.oh_my_zsh import OhMyZshInstaller; import logging; o = OhMyZshInstaller(logging.getLogger()); print(o.is_installed())"
```

## License

MIT License