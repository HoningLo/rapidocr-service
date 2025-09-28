"""File management utilities for handling uploads and temporary files."""

import asyncio
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

from .config import settings
from .logging_config import LoggingMixin


class FileManager(LoggingMixin):
    """Manages temporary file storage, cleanup, and UUID tracking."""

    def __init__(self) -> None:
        super().__init__()
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self._cleanup_task: asyncio.Task[None] | None = None

    async def start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.log_info(
                "Started file cleanup task",
                cleanup_interval=settings.cleanup_interval,
                retention_time=settings.file_retention,
            )

    async def stop_cleanup_task(self) -> None:
        """Stop the background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self.log_info("Stopped file cleanup task")

    async def save_upload_file(self, upload_file: UploadFile) -> tuple[str, Path]:
        """
        Save an uploaded file with UUID naming.

        Returns:
            tuple: (uuid_string, file_path)
        """
        # Generate UUID for the file
        file_uuid = str(uuid4())

        # Get file extension
        original_name = upload_file.filename or "unknown"
        file_ext = Path(original_name).suffix.lower()
        if not file_ext:
            file_ext = ".bin"  # Default extension

        # Create file path with UUID
        file_path = self.temp_dir / f"{file_uuid}{file_ext}"

        try:
            # Save file content
            async with aiofiles.open(file_path, "wb") as f:
                content = await upload_file.read()
                await f.write(content)

            # Reset file pointer for potential re-reading
            await upload_file.seek(0)

            self.log_info(
                "Saved upload file",
                file_uuid=file_uuid,
                original_name=original_name,
                file_size=len(content),
                file_path=str(file_path),
            )

            return file_uuid, file_path

        except Exception as e:
            self.log_error(
                "Failed to save upload file",
                file_uuid=file_uuid,
                original_name=original_name,
                error=str(e),
            )

            # Cleanup partial file if it exists
            if file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass

            raise

    async def save_multiple_files(
        self, upload_files: list[UploadFile]
    ) -> list[tuple[str, Path, str]]:
        """
        Save multiple uploaded files with UUID naming.

        Returns:
            List of tuples: [(uuid_string, file_path, original_filename), ...]
        """
        results = []

        for upload_file in upload_files:
            try:
                file_uuid, file_path = await self.save_upload_file(upload_file)
                results.append(
                    (file_uuid, file_path, upload_file.filename or "unknown")
                )
            except Exception as e:
                self.log_error(
                    "Failed to save file in batch",
                    filename=upload_file.filename,
                    error=str(e),
                )
                raise

        self.log_info("Saved multiple files", file_count=len(results))
        return results

    def cleanup_file(self, file_path: Path) -> bool:
        """
        Remove a specific file.

        Returns:
            bool: True if file was removed, False otherwise
        """
        try:
            if file_path.exists():
                file_path.unlink()
                self.log_debug("Cleaned up file", file_path=str(file_path))
                return True
        except Exception as e:
            self.log_warning(
                "Failed to cleanup file", file_path=str(file_path), error=str(e)
            )
        return False

    async def cleanup_old_files(self) -> int:
        """
        Clean up files older than the retention time.

        Returns:
            int: Number of files cleaned up
        """
        if not self.temp_dir.exists():
            return 0

        current_time = time.time()
        retention_seconds = settings.file_retention
        cleanup_count = 0

        try:
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime

                    if file_age > retention_seconds:
                        if self.cleanup_file(file_path):
                            cleanup_count += 1

        except Exception as e:
            self.log_error("Error during file cleanup", error=str(e))

        if cleanup_count > 0:
            self.log_info("Cleaned up old files", cleanup_count=cleanup_count)

        return cleanup_count

    async def _cleanup_loop(self) -> None:
        """Background task for periodic file cleanup."""
        while True:
            try:
                await asyncio.sleep(settings.cleanup_interval)
                await self.cleanup_old_files()
            except asyncio.CancelledError:
                self.log_info("Cleanup loop cancelled")
                break
            except Exception as e:
                self.log_error("Error in cleanup loop", error=str(e))
                # Continue running despite errors

    def get_temp_dir_info(self) -> dict[str, Any]:
        """Get information about the temporary directory."""
        try:
            if not self.temp_dir.exists():
                return {"exists": False}

            files = list(self.temp_dir.iterdir())
            file_count = len([f for f in files if f.is_file()])

            # Calculate total size
            total_size = sum(f.stat().st_size for f in files if f.is_file())

            return {
                "exists": True,
                "path": str(self.temp_dir),
                "file_count": file_count,
                "total_size_bytes": total_size,
                "cleanup_active": self._cleanup_task is not None
                and not self._cleanup_task.done(),
            }
        except Exception as e:
            self.log_error("Error getting temp dir info", error=str(e))
            return {"error": str(e)}


# Global file manager instance
file_manager = FileManager()
