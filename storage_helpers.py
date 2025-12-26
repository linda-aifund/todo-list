"""
Supabase Storage helper functions for file attachments
"""

from supabase import Client
from typing import Optional, Tuple
import os
from datetime import datetime, timedelta
from constants import STORAGE_BUCKET, MAX_FILE_SIZE_BYTES, ALLOWED_FILE_TYPES


def upload_file(supabase: Client, todo_id: int, file, file_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload a file to Supabase Storage

    Args:
        supabase: Supabase client
        todo_id: ID of the todo this file belongs to
        file: File object from st.file_uploader
        file_name: Original filename

    Returns:
        Tuple of (success: bool, file_path: str, error_message: str)
    """
    try:
        # Validate file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE_BYTES:
            return False, None, f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds maximum allowed size ({MAX_FILE_SIZE_BYTES / 1024 / 1024} MB)"

        # Validate file type
        file_extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
        if file_extension not in ALLOWED_FILE_TYPES:
            return False, None, f"File type '.{file_extension}' is not allowed"

        # Generate unique file path: {todo_id}/{timestamp}_{filename}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = file_name.replace(' ', '_').replace('/', '_')
        file_path = f"{todo_id}/{timestamp}_{safe_filename}"

        # Read file contents
        file_contents = file.read()

        # Upload to Supabase Storage
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=file_path,
            file=file_contents,
            file_options={"content-type": file.type if hasattr(file, 'type') else "application/octet-stream"}
        )

        return True, file_path, None

    except Exception as e:
        return False, None, str(e)


def download_file(supabase: Client, file_path: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
    """
    Download a file from Supabase Storage

    Args:
        supabase: Supabase client
        file_path: Path to file in storage

    Returns:
        Tuple of (success: bool, file_data: bytes, error_message: str)
    """
    try:
        response = supabase.storage.from_(STORAGE_BUCKET).download(file_path)
        return True, response, None

    except Exception as e:
        return False, None, str(e)


def get_signed_url(supabase: Client, file_path: str, expires_in: int = 3600) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Generate a signed URL for downloading a file

    Args:
        supabase: Supabase client
        file_path: Path to file in storage
        expires_in: URL expiration time in seconds (default 1 hour)

    Returns:
        Tuple of (success: bool, signed_url: str, error_message: str)
    """
    try:
        response = supabase.storage.from_(STORAGE_BUCKET).create_signed_url(
            file_path,
            expires_in
        )

        if response.get('signedURL'):
            return True, response['signedURL'], None
        else:
            return False, None, "Failed to generate signed URL"

    except Exception as e:
        return False, None, str(e)


def delete_file(supabase: Client, file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Delete a file from Supabase Storage

    Args:
        supabase: Supabase client
        file_path: Path to file in storage

    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        supabase.storage.from_(STORAGE_BUCKET).remove([file_path])
        return True, None

    except Exception as e:
        return False, str(e)


def get_file_icon(file_name: str) -> str:
    """
    Get icon for file based on extension

    Args:
        file_name: Name of the file

    Returns:
        Icon emoji string
    """
    from constants import FILE_ICONS

    extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
    return FILE_ICONS.get(extension, FILE_ICONS['default'])


def validate_file_upload(file, file_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file before upload

    Args:
        file: File object
        file_name: Original filename

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds maximum ({MAX_FILE_SIZE_BYTES / 1024 / 1024} MB)"

    # Check file extension
    file_extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
    if not file_extension:
        return False, "File must have an extension"

    if file_extension not in ALLOWED_FILE_TYPES:
        return False, f"File type '.{file_extension}' is not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"

    return True, None


def create_storage_bucket(supabase: Client) -> Tuple[bool, Optional[str]]:
    """
    Create the storage bucket if it doesn't exist

    Args:
        supabase: Supabase client

    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        # Try to create the bucket
        supabase.storage.create_bucket(STORAGE_BUCKET, options={"public": False})
        return True, None

    except Exception as e:
        # Bucket might already exist, which is fine
        if "already exists" in str(e).lower():
            return True, None
        return False, str(e)
