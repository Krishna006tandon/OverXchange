import os
import tempfile
from datetime import timedelta

class Config:
    """Secure configuration for the application"""
    
    # Security Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_strong_random_secret_key_for_overxchange_2025_august_23_cli_agent_generated_1234567890'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another_super_strong_jwt_secret_key_for_overxchange_2025_august_23_cli_agent_generated_0987654321'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database Settings
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'OverXchange'
    
    # CORS Settings - Restrict to specific origins in production
    ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', 'http://localhost:8080', 'http://127.0.0.1:8080']
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour;10 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # File Upload Security
    if os.environ.get('FLASK_ENV') == 'development':
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    else:
        UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://accounts.google.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https://api.mongodb.com https://accounts.google.com https://cdn.jsdelivr.net;"
    }
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Password Security
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # API Security
    API_RATE_LIMIT = "100 per hour"
    API_KEY_HEADER = 'X-API-Key'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Development vs Production
    DEBUG = os.environ.get('FLASK_ENV') == 'development'


    
    @staticmethod
    def init_app(app):
        """Initialize security settings for the app"""
        # Set security headers
        @app.after_request
        def add_security_headers(response):
            for header, value in Config.SECURITY_HEADERS.items():
                response.headers[header] = value
            return response

        # Create upload folder if it doesn't exist
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder and not os.path.exists(upload_folder):
            os.makedirs(upload_folder)