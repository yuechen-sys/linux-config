"""Oh My Zsh installer with plugin management."""

import os
import shutil
from pathlib import Path
from typing import List
from .base import BaseInstaller


class OhMyZshInstaller(BaseInstaller):
    """Installer for Oh My Zsh and required plugins."""
    
    def __init__(self, logger):
        super().__init__(logger)
        self.oh_my_zsh_dir = self.home / '.oh-my-zsh'
        self.plugins_dir = self.oh_my_zsh_dir / 'custom' / 'plugins'
        
        # Required plugins based on .zshrc configuration
        self.required_plugins = [
            {
                'name': 'zsh-syntax-highlighting',
                'url': 'https://github.com/zsh-users/zsh-syntax-highlighting.git'
            },
            {
                'name': 'zsh-autosuggestions', 
                'url': 'https://github.com/zsh-users/zsh-autosuggestions.git'
            }
        ]
    
    @property
    def description(self) -> str:
        return "Oh My Zsh framework with syntax highlighting and autosuggestions (requires zsh)"
    
    def is_installed(self) -> bool:
        """Check if Oh My Zsh is installed."""
        return self.oh_my_zsh_dir.exists() and (self.oh_my_zsh_dir / 'oh-my-zsh.sh').exists()
    
    def _check_prerequisites(self) -> List[str]:
        """Check prerequisites for Oh My Zsh setup."""
        issues = []
        
        if not self.command_exists('zsh'):
            issues.append("zsh is not installed")
        
        if not self.command_exists('curl') and not self.command_exists('wget'):
            issues.append("Neither curl nor wget is available for downloading")
        
        if not self.command_exists('git'):
            issues.append("git is not installed")
        
        return issues
    
    def install(self) -> bool:
        """Install Oh My Zsh and required plugins."""
        try:
            # Check prerequisites first
            issues = self._check_prerequisites()
            if issues:
                self.logger.error("Prerequisites not met:")
                for issue in issues:
                    self.logger.error(f"  - {issue}")
                self.logger.info("Please install missing dependencies first:")
                self.logger.info("  Ubuntu/Debian: sudo apt install zsh curl git")
                self.logger.info("  CentOS/RHEL:   sudo yum install zsh curl git")
                self.logger.info("  macOS:         brew install zsh curl git")
                return False
            
            # Install Oh My Zsh
            if not self.is_installed():
                self.logger.info("Installing Oh My Zsh...")
                self._install_oh_my_zsh()
            else:
                self.logger.info("Oh My Zsh already installed")
            
            # Install plugins
            self.logger.info("Installing Oh My Zsh plugins...")
            self._install_plugins()
            
            # Suggest setting zsh as default shell
            self._suggest_default_shell()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Oh My Zsh: {e}")
            return False
    
    
    def _install_oh_my_zsh(self):
        """Install Oh My Zsh framework."""
        install_script_url = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
        
        # Download and run the installer with non-interactive mode
        cmd = f'sh -c "$(curl -fsSL {install_script_url})" "" --unattended'
        self.run_command([cmd], shell=True)
        
        if not self.is_installed():
            raise Exception("Oh My Zsh installation failed")
    
    def _install_plugins(self):
        """Install required Oh My Zsh plugins."""
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        for plugin in self.required_plugins:
            plugin_path = self.plugins_dir / plugin['name']
            
            if plugin_path.exists():
                self.logger.info(f"Plugin {plugin['name']} already installed, updating...")
                self.run_command(['git', 'pull'], cwd=plugin_path)
            else:
                self.logger.info(f"Installing plugin {plugin['name']}...")
                self.run_command([
                    'git', 'clone', plugin['url'], str(plugin_path)
                ])
    
    def _suggest_default_shell(self):
        """Suggest setting zsh as the default shell if it's not already."""
        try:
            # Check current shell
            current_shell = os.environ.get('SHELL', '')
            if 'zsh' in current_shell:
                self.logger.info("zsh is already the default shell")
                return
            
            # Get zsh path
            result = self.run_command(['which', 'zsh'])
            zsh_path = result.stdout.strip()
            
            self.logger.info("To set zsh as your default shell, run:")
            self.logger.info(f"  chsh -s {zsh_path}")
            self.logger.info("Then log out and log back in for the change to take effect")
            
        except Exception as e:
            self.logger.info("To set zsh as default shell:")
            self.logger.info("  chsh -s $(which zsh)")
            self.logger.info("Then log out and log back in")
    
    def update(self) -> bool:
        """Update Oh My Zsh and plugins."""
        try:
            if self.is_installed():
                self.logger.info("Updating Oh My Zsh...")
                # Update Oh My Zsh itself
                self.run_command(['git', 'pull'], cwd=self.oh_my_zsh_dir)
                
                # Update plugins
                self._install_plugins()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update Oh My Zsh: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall Oh My Zsh."""
        try:
            if self.oh_my_zsh_dir.exists():
                self.logger.info("Removing Oh My Zsh directory...")
                shutil.rmtree(self.oh_my_zsh_dir)
            
            # Try to restore original shell
            try:
                self.run_command(['chsh', '-s', '/bin/bash'])
            except:
                pass
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to uninstall Oh My Zsh: {e}")
            return False