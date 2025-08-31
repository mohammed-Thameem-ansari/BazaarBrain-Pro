#!/usr/bin/env python3
"""
Dual LLM Test Script for BazaarBrain-Pro
Compares OpenAI GPT and Google Gemini responses side by side
"""

import time
from openai import OpenAI
import google.generativeai as genai
from config import config

def test_gpt_response(prompt):
    """Get response from OpenAI GPT"""
    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are BazaarBrain, an AI assistant for small shopkeepers. Be concise and practical."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"❌ GPT Error: {e}"

def test_gemini_response(prompt):
    """Get response from Google Gemini"""
    try:
        genai.configure(api_key=config.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"❌ Gemini Error: {e}"

def compare_responses(prompt):
    """Compare responses from both LLMs"""
    print(f"\n🔍 Testing: {prompt}")
    print("=" * 60)
    
    # Get responses from both models
    print("🤖 Getting GPT response...")
    gpt_response = test_gpt_response(prompt)
    
    print("🤖 Getting Gemini response...")
    gemini_response = test_gemini_response(prompt)
    
    # Display responses side by side
    print("\n📊 RESPONSE COMPARISON:")
    print("-" * 30)
    print("🟦 GPT (OpenAI):")
    print(f"   {gpt_response}")
    print("\n🟨 Gemini (Google):")
    print(f"   {gemini_response}")
    print("-" * 30)

def run_test_suite():
    """Run a series of test prompts"""
    test_prompts = [
        "What is 2+2?",
        "How can a small shopkeeper improve their inventory management?",
        "What are the top 3 tips for increasing sales in a grocery store?",
        "Explain the concept of profit margin in simple terms.",
        "What should a shopkeeper do if they're running low on cash?"
    ]
    
    print("🚀 BazaarBrain-Pro Dual LLM Test Suite")
    print("=" * 60)
    print("Testing GPT-4o-mini vs Gemini-1.5-flash")
    print("=" * 60)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 Test {i}/{len(test_prompts)}")
        compare_responses(prompt)
        
        # Small delay between tests
        if i < len(test_prompts):
            time.sleep(1)
    
    print("\n🎉 Test suite completed!")
    print("💡 Compare the responses to see the strengths of each model")

if __name__ == "__main__":
    # Validate config first
    try:
        config.validate()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please run setup_api_keys.py first")
        exit(1)
    
    # Run the test suite
    run_test_suite()
