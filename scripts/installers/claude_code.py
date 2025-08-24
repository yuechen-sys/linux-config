"""Claude Code installer with MCP setup (requires Node.js/npm)."""

import json
from pathlib import Path
from typing import Dict, List
from .base import BaseInstaller


class ClaudeCodeInstaller(BaseInstaller):
    """Installer for Claude Code with all dependencies and MCP plugins."""
    
    def __init__(self, logger):
        super().__init__(logger)
        
        # MCP plugins to install based on custom-CLAUDE.md
        self.mcp_plugins = [
            {
                'name': 'context7',
                'command': ['claude', 'mcp', 'add', '--transport', 'http', 'context7', 
                           'https://mcp.context7.com/mcp']
            },
            {
                'name': 'grep',
                'command': ['claude', 'mcp', 'add', '--transport', 'http', 'grep', 
                           'https://mcp.grep.app']
            },
            {
                'name': 'spec-workflow-mcp',
                'command': ['claude', 'mcp', 'add', 'spec-workflow-mcp', '-s', 'user', 
                           '--', 'npx', '-y', 'spec-workflow-mcp@latest']
            }
        ]
    
    @property
    def description(self) -> str:
        return "Claude Code CLI with MCP plugins (requires Node.js/npm)"
    
    def is_installed(self) -> bool:
        """Check if Claude Code is installed and working."""
        return self.command_exists('claude') and self._check_claude_working()
    
    def _check_claude_working(self) -> bool:
        """Check if Claude Code is properly configured."""
        try:
            result = self.run_command(['claude', '--version'], check=False)
            return result.returncode == 0
        except:
            return False
    
    def _check_prerequisites(self) -> List[str]:
        """Check prerequisites for Claude Code setup."""
        issues = []
        
        # Check for Node.js
        if not self.command_exists('node'):
            issues.append("Node.js is not installed")
        
        # Check for npm
        if not self.command_exists('npm'):
            issues.append("npm is not installed")
        
        return issues
    
    def install(self) -> bool:
        """Install Claude Code with all dependencies."""
        try:
            # Check prerequisites first
            issues = self._check_prerequisites()
            if issues:
                self.logger.error("Prerequisites not met:")
                for issue in issues:
                    self.logger.error(f"  - {issue}")
                self.logger.info("Please install Node.js and npm first:")
                self.logger.info("Option 1 - Using Node Version Manager (NVM):")
                self.logger.info("  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash")
                self.logger.info("  source ~/.bashrc  # or restart terminal")
                self.logger.info("  nvm install --lts")
                self.logger.info("  nvm use --lts")
                self.logger.info("Option 2 - System package manager:")
                self.logger.info("  Ubuntu/Debian: sudo apt install nodejs npm")
                self.logger.info("  CentOS/RHEL:   sudo yum install nodejs npm")
                self.logger.info("  macOS:         brew install node")
                return False
            
            # Install Claude Code
            if not self.command_exists('claude'):
                self.logger.info("Installing Claude Code...")
                self._install_claude_code()
            else:
                self.logger.info("Claude Code already installed")
            
            # Install MCP plugins
            self.logger.info("Installing MCP plugins...")
            self._install_mcp_plugins()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Claude Code: {e}")
            return False
    
    
    def _install_claude_code(self):
        """Install Claude Code CLI via NPM."""
        # Install Claude Code globally using system npm
        self.logger.info("Installing Claude Code via npm...")
        self.run_command(['npm', 'install', '-g', '@anthropics/claude-code'])
        
        # Verify installation
        result = self.run_command(['claude', '--version'], check=False)
        
        if result.returncode != 0:
            # Try alternative installation method
            self.logger.info("NPM installation failed, trying alternative installation via curl...")
            curl_install = 'curl -fsSL https://claude.ai/install.sh | sh'
            self.run_command([curl_install], shell=True)
    
    def _install_mcp_plugins(self):
        """Install required MCP plugins for Claude Code."""
        for plugin in self.mcp_plugins:
            try:
                self.logger.info(f"Installing MCP plugin: {plugin['name']}")
                
                # Run the plugin command directly
                self.run_command(plugin['command'])
                
            except Exception as e:
                self.logger.warning(f"Failed to install MCP plugin {plugin['name']}: {e}")
                # Don't fail the entire installation for MCP plugin failures
                continue
    
    def _check_mcp_status(self) -> Dict[str, bool]:
        """Check which MCP plugins are installed."""
        status = {}
        
        try:
            result = self.run_command(['claude', 'mcp', 'list'], check=False)
            
            if result.returncode == 0:
                output = result.stdout
                for plugin in self.mcp_plugins:
                    status[plugin['name']] = plugin['name'] in output
            else:
                # If claude mcp list fails, assume none are installed
                for plugin in self.mcp_plugins:
                    status[plugin['name']] = False
                    
        except Exception:
            for plugin in self.mcp_plugins:
                status[plugin['name']] = False
        
        return status
    
    def update(self) -> bool:
        """Update Claude Code and MCP plugins."""
        try:
            # Update Claude Code
            self.logger.info("Updating Claude Code...")
            self.run_command(['npm', 'update', '-g', '@anthropics/claude-code'])
            
            # Reinstall MCP plugins to ensure they're up to date
            self._install_mcp_plugins()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Claude Code: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall Claude Code."""
        try:
            # Uninstall Claude Code
            self.logger.info("Uninstalling Claude Code...")
            self.run_command(['npm', 'uninstall', '-g', '@anthropics/claude-code'], check=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall Claude Code: {e}")
            return False
    
    def status(self):
        """Show detailed status of Claude Code installation."""
        self.logger.info("Claude Code Installation Status:")
        
        # Check Node.js
        try:
            result = self.run_command(['node', '--version'])
            node_version = result.stdout.strip()
            self.logger.info(f"  Node.js: ✅ {node_version}")
        except:
            self.logger.info("  Node.js: ❌")
        
        # Check npm
        try:
            result = self.run_command(['npm', '--version'])
            npm_version = result.stdout.strip()
            self.logger.info(f"  npm: ✅ {npm_version}")
        except:
            self.logger.info("  npm: ❌")
        
        # Check Claude Code
        claude_status = "✅" if self.is_installed() else "❌"
        self.logger.info(f"  Claude Code: {claude_status}")
        
        # Check MCP plugins
        mcp_status = self._check_mcp_status()
        self.logger.info("  MCP Plugins:")
        for plugin, installed in mcp_status.items():
            status = "✅" if installed else "❌"
            self.logger.info(f"    {plugin}: {status}")