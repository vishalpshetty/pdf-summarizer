#!/usr/bin/env python3
"""
Test script to verify LangSmith connection
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT_NAME = os.getenv("LANGSMITH_PROJECT_NAME")

print("=" * 60)
print("LangSmith Configuration Check")
print("=" * 60)

if not LANGSMITH_API_KEY:
    print("❌ LANGSMITH_API_KEY not found in .env file")
else:
    print(f"✅ LANGSMITH_API_KEY found: {LANGSMITH_API_KEY[:20]}...")

if not LANGSMITH_PROJECT_NAME:
    print("❌ LANGSMITH_PROJECT_NAME not found in .env file")
else:
    print(f"✅ LANGSMITH_PROJECT_NAME: {LANGSMITH_PROJECT_NAME}")

print()
print("Now testing LangSmith connection...")
print("=" * 60)

try:
    from langsmith import Client
    
    # Create LangSmith client
    client = Client(api_key=LANGSMITH_API_KEY)
    
    print("✅ LangSmith client created successfully")
    
    # Try to list projects
    print("\nAttempting to connect to LangSmith API...")
    
    # This will create the project if it doesn't exist
    from langsmith import traceable
    import anthropic
    
    @traceable(name="test_trace", project_name=LANGSMITH_PROJECT_NAME)
    def test_function():
        return "Hello from LangSmith test!"
    
    result = test_function()
    print(f"✅ Test trace sent successfully: {result}")
    print(f"\n🎉 Success! Check your LangSmith dashboard for project: {LANGSMITH_PROJECT_NAME}")
    print(f"   URL: https://smith.langchain.com/")
    
except ImportError as e:
    print(f"❌ Failed to import LangSmith: {e}")
    print("   Run: pip install langsmith")
except Exception as e:
    print(f"❌ Error connecting to LangSmith: {e}")
    print("   Check your API key and internet connection")

print("=" * 60)
