#!/usr/bin/env python3
"""
OpenAI GPT Test Script for BazaarBrain-Pro
Tests the OpenAI API integration
"""

import os
from openai import OpenAI
from config import config

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        print("🔌 Testing OpenAI connection...")
        
        # Test API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Hello from BazaarBrain! Please respond with a brief business tip for small shopkeepers."}
            ],
            max_tokens=150
        )
        
        # Extract and display response
        ai_response = response.choices[0].message.content
        print(f"✅ OpenAI API working!")
        print(f"🤖 Response: {ai_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

def test_business_query():
    """Test a business-specific query"""
    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        print("\n💼 Testing business query...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are BazaarBrain, an AI assistant for small shopkeepers. Provide practical, actionable advice."},
                {"role": "user", "content": "I'm a small grocery store owner. How can I improve my inventory management?"}
            ],
            max_tokens=200
        )
        
        ai_response = response.choices[0].message.content
        print(f"✅ Business query successful!")
        print(f"💡 Advice: {ai_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Business query error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BazaarBrain-Pro OpenAI Test")
    print("=" * 40)
    
    # Validate config first
    try:
        config.validate()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please run setup_api_keys.py first")
        exit(1)
    
    # Test basic connection
    if test_openai_connection():
        # Test business query
        test_business_query()
        print("\n🎉 All OpenAI tests passed!")
    else:
        print("\n❌ OpenAI tests failed. Check your API key and internet connection.")
