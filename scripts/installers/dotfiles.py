"""Dotfiles installer for deploying configuration files."""

import os
import shutil
from pathlib import Path
from typing import Dict, List
from .base import BaseInstaller


class DotfilesInstaller(BaseInstaller):
    """Installer for deploying dotfiles and configuration files."""
    
    def __init__(self, logger):
        super().__init__(logger)
        self.repo_root = Path(__file__).parent.parent.parent.resolve()
        self.configs_dir = self.repo_root / 'configs'
        
        # Configuration files mapping: source -> destination
        self.dotfiles_map = {
            '.zshrc': self.home / '.zshrc',
            '.gitconfig': self.home / '.gitconfig',
            'custom-CLAUDE.md': self.home / '.claude-custom.md',
        }
    
    @property 
    def description(self) -> str:
        return "Deploy dotfiles (.zshrc, .gitconfig, etc.) to home directory"
    
    def _get_source_path(self, filename: str) -> Path:
        """Get source path for a config file, checking personal then default."""
        personal_path = self.configs_dir / 'personal' / filename
        default_path = self.configs_dir / 'default' / filename
        
        if personal_path.exists():
            return personal_path
        elif default_path.exists():
            return default_path
        else:
            # Fallback to root directory for backward compatibility
            return self.repo_root / filename
    
    def is_installed(self) -> bool:
        """Check if dotfiles are deployed and up to date."""
        for src_name, dest_path in self.dotfiles_map.items():
            src_path = self._get_source_path(src_name)
            
            if not src_path.exists():
                continue  # Skip if source doesn't exist
                
            if not dest_path.exists():
                return False  # Destination doesn't exist
            
            # Skip if source and destination are the same file
            if src_path.resolve() == dest_path.resolve():
                continue
                
            # Check if files are different (simple size comparison)
            if src_path.stat().st_size != dest_path.stat().st_size:
                return False
                
        return True
    
    def install(self) -> bool:
        """Deploy dotfiles to home directory."""
        try:
            self.logger.info("Deploying dotfiles...")
            
            # Create backups of existing files
            self._create_backups()
            
            # Copy files
            for src_name, dest_path in self.dotfiles_map.items():
                src_path = self._get_source_path(src_name)
                
                if not src_path.exists():
                    self.logger.warning(f"Source file not found: {src_path}")
                    continue
                
                source_type = "personal" if "personal" in str(src_path) else "default"
                self.logger.info(f"Deploying {src_name} ({source_type}) -> {dest_path}")
                
                # Create destination directory if needed
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file (skip if same file)
                if src_path.resolve() != dest_path.resolve():
                    shutil.copy2(src_path, dest_path)
                else:
                    self.logger.info(f"Skipping {src_name} (source and destination are the same file)")
            
            # Set proper permissions
            self._set_permissions()
            
            self.logger.info("Dotfiles deployment completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy dotfiles: {e}")
            return False
    
    def _create_backups(self):
        """Create backups of existing dotfiles."""
        backup_dir = self.home / '.config-backups'
        backup_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for src_name, dest_path in self.dotfiles_map.items():
            if dest_path.exists():
                backup_name = f"{dest_path.name}.backup_{timestamp}"
                backup_path = backup_dir / backup_name
                
                self.logger.info(f"Backing up {dest_path} -> {backup_path}")
                shutil.copy2(dest_path, backup_path)
    
    def _set_permissions(self):
        """Set appropriate permissions for dotfiles."""
        for dest_path in self.dotfiles_map.values():
            if dest_path.exists():
                # Make readable/writable by owner only for config files
                dest_path.chmod(0o600)
                
        # Special case: .zshrc should be executable
        zshrc_path = self.home / '.zshrc'
        if zshrc_path.exists():
            zshrc_path.chmod(0o644)
    
    def update(self) -> bool:
        """Update dotfiles (same as install)."""
        return self.install()
    
    def uninstall(self) -> bool:
        """Remove deployed dotfiles and restore backups if available."""
        try:
            backup_dir = self.home / '.config-backups'
            
            for src_name, dest_path in self.dotfiles_map.items():
                if dest_path.exists():
                    self.logger.info(f"Removing {dest_path}")
                    dest_path.unlink()
                    
                    # Try to restore latest backup
                    backups = list(backup_dir.glob(f"{dest_path.name}.backup_*"))
                    if backups:
                        latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
                        self.logger.info(f"Restoring backup {latest_backup} -> {dest_path}")
                        shutil.copy2(latest_backup, dest_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall dotfiles: {e}")
            return False
    
    def status(self):
        """Show detailed status of dotfiles."""
        self.logger.info("Dotfiles Status:")
        
        for src_name, dest_path in self.dotfiles_map.items():
            src_path = self._get_source_path(src_name)
            
            if not src_path.exists():
                self.logger.info(f"  {src_name}: ❌ Source not found")
                continue
            
            if not dest_path.exists():
                self.logger.info(f"  {src_name}: ❌ Not deployed")
                continue
            
            # Compare file sizes and show source type
            src_size = src_path.stat().st_size
            dest_size = dest_path.stat().st_size
            source_type = "personal" if "personal" in str(src_path) else "default"
            
            if src_size == dest_size:
                self.logger.info(f"  {src_name}: ✅ Up to date ({source_type})")
            else:
                self.logger.info(f"  {src_name}: ⚠️  Out of sync ({source_type}, sizes: {src_size} vs {dest_size})")
        
        # Show available backups
        backup_dir = self.home / '.config-backups'
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.backup_*"))
            if backups:
                self.logger.info(f"  Available backups: {len(backups)} files in {backup_dir}")
    
    def diff(self, filename: str = None):
        """Show differences between source and deployed files."""
        import difflib
        
        files_to_check = self.dotfiles_map.items()
        if filename:
            # Filter to specific file
            files_to_check = [(k, v) for k, v in self.dotfiles_map.items() if k == filename]
            if not files_to_check:
                self.logger.error(f"File not found: {filename}")
                return
        
        for src_name, dest_path in files_to_check:
            src_path = self.repo_root / src_name
            
            if not src_path.exists() or not dest_path.exists():
                continue
            
            try:
                with open(src_path, 'r') as f:
                    src_lines = f.readlines()
                with open(dest_path, 'r') as f:
                    dest_lines = f.readlines()
                
                diff = list(difflib.unified_diff(
                    dest_lines, src_lines,
                    fromfile=f"deployed/{src_name}",
                    tofile=f"source/{src_name}",
                    lineterm=""
                ))
                
                if diff:
                    self.logger.info(f"Differences in {src_name}:")
                    for line in diff:
                        print(line)
                else:
                    self.logger.info(f"No differences in {src_name}")
                    
            except Exception as e:
                self.logger.warning(f"Could not compare {src_name}: {e}")