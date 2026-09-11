# File upload handling
"""
File handling utilities for resume uploads and processing
"""
import os
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
import hashlib
from config.settings import settings
from utils.logger import log


class FileHandler:
    """Utility class for handling file operations"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
    }
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_size = settings.MAX_UPLOAD_SIZE
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_file(
        self,
        filename: str,
        file_size: int,
        mime_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate file before upload
        
        Args:
            filename: Original filename
            file_size: File size in bytes
            mime_type: MIME type (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Check size
        if file_size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"
        
        # Check MIME type if provided
        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            return False, f"Invalid MIME type: {mime_type}"
        
        return True, None
    
    def generate_safe_filename(self, original_filename: str) -> str:
        """Generate a safe, unique filename
        
        Args:
            original_filename: Original filename
            
        Returns:
            Safe filename with timestamp
        """
        # Get extension
        file_ext = Path(original_filename).suffix.lower()
        
        # Remove extension from name
        name = Path(original_filename).stem
        
        # Clean filename (remove special characters)
        safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_'))
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate hash for uniqueness
        hash_part = hashlib.md5(
            f"{original_filename}{timestamp}".encode()
        ).hexdigest()[:8]
        
        # Construct safe filename
        safe_filename = f"{timestamp}_{safe_name}_{hash_part}{file_ext}"
        
        return safe_filename
    
    def save_uploaded_file(
        self,
        file_content: bytes,
        original_filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Save uploaded file to disk
        
        Args:
            file_content: File content as bytes
            original_filename: Original filename
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            # Validate file
            is_valid, error = self.validate_file(
                original_filename,
                len(file_content)
            )
            
            if not is_valid:
                return False, None, error
            
            # Generate safe filename
            safe_filename = self.generate_safe_filename(original_filename)
            file_path = self.upload_dir / safe_filename
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            log.info(f"File saved: {file_path}")
            
            return True, str(file_path), None
            
        except Exception as e:
            log.error(f"Error saving file: {e}")
            return False, None, str(e)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Success status
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                log.info(f"File deleted: {file_path}")
                return True
            else:
                log.warning(f"File not found: {file_path}")
                return False
        except Exception as e:
            log.error(f"Error deleting file: {e}")
            return False
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up old uploaded files
        
        Args:
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        try:
            deleted_count = 0
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            for file_path in self.upload_dir.glob('*'):
                if file_path.is_file():
                    file_mtime = file_path.stat().st_mtime
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            log.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            log.error(f"Error cleaning up files: {e}")
            return 0
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            File info dictionary
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            
            return {
                "filename": path.name,
                "size": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path.suffix,
                "exists": True
            }
        except Exception as e:
            log.error(f"Error getting file info: {e}")
            return None
    
    def list_uploaded_files(self, limit: int = 100) -> List[dict]:
        """List all uploaded files
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of file info dictionaries
        """
        try:
            files = []
            for file_path in self.upload_dir.glob('*'):
                if file_path.is_file() and len(files) < limit:
                    info = self.get_file_info(str(file_path))
                    if info:
                        files.append(info)
            
            # Sort by modified time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            return files
        except Exception as e:
            log.error(f"Error listing files: {e}")
            return []
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics
        
        Returns:
            Storage stats dictionary
        """
        try:
            total_size = 0
            file_count = 0
            
            for file_path in self.upload_dir.glob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "total_files": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "upload_dir": str(self.upload_dir),
                "max_file_size_mb": self.max_size / (1024 * 1024)
            }
        except Exception as e:
            log.error(f"Error getting storage stats: {e}")
            return {}
    
    def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy a file
        
        Args:
            source_path: Source file path
            dest_path: Destination file path
            
        Returns:
            Success status
        """
        try:
            shutil.copy2(source_path, dest_path)
            log.info(f"File copied: {source_path} -> {dest_path}")
            return True
        except Exception as e:
            log.error(f"Error copying file: {e}")
            return False
    
    def move_file(self, source_path: str, dest_path: str) -> bool:
        """Move a file
        
        Args:
            source_path: Source file path
            dest_path: Destination file path
            
        Returns:
            Success status
        """
        try:
            shutil.move(source_path, dest_path)
            log.info(f"File moved: {source_path} -> {dest_path}")
            return True
        except Exception as e:
            log.error(f"Error moving file: {e}")
            return False


# Global instance
file_handler = FileHandler()