"""JSON file operations service.

Provides safe read/write operations for game configuration JSON files.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import shutil


class JSONService:
    """Service for managing JSON configuration files."""
    
    def __init__(self, data_dir: str = None):
        """Initialize JSON service.
        
        Args:
            data_dir: Path to data directory (defaults to ../data relative to backend)
        """
        if data_dir is None:
            backend_dir = Path(__file__).parent.parent
            self.data_dir = backend_dir.parent / 'data'
        else:
            self.data_dir = Path(data_dir)
        
        self.backup_dir = self.data_dir / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
    
    def read_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """Read JSON file.
        
        Args:
            filename: Name of JSON file (e.g., 'specialists.json')
            
        Returns:
            Parsed JSON data or None if error
        """
        try:
            file_path = self.data_dir / filename
            if not file_path.exists():
                return None
                
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None
    
    def write_json(self, filename: str, data: Dict[str, Any], create_backup: bool = True) -> bool:
        """Write JSON file with optional backup.
        
        Args:
            filename: Name of JSON file
            data: Data to write
            create_backup: Whether to create backup before writing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.data_dir / filename
            
            # Create backup if file exists
            if create_backup and file_path.exists():
                self._create_backup(filename)
            
            # Write file with pretty formatting
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error writing {filename}: {e}")
            return False
    
    def _create_backup(self, filename: str):
        """Create timestamped backup of file.
        
        Args:
            filename: Name of file to backup
        """
        try:
            source = self.data_dir / filename
            if not source.exists():
                return
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{filename.replace('.json', '')}_{timestamp}.json"
            destination = self.backup_dir / backup_name
            
            shutil.copy2(source, destination)
            
            # Keep only last 10 backups per file
            self._cleanup_old_backups(filename)
        except Exception as e:
            print(f"Error creating backup for {filename}: {e}")
    
    def _cleanup_old_backups(self, filename: str, keep_count: int = 10):
        """Remove old backup files.
        
        Args:
            filename: Original filename
            keep_count: Number of backups to keep
        """
        try:
            base_name = filename.replace('.json', '')
            backups = sorted([
                f for f in self.backup_dir.iterdir()
                if f.name.startswith(base_name) and f.name.endswith('.json')
            ], key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for backup in backups[keep_count:]:
                backup.unlink()
        except Exception as e:
            print(f"Error cleaning up backups for {filename}: {e}")
    
    def list_config_files(self) -> List[str]:
        """List all JSON configuration files.
        
        Returns:
            List of JSON filenames
        """
        try:
            return [
                f.name for f in self.data_dir.iterdir()
                if f.is_file() and f.suffix == '.json'
            ]
        except Exception as e:
            print(f"Error listing config files: {e}")
            return []
    
    def validate_json_schema(self, filename: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate JSON data against expected schema.
        
        Args:
            filename: Name of file for context
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation - ensure it's a dict
        if not isinstance(data, dict):
            return False, "Data must be a JSON object"
        
        # File-specific validation
        if filename == 'specialists.json':
            if 'specialists' not in data or not isinstance(data['specialists'], list):
                return False, "Missing or invalid 'specialists' array"
        elif filename == 'incidents.json':
            if 'incident_types' not in data or not isinstance(data['incident_types'], list):
                return False, "Missing or invalid 'incident_types' array"
        elif filename == 'clients.json':
            if 'clients' not in data or not isinstance(data['clients'], list):
                return False, "Missing or invalid 'clients' array"
        
        return True, None
    
    def get_backup_list(self, filename: str) -> List[Dict[str, Any]]:
        """Get list of backups for a file.
        
        Args:
            filename: Original filename
            
        Returns:
            List of backup info dictionaries
        """
        try:
            base_name = filename.replace('.json', '')
            backups = []
            
            for backup_file in self.backup_dir.iterdir():
                if backup_file.name.startswith(base_name) and backup_file.name.endswith('.json'):
                    stat = backup_file.stat()
                    backups.append({
                        'filename': backup_file.name,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return sorted(backups, key=lambda x: x['created'], reverse=True)
        except Exception as e:
            print(f"Error getting backup list: {e}")
            return []
    
    def restore_backup(self, backup_filename: str, target_filename: str) -> bool:
        """Restore a backup file.
        
        Args:
            backup_filename: Name of backup file
            target_filename: Name of target file to restore to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = self.backup_dir / backup_filename
            target_path = self.data_dir / target_filename
            
            if not backup_path.exists():
                return False
            
            # Create backup of current file before restoring
            if target_path.exists():
                self._create_backup(target_filename)
            
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False


# Global JSON service instance
json_service = JSONService()
