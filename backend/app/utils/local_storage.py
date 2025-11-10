"""
Local File Storage Utilities
Replacement for AWS S3 - stores files locally on the server
"""

import os
import shutil
import json
import logging
from pathlib import Path
from uuid import uuid4
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class LocalStorage:
    """Local file storage manager"""

    def __init__(self, base_path: str = None):
        """
        Initialize local storage

        Args:
            base_path: Base directory for file storage (default: ./storage/contracts)
        """
        self.base_path = base_path or settings.LOCAL_STORAGE_PATH
        self._ensure_base_directory()
        logger.info(f"Local storage initialized at: {self.base_path}")

    def _ensure_base_directory(self):
        """Ensure base storage directory exists"""
        os.makedirs(self.base_path, exist_ok=True)

    def _get_contract_directory(self, user_id: str, contract_id: str) -> str:
        """Get contract directory path"""
        return os.path.join(
            self.base_path,
            f"user_{user_id}",
            "contracts",
            contract_id
        )

    def upload_file(
        self,
        file,
        user_id: str,
        contract_id: str,
        custom_filename: Optional[str] = None
    ) -> str:
        """
        Upload file to local storage

        Args:
            file: File object to upload
            user_id: User ID
            contract_id: Contract ID
            custom_filename: Custom filename (optional)

        Returns:
            str: Relative file path

        Raises:
            Exception: If upload fails
        """
        try:
            # Generate filename
            if custom_filename:
                filename = custom_filename
            else:
                ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
                filename = f"contract_{uuid4().hex[:8]}.{ext}"

            # Create directory structure
            contract_dir = self._get_contract_directory(user_id, contract_id)
            os.makedirs(contract_dir, exist_ok=True)

            # Full file path
            file_path = os.path.join(contract_dir, filename)

            logger.info(f"Uploading to local storage: {file_path}")

            # Reset file pointer
            file.file.seek(0)

            # Check file size
            file_content = file.file.read()
            file_size = len(file_content)

            if file_size == 0:
                raise Exception(f"File is empty: {file.filename}")

            logger.info(f"File size: {file_size} bytes")

            # Write file
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Save metadata
            self._save_file_metadata(
                file_path,
                user_id=user_id,
                contract_id=contract_id,
                original_filename=file.filename,
                file_size=file_size,
                content_type=file.content_type
            )

            # Return relative path
            relative_path = os.path.relpath(file_path, self.base_path)

            logger.info(f"Local storage upload successful: {relative_path}")
            return relative_path

        except Exception as e:
            error_msg = f"Local storage upload failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _save_file_metadata(
        self,
        file_path: str,
        user_id: str,
        contract_id: str,
        original_filename: str,
        file_size: int,
        content_type: Optional[str] = None
    ):
        """Save file metadata as JSON"""
        metadata_path = f"{file_path}.meta.json"
        metadata = {
            "user_id": user_id,
            "contract_id": contract_id,
            "original_filename": original_filename,
            "file_size": file_size,
            "content_type": content_type or "application/octet-stream",
            "uploaded_at": datetime.utcnow().isoformat(),
        }

        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")

    def download_files(
        self,
        file_paths: List[str],
        destination_dir: Optional[str] = None
    ) -> List[str]:
        """
        Copy files to destination directory

        Args:
            file_paths: List of relative file paths
            destination_dir: Destination directory (default: temp directory)

        Returns:
            list: List of absolute file paths in destination

        Raises:
            Exception: If download fails
        """
        if destination_dir is None:
            import tempfile
            destination_dir = tempfile.mkdtemp()

        try:
            os.makedirs(destination_dir, exist_ok=True)
            local_paths = []

            for relative_path in file_paths:
                try:
                    # Get source path
                    source_path = os.path.join(self.base_path, relative_path)

                    if not os.path.exists(source_path):
                        raise FileNotFoundError(f"File not found: {source_path}")

                    # Get destination path
                    filename = os.path.basename(source_path)
                    dest_path = os.path.join(destination_dir, filename)

                    logger.info(f"Copying file: {source_path} -> {dest_path}")

                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    local_paths.append(dest_path)

                    logger.info(f"File copied successfully: {filename}")

                except FileNotFoundError as e:
                    logger.error(f"File not found: {relative_path}")
                    raise Exception(f"File not found: {relative_path}")
                except Exception as e:
                    logger.error(f"Copy failed: {relative_path}, error: {str(e)}")
                    raise Exception(f"File copy failed: {relative_path} - {str(e)}")

            return local_paths

        except Exception as e:
            logger.error(f"File download processing failed: {str(e)}")
            raise

    def list_files(
        self,
        user_id: str,
        contract_id: str,
        extensions: Optional[List[str]] = None
    ) -> List[str]:
        """
        List files in contract directory

        Args:
            user_id: User ID
            contract_id: Contract ID
            extensions: File extensions to filter (e.g., ['.jpg', '.png'])

        Returns:
            list: List of relative file paths
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.pdf']

        try:
            contract_dir = self._get_contract_directory(user_id, contract_id)

            if not os.path.exists(contract_dir):
                logger.warning(f"Contract directory not found: {contract_dir}")
                return []

            logger.info(f"Listing files in: {contract_dir}")

            file_paths = []

            for filename in os.listdir(contract_dir):
                # Skip metadata files
                if filename.endswith('.meta.json'):
                    continue

                # Check extension
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in extensions:
                    full_path = os.path.join(contract_dir, filename)
                    relative_path = os.path.relpath(full_path, self.base_path)
                    file_paths.append(relative_path)

            # Sort by filename
            file_paths.sort()

            logger.info(f"Found {len(file_paths)} files")
            return file_paths

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise

    def delete_contract(self, user_id: str, contract_id: str) -> bool:
        """
        Delete all files for a contract

        Args:
            user_id: User ID
            contract_id: Contract ID

        Returns:
            bool: Success status
        """
        try:
            contract_dir = self._get_contract_directory(user_id, contract_id)

            if os.path.exists(contract_dir):
                shutil.rmtree(contract_dir)
                logger.info(f"Deleted contract directory: {contract_dir}")
                return True
            else:
                logger.warning(f"Contract directory not found: {contract_dir}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete contract: {e}")
            return False

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information including metadata

        Args:
            file_path: Relative file path

        Returns:
            dict: File information or None if not found
        """
        try:
            full_path = os.path.join(self.base_path, file_path)

            if not os.path.exists(full_path):
                return None

            # Get basic file info
            stat = os.stat(full_path)
            info = {
                "path": file_path,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }

            # Try to load metadata
            metadata_path = f"{full_path}.meta.json"
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        info.update(metadata)
                except Exception as e:
                    logger.warning(f"Failed to load metadata: {e}")

            return info

        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_size = 0
            file_count = 0

            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    if not file.endswith('.meta.json'):
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1

            return {
                "base_path": self.base_path,
                "total_files": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
            }

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "base_path": self.base_path,
                "error": str(e)
            }


# Global instance
_local_storage: Optional[LocalStorage] = None


def get_local_storage() -> LocalStorage:
    """Get or create local storage instance"""
    global _local_storage

    if _local_storage is None:
        _local_storage = LocalStorage()

    return _local_storage
