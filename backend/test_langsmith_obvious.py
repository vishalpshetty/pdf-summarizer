#!/usr/bin/env python3
"""
Create multiple obvious test traces in LangSmith
"""

import os
from dotenv import load_dotenv
from langsmith import traceable, Client
import time

# Load environment variables
load_dotenv()

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT_NAME = os.getenv("LANGSMITH_PROJECT_NAME", "pdfanalyser")

print("=" * 60)
print(f"Creating test traces in project: {LANGSMITH_PROJECT_NAME}")
print("=" * 60)

# Set environment variable to ensure LangSmith is enabled
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT_NAME

@traceable(name="OBVIOUS_TEST_TRACE", project_name=LANGSMITH_PROJECT_NAME)
def create_test_trace(message):
    """Function that will appear in LangSmith"""
    time.sleep(0.5)  # Small delay to ensure trace is sent
    return f"Test message: {message}"

# Create multiple traces
print("\nCreating 5 test traces...")
for i in range(1, 6):
    result = create_test_trace(f"Test #{i} - If you see this in LangSmith, it's working!")
    print(f"✅ Trace {i} sent: {result}")
    time.sleep(1)

print("\n" + "=" * 60)
print("✅ All traces sent!")
print(f"\nNow go to LangSmith and look for:")
print(f"  • Project name: {LANGSMITH_PROJECT_NAME}")
print(f"  • Trace name: OBVIOUS_TEST_TRACE")
print(f"  • You should see 5 traces just now")
print(f"\n🔗 URL: https://smith.langchain.com/")
print("=" * 60)

# Try to get project info
try:
    client = Client(api_key=LANGSMITH_API_KEY)
    print("\n📊 Project Info:")
    print(f"   Using API Key: {LANGSMITH_API_KEY[:20]}...")
    print(f"   Project Name: {LANGSMITH_PROJECT_NAME}")
except Exception as e:
    print(f"\n⚠️  Could not get project info: {e}")
