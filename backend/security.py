import re
import hashlib
import secrets
import string
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from config import Config

class SecurityUtils:
    """Security utilities for input validation, sanitization, and authentication"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < Config.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {Config.PASSWORD_MIN_LENGTH} characters long")
        
        if Config.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if Config.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if Config.PASSWORD_REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if Config.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent XSS"""
        if not input_str:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'vbscript:', 'onload', 'onerror']
        sanitized = input_str
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized.strip()
    
    @staticmethod
    def generate_secure_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely"""
        return generate_password_hash(password, method='pbkdf2:sha256')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(hashed_password, password)
    
    @staticmethod
    def generate_jwt_token(user_id: str, user_type: str) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size"""
        return file_size <= Config.MAX_CONTENT_LENGTH
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_hex(32)
    
    @staticmethod
    def validate_csrf_token(token: str, stored_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, stored_token)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1)
            filename = name[:255-len(ext)-1] + '.' + ext
        return filename
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_license_number(license_number: str) -> bool:
        """Validate license number format"""
        # Remove spaces and convert to uppercase
        license_number = re.sub(r'\s+', '', license_number).upper()
        # Check if it contains only alphanumeric characters and common separators
        return bool(re.match(r'^[A-Z0-9\-\.\/]+$', license_number))
    
    @staticmethod
    def log_security_event(event_type: str, user_id: Optional[str] = None, details: Optional[str] = None):
        """Log security events"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[SECURITY] {timestamp} - {event_type}"
        if user_id:
            log_entry += f" - User: {user_id}"
        if details:
            log_entry += f" - Details: {details}"
        
        # In production, this should go to a proper logging system
        print(log_entry) 