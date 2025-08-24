# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal Linux configuration repository containing dotfiles and shell configuration. The repository is minimal and focused on core shell setup.

## Repository Structure

- `configs/default/` - Default configuration files for new installations
  - `.gitconfig` - Git configuration with user settings and Oh My Zsh integration
  - `.zshrc` - Zsh shell configuration using Oh My Zsh framework with agnoster theme
  - `custom-CLAUDE.md` - Claude Code custom instructions
- `scripts/` - Python-based configuration management system
  - `config.py` - Main configuration manager
  - `installers/` - Component installers (Oh My Zsh, Claude Code, dotfiles)
  - `utils/` - System utilities and logging
- `config` - Main executable script for environment setup

## Key Configuration Details

### Zsh Configuration
- Uses Oh My Zsh framework with agnoster theme
- Enabled plugins: git, zsh-syntax-highlighting, zsh-autosuggestions
- Supports local machine-specific configuration via `~/.zshrc.local`
- Has untracked files dirty status disabled for performance with large repositories

### Git Configuration
- User: yuechen-sys (yuechen@kaist.ac.kr)
- Oh My Zsh integration enabled with `hide-dirty = 1`

## Configuration Management

### Using the Config System

```bash
# Install all components on new machine
./config install all

# Install individual components
./config install oh-my-zsh    # Shell setup
./config install claude-code  # AI CLI with dependencies
./config install dotfiles     # Deploy configuration files

# Check status
./config list

# Update components
./config update claude-code
```

### Customizing Configurations

- Default configurations are in `configs/default/`
- Create personal customizations in `configs/personal/` (takes priority)
- The dotfiles installer automatically uses personal configs when available

### Development Notes

When modifying configurations:
- Test changes by running `./config install dotfiles` 
- Use `./config -v install [component]` for detailed logging
- Backup files are automatically created in `~/.config-backups/`