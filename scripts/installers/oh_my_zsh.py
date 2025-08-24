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
        return "Oh My Zsh framework with syntax highlighting and autosuggestions"
    
    def is_installed(self) -> bool:
        """Check if Oh My Zsh is installed."""
        return self.oh_my_zsh_dir.exists() and (self.oh_my_zsh_dir / 'oh-my-zsh.sh').exists()
    
    def install(self) -> bool:
        """Install Oh My Zsh and required plugins."""
        try:
            # Install zsh if not present
            if not self.command_exists('zsh'):
                self.logger.info("Installing zsh...")
                self._install_zsh()
            
            # Install Oh My Zsh
            if not self.is_installed():
                self.logger.info("Installing Oh My Zsh...")
                self._install_oh_my_zsh()
            else:
                self.logger.info("Oh My Zsh already installed")
            
            # Install plugins
            self.logger.info("Installing Oh My Zsh plugins...")
            self._install_plugins()
            
            # Set zsh as default shell if not already
            self._set_default_shell()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Oh My Zsh: {e}")
            return False
    
    def _install_zsh(self):
        """Install zsh package."""
        # Try different package managers
        package_managers = [
            ['sudo', 'apt-get', 'update', '&&', 'sudo', 'apt-get', 'install', '-y', 'zsh'],
            ['sudo', 'yum', 'install', '-y', 'zsh'],
            ['sudo', 'dnf', 'install', '-y', 'zsh'],
            ['sudo', 'pacman', '-S', '--noconfirm', 'zsh'],
            ['brew', 'install', 'zsh']
        ]
        
        for cmd in package_managers:
            try:
                self.run_command(cmd, shell=True)
                return
            except:
                continue
        
        raise Exception("Could not install zsh - no supported package manager found")
    
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
    
    def _set_default_shell(self):
        """Set zsh as the default shell if it's not already."""
        try:
            # Check current shell
            current_shell = os.environ.get('SHELL', '')
            if 'zsh' in current_shell:
                self.logger.info("zsh is already the default shell")
                return
            
            # Get zsh path
            result = self.run_command(['which', 'zsh'])
            zsh_path = result.stdout.strip()
            
            # Add zsh to /etc/shells if not present
            try:
                with open('/etc/shells', 'r') as f:
                    shells = f.read()
                if zsh_path not in shells:
                    self.logger.info("Adding zsh to /etc/shells...")
                    self.run_command(['sudo', 'sh', '-c', f'echo {zsh_path} >> /etc/shells'])
            except:
                pass  # Not critical if this fails
            
            # Change default shell
            self.logger.info("Setting zsh as default shell...")
            self.run_command(['chsh', '-s', zsh_path])
            
            self.logger.warning("You need to log out and log back in for the shell change to take effect")
            
        except Exception as e:
            self.logger.warning(f"Could not set zsh as default shell: {e}")
    
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