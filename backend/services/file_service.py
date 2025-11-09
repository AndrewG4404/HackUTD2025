"""
File upload and management service
Handles saving uploaded files to the uploads directory
"""
import os
import uuid
from pathlib import Path
from typing import List
from fastapi import UploadFile
import aiofiles


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default


def ensure_upload_dir():
    """Ensure upload directory exists"""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


async def save_uploaded_files(
    files: List[UploadFile],
    evaluation_id: str,
    vendor_id: str
) -> List[dict]:
    """
    Save uploaded files to disk.
    Returns list of file info dictionaries.
    """
    ensure_upload_dir()
    
    saved_files = []
    eval_dir = Path(UPLOAD_DIR) / evaluation_id / vendor_id
    eval_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        # Read content first to check size (UploadFile has no .size attribute)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"File {file.filename} exceeds maximum size")
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = eval_dir / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        saved_files.append({
            "name": file.filename,
            "path": str(file_path),
            "mime_type": file.content_type or "application/octet-stream"
        })
    
    return saved_files

