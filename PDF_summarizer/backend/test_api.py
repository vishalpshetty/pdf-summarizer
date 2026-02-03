#!/usr/bin/env python3
"""
Quick test script to verify Anthropic API key and check available models
"""

import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    print("❌ ERROR: ANTHROPIC_API_KEY not found in .env file")
    exit(1)

print(f"✅ API Key found: {ANTHROPIC_API_KEY[:20]}...")
print()

# Initialize client
try:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("✅ Anthropic client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    exit(1)

print()
print("Testing different Claude models...")
print("=" * 60)

# Test different models
models_to_test = [
    "claude-3-haiku-20240307",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-20241022",
]

for model in models_to_test:
    try:
        print(f"\n🧪 Testing: {model}")
        message = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Hello, this model works!'"}
            ]
        )
        response = message.content[0].text
        print(f"   ✅ SUCCESS: {response}")
    except anthropic.NotFoundError as e:
        print(f"   ❌ 404 Not Found - Model not available on your account")
    except anthropic.AuthenticationError as e:
        print(f"   ❌ Authentication Error - Check your API key")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

print()
print("=" * 60)
print("Test complete!")
