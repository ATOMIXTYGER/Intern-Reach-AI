import re
import os
import bleach
from typing import Tuple

ALLOWED_TAGS = ['b', 'i', 'strong', 'em', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre']
ALLOWED_ATTRIBUTES = {}

def sanitize_html(text: str) -> str:
    """
    Sanitize text/HTML to prevent XSS.
    """
    if not text:
        return ""
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes an uploaded filename to prevent directory traversal or script execution.
    """
    base = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    if clean.startswith('.'):
        clean = f"upload_{clean}"
    return clean

def validate_file_mime_and_size(filename: str, content: bytes, max_size_bytes: int = 10 * 1024 * 1024) -> Tuple[bool, str]:
    """
    Validates file size, extension, and magic bytes for PDF and DOCX uploads.
    """
    if len(content) > max_size_bytes:
        return False, f"File size ({len(content)} bytes) exceeds maximum permitted limit ({max_size_bytes} bytes)."
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ('.pdf', '.docx', '.doc'):
        return False, f"Unsupported file extension '{ext}'. Only .pdf and .docx are supported."
    
    # Check magic numbers
    if ext == '.pdf':
        if not content.startswith(b'%PDF-'):
            return False, "Invalid PDF header bytes."
    elif ext == '.docx':
        # DOCX is a zip file, starts with PK\x03\x04
        if not content.startswith(b'PK\x03\x04'):
            return False, "Invalid DOCX format (missing PK zip signature)."
            
    return True, "Valid"
