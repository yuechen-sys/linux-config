"""System information and utilities."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class SystemInfo:
    """System information gathering utility."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.architecture = platform.machine()
        self.python_version = platform.python_version()
    
    @property
    def is_linux(self) -> bool:
        return self.platform == 'linux'
    
    @property
    def is_macos(self) -> bool:
        return self.platform == 'darwin'
    
    @property
    def is_wsl(self) -> bool:
        """Check if running in Windows Subsystem for Linux."""
        if not self.is_linux:
            return False
        
        try:
            with open('/proc/version', 'r') as f:
                version = f.read().lower()
                return 'microsoft' in version or 'wsl' in version
        except:
            return False
    
    def get_distribution(self) -> Optional[str]:
        """Get Linux distribution name."""
        if not self.is_linux:
            return None
        
        try:
            # Try /etc/os-release first
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        
        # Try lsb_release command
        try:
            result = subprocess.run(['lsb_release', '-si'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().lower()
        except:
            pass
        
        return None
    
    def get_package_manager(self) -> Optional[str]:
        """Detect the system package manager."""
        package_managers = {
            'apt-get': ['/usr/bin/apt-get', '/bin/apt-get'],
            'yum': ['/usr/bin/yum', '/bin/yum'],
            'dnf': ['/usr/bin/dnf', '/bin/dnf'],
            'pacman': ['/usr/bin/pacman', '/bin/pacman'],
            'zypper': ['/usr/bin/zypper', '/bin/zypper'],
            'brew': ['/usr/local/bin/brew', '/opt/homebrew/bin/brew', 
                    os.path.expanduser('~/bin/brew')]
        }
        
        for manager, paths in package_managers.items():
            for path in paths:
                if Path(path).exists():
                    return manager
        
        return None
    
    def get_shell(self) -> str:
        """Get current shell."""
        return os.environ.get('SHELL', '/bin/bash')
    
    def get_environment_info(self) -> Dict[str, str]:
        """Get comprehensive environment information."""
        return {
            'platform': self.platform,
            'architecture': self.architecture,
            'python_version': self.python_version,
            'distribution': self.get_distribution() or 'unknown',
            'package_manager': self.get_package_manager() or 'unknown',
            'shell': self.get_shell(),
            'is_wsl': str(self.is_wsl),
            'home': str(Path.home()),
            'user': os.environ.get('USER', 'unknown'),
        }
    
    def check_prerequisites(self) -> List[str]:
        """Check system prerequisites for installation."""
        issues = []
        
        # Check if we have internet connectivity
        if not self._has_internet():
            issues.append("No internet connectivity detected")
        
        # Check for required commands
        required_commands = ['curl', 'git']
        for cmd in required_commands:
            if not self._command_exists(cmd):
                issues.append(f"Required command not found: {cmd}")
        
        # Check disk space (at least 1GB free)
        if not self._has_sufficient_disk_space():
            issues.append("Insufficient disk space (need at least 1GB free)")
        
        return issues
    
    def _has_internet(self) -> bool:
        """Check internet connectivity."""
        test_hosts = ['8.8.8.8', '1.1.1.1']  # Google DNS and Cloudflare DNS
        
        for host in test_hosts:
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '3', host],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return True
            except:
                continue
        
        return False
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run(['which', command], 
                         capture_output=True, check=True)
            return True
        except:
            return False
    
    def _has_sufficient_disk_space(self, min_space_gb: float = 1.0) -> bool:
        """Check if there's sufficient disk space."""
        try:
            home_path = Path.home()
            stat = os.statvfs(home_path)
            free_bytes = stat.f_bavail * stat.f_frsize
            free_gb = free_bytes / (1024 ** 3)
            return free_gb >= min_space_gb
        except:
            return True  # Assume sufficient space if we can't check