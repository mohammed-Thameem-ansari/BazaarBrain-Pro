import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the appropriate .env file.
# Priority: explicit DOTENV_FILE > .env.production (when ENVIRONMENT=production) > .env
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
dotenv_file = os.getenv("DOTENV_FILE")
if not dotenv_file:
    if ENVIRONMENT == "production" and Path(".env.production").exists():
        dotenv_file = ".env.production"
    elif Path(".env").exists():
        dotenv_file = ".env"

if dotenv_file:
    load_dotenv(dotenv_file)
else:
    # Fallback to loading any default env if present (no-op if none)
    load_dotenv()

class Config:
    """Configuration class for BazaarBrain-Pro"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Google Cloud / Gemini Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    # Accept either SUPABASE_ANON_KEY or SUPABASE_KEY for flexibility
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # App Configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS / Frontend origins (comma-separated)
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")  # single origin convenience
    ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
    if FRONTEND_ORIGIN and FRONTEND_ORIGIN not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(FRONTEND_ORIGIN)
    # Development fallback
    if not ALLOWED_ORIGINS:
        # In dev allow all; in prod default to none unless explicitly set
        ALLOW_ALL_CORS = os.getenv("ALLOW_ALL_CORS", "true" if ENVIRONMENT != "production" else "false").lower() == "true"
        ALLOWED_ORIGINS = ["*"] if ALLOW_ALL_CORS else []
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "OPENAI_API_KEY",
            "GOOGLE_API_KEY", 
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Create global config instance
config = Config()
