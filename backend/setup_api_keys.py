#!/usr/bin/env python3
"""
API Key Setup Script for BazaarBrain-Pro
This script helps you collect and test your API keys
"""

import os
from config import config

def create_env_file():
    """Create .env file with template"""
    env_content = """# BazaarBrain-Pro Environment Variables
# Fill in your actual API keys below

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Google Cloud / Gemini API  
GOOGLE_API_KEY=your_google_api_key_here

# Supabase
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# App Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("📝 Please edit .env and add your actual API keys")

def get_api_keys():
    """Get API keys from user input"""
    print("\n🔑 Let's collect your API keys:")
    
    # OpenAI
    openai_key = input("Enter your OpenAI API key: ").strip()
    if openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
    
    # Google
    google_key = input("Enter your Google Cloud API key: ").strip()
    if google_key:
        os.environ['GOOGLE_API_KEY'] = google_key
    
    # Supabase
    supabase_url = input("Enter your Supabase project URL: ").strip()
    if supabase_url:
        os.environ['SUPABASE_URL'] = supabase_url
    
    supabase_anon = input("Enter your Supabase anon key: ").strip()
    if supabase_anon:
        os.environ['SUPABASE_ANON_KEY'] = supabase_anon
    
    supabase_service = input("Enter your Supabase service role key (optional): ").strip()
    if supabase_service:
        os.environ['SUPABASE_SERVICE_ROLE_KEY'] = supabase_service

def test_config():
    """Test if configuration is valid"""
    try:
        config.validate()
        print("✅ All required environment variables are set!")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BazaarBrain-Pro API Key Setup")
    print("=" * 40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        create_env_file()
        print("\n📋 Please edit the .env file with your API keys")
        print("   Then run this script again to test them")
    else:
        print("📁 .env file already exists")
        
        # Try to load and test
        if test_config():
            print("🎉 Configuration is ready!")
        else:
            print("⚠️  Some API keys are missing. Please check your .env file")
