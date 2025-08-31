#!/usr/bin/env python3
"""
Google Gemini Test Script for BazaarBrain-Pro
Tests the Google Gemini API integration
"""

import google.generativeai as genai
from config import config

def test_gemini_connection():
    """Test Gemini API connection"""
    try:
        # Configure Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        print("🔌 Testing Gemini connection...")
        
        # Test basic API call
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello from BazaarBrain! Please respond with a brief business tip for small shopkeepers.")
        
        print(f"✅ Gemini API working!")
        print(f"🤖 Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False

def test_business_analysis():
    """Test business analysis capabilities"""
    try:
        genai.configure(api_key=config.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        print("\n💼 Testing business analysis...")
        
        prompt = """
        As BazaarBrain, an AI assistant for small shopkeepers, analyze this scenario:
        
        A small grocery store has these sales data:
        - Monday: $150 in sales
        - Tuesday: $180 in sales  
        - Wednesday: $120 in sales
        - Thursday: $200 in sales
        - Friday: $250 in sales
        
        Provide 2-3 insights about this pattern and suggest one improvement action.
        """
        
        response = model.generate_content(prompt)
        
        print(f"✅ Business analysis successful!")
        print(f"💡 Analysis: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Business analysis error: {e}")
        return False

def test_structured_output():
    """Test structured output capabilities"""
    try:
        genai.configure(api_key=config.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        print("\n📊 Testing structured output...")
        
        prompt = """
        As BazaarBrain, provide a structured response for inventory management:
        
        Format your response as:
        1. Key Challenge: [identify main issue]
        2. Solution: [provide actionable solution]
        3. Expected Outcome: [what this will achieve]
        
        Topic: Managing perishable goods in a small store
        """
        
        response = model.generate_content(prompt)
        
        print(f"✅ Structured output successful!")
        print(f"📋 Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Structured output error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BazaarBrain-Pro Gemini Test")
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
    if test_gemini_connection():
        # Test business analysis
        test_business_analysis()
        
        # Test structured output
        test_structured_output()
        
        print("\n🎉 All Gemini tests passed!")
    else:
        print("\n❌ Gemini tests failed. Check your API key and internet connection.")
