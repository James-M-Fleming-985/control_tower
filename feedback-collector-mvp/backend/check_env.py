#!/usr/bin/env python3
"""Quick test to verify environment variables are loaded correctly"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔧 Environment Variables Check:")
print(f"SMTP_HOST: {os.getenv('SMTP_HOST', 'NOT SET')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'NOT SET')}")
print(f"SMTP_USER: {os.getenv('SMTP_USER', 'NOT SET')}")
print(f"SMTP_PASSWORD: {'SET' if os.getenv('SMTP_PASSWORD') else 'NOT SET'}")
print(f"FROM_EMAIL: {os.getenv('FROM_EMAIL', 'NOT SET')}")
print(f"FROM_NAME: {os.getenv('FROM_NAME', 'NOT SET')}")

# Test if credentials look correct
smtp_user = os.getenv('SMTP_USER', '')
smtp_password = os.getenv('SMTP_PASSWORD', '')

if smtp_user and smtp_password:
    print("✅ Gmail credentials appear to be configured")
else:
    print("❌ Gmail credentials missing")