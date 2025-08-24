"""Claude Code installer with NVM/NPM dependencies and MCP setup."""

import os
import json
from pathlib import Path
from typing import Dict, List
from .base import BaseInstaller


class ClaudeCodeInstaller(BaseInstaller):
    """Installer for Claude Code with all dependencies and MCP plugins."""
    
    def __init__(self, logger):
        super().__init__(logger)
        self.nvm_dir = self.home / '.nvm'
        self.node_version = 'lts/*'  # Use latest LTS version
        
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
        return "Claude Code CLI with NVM, Node.js, and MCP plugins"
    
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
    
    def install(self) -> bool:
        """Install Claude Code with all dependencies."""
        try:
            # Install NVM
            if not self._is_nvm_installed():
                self.logger.info("Installing NVM...")
                self._install_nvm()
            else:
                self.logger.info("NVM already installed")
            
            # Install Node.js via NVM
            self.logger.info("Installing Node.js via NVM...")
            self._install_node()
            
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
    
    def _is_nvm_installed(self) -> bool:
        """Check if NVM is installed."""
        nvm_script = self.nvm_dir / 'nvm.sh'
        return nvm_script.exists()
    
    def _install_nvm(self):
        """Install Node Version Manager (NVM)."""
        nvm_install_url = "https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh"
        
        # Download and run NVM installer
        install_cmd = f'curl -o- {nvm_install_url} | bash'
        self.run_command([install_cmd], shell=True)
        
        if not self._is_nvm_installed():
            raise Exception("NVM installation failed")
        
        # Source NVM in current session
        self._source_nvm()
    
    def _source_nvm(self):
        """Source NVM in the current environment."""
        nvm_script = self.nvm_dir / 'nvm.sh'
        if nvm_script.exists():
            # Set NVM environment variables
            os.environ['NVM_DIR'] = str(self.nvm_dir)
    
    def _install_node(self):
        """Install Node.js using NVM."""
        self._source_nvm()
        
        # Commands to run with NVM sourced
        nvm_commands = [
            f'source {self.nvm_dir}/nvm.sh && nvm install {self.node_version}',
            f'source {self.nvm_dir}/nvm.sh && nvm use {self.node_version}',
            f'source {self.nvm_dir}/nvm.sh && nvm alias default {self.node_version}'
        ]
        
        for cmd in nvm_commands:
            self.run_command([cmd], shell=True)
        
        # Verify Node.js installation
        node_check_cmd = f'source {self.nvm_dir}/nvm.sh && node --version'
        result = self.run_command([node_check_cmd], shell=True)
        self.logger.info(f"Node.js version: {result.stdout.strip()}")
    
    def _install_claude_code(self):
        """Install Claude Code CLI via NPM."""
        self._source_nvm()
        
        # Install Claude Code globally
        install_cmd = f'source {self.nvm_dir}/nvm.sh && npm install -g @anthropics/claude-code'
        self.run_command([install_cmd], shell=True)
        
        # Verify installation
        verify_cmd = f'source {self.nvm_dir}/nvm.sh && claude --version'
        result = self.run_command([verify_cmd], shell=True, check=False)
        
        if result.returncode != 0:
            # Try alternative installation method
            self.logger.info("Trying alternative installation via curl...")
            curl_install = 'curl -fsSL https://claude.ai/install.sh | sh'
            self.run_command([curl_install], shell=True)
    
    def _install_mcp_plugins(self):
        """Install required MCP plugins for Claude Code."""
        self._source_nvm()
        
        for plugin in self.mcp_plugins:
            try:
                self.logger.info(f"Installing MCP plugin: {plugin['name']}")
                
                # Prepare command with NVM sourcing
                cmd_str = f"source {self.nvm_dir}/nvm.sh && " + ' '.join(plugin['command'])
                self.run_command([cmd_str], shell=True)
                
            except Exception as e:
                self.logger.warning(f"Failed to install MCP plugin {plugin['name']}: {e}")
                # Don't fail the entire installation for MCP plugin failures
                continue
    
    def _check_mcp_status(self) -> Dict[str, bool]:
        """Check which MCP plugins are installed."""
        status = {}
        
        try:
            self._source_nvm()
            list_cmd = f'source {self.nvm_dir}/nvm.sh && claude mcp list'
            result = self.run_command([list_cmd], shell=True, check=False)
            
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
            self._source_nvm()
            
            # Update Claude Code
            self.logger.info("Updating Claude Code...")
            update_cmd = f'source {self.nvm_dir}/nvm.sh && npm update -g @anthropics/claude-code'
            self.run_command([update_cmd], shell=True)
            
            # Update Node.js if needed
            self.logger.info("Updating Node.js to latest LTS...")
            node_update_cmds = [
                f'source {self.nvm_dir}/nvm.sh && nvm install {self.node_version}',
                f'source {self.nvm_dir}/nvm.sh && nvm use {self.node_version}'
            ]
            
            for cmd in node_update_cmds:
                self.run_command([cmd], shell=True)
            
            # Reinstall MCP plugins to ensure they're up to date
            self._install_mcp_plugins()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Claude Code: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall Claude Code (keeps NVM and Node.js)."""
        try:
            self._source_nvm()
            
            # Uninstall Claude Code
            self.logger.info("Uninstalling Claude Code...")
            uninstall_cmd = f'source {self.nvm_dir}/nvm.sh && npm uninstall -g @anthropics/claude-code'
            self.run_command([uninstall_cmd], shell=True, check=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall Claude Code: {e}")
            return False
    
    def status(self):
        """Show detailed status of Claude Code installation."""
        self.logger.info("Claude Code Installation Status:")
        
        # Check NVM
        nvm_status = "✅" if self._is_nvm_installed() else "❌"
        self.logger.info(f"  NVM: {nvm_status}")
        
        # Check Node.js
        try:
            self._source_nvm()
            node_cmd = f'source {self.nvm_dir}/nvm.sh && node --version'
            result = self.run_command([node_cmd], shell=True)
            node_version = result.stdout.strip()
            self.logger.info(f"  Node.js: ✅ {node_version}")
        except:
            self.logger.info("  Node.js: ❌")
        
        # Check Claude Code
        claude_status = "✅" if self.is_installed() else "❌"
        self.logger.info(f"  Claude Code: {claude_status}")
        
        # Check MCP plugins
        mcp_status = self._check_mcp_status()
        self.logger.info("  MCP Plugins:")
        for plugin, installed in mcp_status.items():
            status = "✅" if installed else "❌"
            self.logger.info(f"    {plugin}: {status}")