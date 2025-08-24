"""Base installer class for all component installers."""

import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import logging


class BaseInstaller(ABC):
    """Abstract base class for all installers."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.home = Path.home()
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this installer does."""
        pass
    
    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the component is already installed."""
        pass
    
    @abstractmethod
    def install(self) -> bool:
        """Install the component."""
        pass
    
    def update(self) -> bool:
        """Update the component. Default implementation reinstalls."""
        self.logger.info(f"Updating {self.__class__.__name__}")
        return self.install()
    
    def uninstall(self) -> bool:
        """Uninstall the component. Default implementation not supported."""
        self.logger.warning(f"Uninstall not implemented for {self.__class__.__name__}")
        return False
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, 
                   shell: bool = False, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        if shell and isinstance(command, list):
            command = ' '.join(command)
        
        self.logger.debug(f"Running command: {command}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=shell,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                self.logger.debug(f"stdout: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"stderr: {result.stderr}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e}")
            self.logger.error(f"stdout: {e.stdout}")
            self.logger.error(f"stderr: {e.stderr}")
            raise
    
    def download_file(self, url: str, destination: Path) -> bool:
        """Download a file using curl or wget."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Try curl first, then wget
        for cmd in [['curl', '-fsSL', url, '-o', str(destination)],
                   ['wget', '-q', url, '-O', str(destination)]]:
            try:
                self.run_command(cmd)
                return True
            except subprocess.CalledProcessError:
                continue
        
        self.logger.error(f"Failed to download {url}")
        return False
    
    def file_exists(self, path: Path) -> bool:
        """Check if a file exists."""
        return path.exists()
    
    def directory_exists(self, path: Path) -> bool:
        """Check if a directory exists."""
        return path.is_dir()
    
    def command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            self.run_command(['which', command], check=True)
            return True
        except subprocess.CalledProcessError:
            return False