"""
Secure file upload service with validation, virus scanning, and storage
"""

import hashlib
import mimetypes
import os
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, UploadFile, status
from PIL import Image
import magic

from ..core.config import settings
from ..core.security import validate_file_upload, sanitize_filename


class SecureFileUploadService:
    """
    Service for handling secure file uploads with comprehensive validation
    """
    
    def __init__(self, base_upload_dir: str = None):
        self.base_upload_dir = Path(base_upload_dir or settings.UPLOAD_DIR)
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different file types
        self.subdirs = {
            'images': self.base_upload_dir / 'images',
            'documents': self.base_upload_dir / 'documents', 
            'avatars': self.base_upload_dir / 'avatars',
            'temp': self.base_upload_dir / 'temp'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file: UploadFile,
        category: str = 'documents',
        allowed_types: Optional[List[str]] = None,
        max_size: Optional[int] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Upload a file with comprehensive security validation
        
        Args:
            file: FastAPI UploadFile object
            category: File category (images, documents, avatars)
            allowed_types: List of allowed file types
            max_size: Maximum file size in bytes
            user_id: ID of the user uploading the file
            tenant_id: Tenant ID for multi-tenant isolation
            
        Returns:
            Dict with file information including secure filename and path
        """
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Basic validation
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
        
        # Validate file size
        max_size = max_size or settings.MAX_FILE_SIZE
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {max_size / 1024 / 1024}MB"
            )
        
        # Validate filename and content
        filename = sanitize_filename(file.filename or 'unnamed_file')
        validate_file_upload(filename, content, allowed_types)
        
        # Validate MIME type
        detected_mime = magic.from_buffer(content, mime=True)
        self._validate_mime_type(filename, detected_mime, allowed_types)
        
        # Virus scan (placeholder - in production use ClamAV or similar)
        if await self._scan_for_viruses(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File failed security scan"
            )
        
        # Generate secure filename
        file_extension = Path(filename).suffix.lower()
        secure_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Determine storage path
        if category not in self.subdirs:
            category = 'documents'
        
        storage_dir = self.subdirs[category]
        if tenant_id:
            storage_dir = storage_dir / tenant_id
            storage_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = storage_dir / secure_filename
        
        # Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # For images, create thumbnail
            thumbnail_path = None
            if category == 'images' and self._is_image_file(file_extension):
                thumbnail_path = await self._create_thumbnail(file_path)
            
            # Calculate file hash for deduplication/integrity
            file_hash = hashlib.sha256(content).hexdigest()
            
            return {
                'filename': filename,
                'secure_filename': secure_filename,
                'file_path': str(file_path),
                'relative_path': str(file_path.relative_to(self.base_upload_dir)),
                'thumbnail_path': str(thumbnail_path) if thumbnail_path else None,
                'size': len(content),
                'mime_type': detected_mime,
                'file_hash': file_hash,
                'category': category,
                'user_id': user_id,
                'tenant_id': tenant_id
            }
            
        except Exception as e:
            # Clean up if save failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    def _validate_mime_type(self, filename: str, detected_mime: str, allowed_types: Optional[List[str]]):
        """Validate file MIME type against filename extension"""
        expected_mime = mimetypes.guess_type(filename)[0]
        
        # Common MIME type mismatches to check
        dangerous_mismatches = [
            ('application/x-executable', '.jpg'),
            ('application/x-executable', '.png'),
            ('text/html', '.jpg'),
            ('text/html', '.png'),
        ]
        
        for dangerous_mime, safe_ext in dangerous_mismatches:
            if detected_mime == dangerous_mime and filename.lower().endswith(safe_ext):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File content does not match extension"
                )
        
        # Additional validation for specific file types
        if allowed_types:
            allowed_mimes = self._get_allowed_mimes(allowed_types)
            if detected_mime not in allowed_mimes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed. Detected: {detected_mime}"
                )
    
    def _get_allowed_mimes(self, allowed_types: List[str]) -> List[str]:
        """Get allowed MIME types for file categories"""
        mime_mappings = {
            'image': [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'image/svg+xml', 'image/bmp', 'image/tiff'
            ],
            'document': [
                'application/pdf', 'text/plain', 'text/csv',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/rtf'
            ],
            'archive': [
                'application/zip', 'application/x-tar', 'application/gzip',
                'application/x-7z-compressed', 'application/x-rar-compressed'
            ]
        }
        
        allowed_mimes = []
        for file_type in allowed_types:
            if file_type in mime_mappings:
                allowed_mimes.extend(mime_mappings[file_type])
        
        return allowed_mimes
    
    async def _scan_for_viruses(self, content: bytes) -> bool:
        """
        Scan file content for viruses
        
        In production, this should integrate with ClamAV or similar.
        For now, this is a placeholder that checks for basic threats.
        """
        # Convert to string for basic pattern matching
        try:
            content_str = content.decode('utf-8', errors='ignore').lower()
        except:
            content_str = str(content).lower()
        
        # Basic suspicious pattern detection
        suspicious_patterns = [
            b'virus', b'trojan', b'malware', b'backdoor',
            b'<script', b'javascript:', b'vbscript:',
            b'eval(', b'exec(', b'system(', b'shell_exec('
        ]
        
        for pattern in suspicious_patterns:
            if pattern in content:
                return True  # Virus detected
        
        return False  # Clean
    
    def _is_image_file(self, extension: str) -> bool:
        """Check if file extension indicates an image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        return extension.lower() in image_extensions
    
    async def _create_thumbnail(self, image_path: Path) -> Optional[Path]:
        """Create thumbnail for image files"""
        try:
            thumbnail_dir = image_path.parent / 'thumbnails'
            thumbnail_dir.mkdir(exist_ok=True)
            
            thumbnail_path = thumbnail_dir / f"thumb_{image_path.name}"
            
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85)
            
            return thumbnail_path
            
        except Exception:
            # Thumbnail creation failed, but don't fail the upload
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Securely delete a file"""
        try:
            path = Path(file_path)
            
            # Ensure file is within our upload directory
            if not path.is_relative_to(self.base_upload_dir):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file path"
                )
            
            if path.exists():
                path.unlink()
                
                # Also delete thumbnail if it exists
                thumbnail_path = path.parent / 'thumbnails' / f"thumb_{path.name}"
                if thumbnail_path.exists():
                    thumbnail_path.unlink()
                
                return True
                
        except Exception:
            pass
        
        return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, str]]:
        """Get information about an uploaded file"""
        try:
            path = Path(file_path)
            
            # Ensure file is within our upload directory
            if not path.is_relative_to(self.base_upload_dir):
                return None
            
            if not path.exists():
                return None
            
            stat = path.stat()
            
            return {
                'path': str(path),
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'mime_type': mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
            }
            
        except Exception:
            return None


# Global instance
file_upload_service = SecureFileUploadService()