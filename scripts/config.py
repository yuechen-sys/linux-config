#!/usr/bin/env python3
"""
Linux Development Environment Configuration Manager
Automates setup of development tools and configurations across multiple machines.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Add scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from installers.base import BaseInstaller
from installers.oh_my_zsh import OhMyZshInstaller
from installers.claude_code import ClaudeCodeInstaller
from installers.dotfiles import DotfilesInstaller
from utils.logger import setup_logger
from utils.system import SystemInfo


class ConfigManager:
    """Main configuration manager for development environment setup."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = setup_logger(verbose)
        self.system_info = SystemInfo()
        self.installers: Dict[str, BaseInstaller] = {}
        self._register_installers()
    
    def _register_installers(self):
        """Register all available installers."""
        self.installers = {
            'oh-my-zsh': OhMyZshInstaller(self.logger),
            'claude-code': ClaudeCodeInstaller(self.logger),
            'dotfiles': DotfilesInstaller(self.logger),
        }
    
    def list_components(self):
        """List all available components for installation."""
        print("Available components:")
        for name, installer in self.installers.items():
            status = "✅" if installer.is_installed() else "❌"
            print(f"  {status} {name}: {installer.description}")
    
    def install_component(self, component: str) -> bool:
        """Install a specific component."""
        if component not in self.installers:
            self.logger.error(f"Unknown component: {component}")
            return False
        
        installer = self.installers[component]
        self.logger.info(f"Installing {component}...")
        
        try:
            if installer.is_installed():
                self.logger.info(f"{component} is already installed")
                return True
            
            return installer.install()
        except Exception as e:
            self.logger.error(f"Failed to install {component}: {e}")
            return False
    
    def install_all(self) -> bool:
        """Install all components in the correct order."""
        # Installation order matters due to dependencies
        install_order = ['oh-my-zsh', 'claude-code', 'dotfiles']
        
        success = True
        for component in install_order:
            if not self.install_component(component):
                success = False
                if not self._confirm_continue(f"Failed to install {component}"):
                    break
        
        return success
    
    def update_component(self, component: str) -> bool:
        """Update a specific component."""
        if component not in self.installers:
            self.logger.error(f"Unknown component: {component}")
            return False
        
        installer = self.installers[component]
        self.logger.info(f"Updating {component}...")
        
        try:
            return installer.update()
        except Exception as e:
            self.logger.error(f"Failed to update {component}: {e}")
            return False
    
    def uninstall_component(self, component: str) -> bool:
        """Uninstall a specific component."""
        if component not in self.installers:
            self.logger.error(f"Unknown component: {component}")
            return False
        
        installer = self.installers[component]
        self.logger.info(f"Uninstalling {component}...")
        
        try:
            return installer.uninstall()
        except Exception as e:
            self.logger.error(f"Failed to uninstall {component}: {e}")
            return False
    
    def _confirm_continue(self, message: str) -> bool:
        """Ask user for confirmation to continue."""
        response = input(f"{message}. Continue? (y/N): ").lower()
        return response in ('y', 'yes')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Linux Development Environment Configuration Manager"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all components')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install components')
    install_parser.add_argument(
        'component',
        nargs='?',
        help='Component to install (or "all" for everything)'
    )
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update components')
    update_parser.add_argument('component', help='Component to update')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall components')
    uninstall_parser.add_argument('component', help='Component to uninstall')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = ConfigManager(verbose=args.verbose)
    
    try:
        if args.command == 'list':
            manager.list_components()
            return 0
        
        elif args.command == 'install':
            if not args.component or args.component == 'all':
                success = manager.install_all()
            else:
                success = manager.install_component(args.component)
            return 0 if success else 1
        
        elif args.command == 'update':
            success = manager.update_component(args.component)
            return 0 if success else 1
        
        elif args.command == 'uninstall':
            success = manager.uninstall_component(args.component)
            return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())