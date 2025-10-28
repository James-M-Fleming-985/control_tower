#!/usr/bin/env python3
"""
Test script for Gmail SMTP configuration in Feedback 360 system.
Run this to verify your Gmail credentials work before testing the full system.
"""

import os
import sys
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiosmtplib import SMTP
from dotenv import load_dotenv

async def test_gmail_smtp():
    """Test Gmail SMTP configuration"""
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("FROM_EMAIL", smtp_user)
    from_name = os.getenv("FROM_NAME", "Feedback360")
    
    print("🔧 Testing Gmail SMTP Configuration...")
    print(f"   Host: {smtp_host}")
    print(f"   Port: {smtp_port}")
    print(f"   User: {smtp_user}")
    print(f"   From: {from_name} <{from_email}>")
    print()
    
    # Validate configuration
    if not smtp_user or not smtp_password:
        print("❌ Error: Missing SMTP credentials")
        print("   Please set SMTP_USER and SMTP_PASSWORD in .env file")
        return False
    
    # Get test recipient
    test_email = input("Enter test email address (or press Enter to skip): ").strip()
    if not test_email:
        print("⏭️  Skipping email send test")
        test_email = None
    
    try:
        # Test connection
        print("🔌 Testing SMTP connection...")
        async with SMTP(hostname=smtp_host, port=smtp_port, use_tls=True) as smtp:
            print("✅ SSL connection established")
            
            await smtp.login(smtp_user, smtp_password)
            print("✅ Authentication successful")
            
            if test_email:
                # Send test email
                print(f"📧 Sending test email to {test_email}...")
                
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Feedback360 - Gmail Configuration Test"
                msg["From"] = f"{from_name} <{from_email}>"
                msg["To"] = test_email
                
                text_content = """
Hi there!

This is a test email from your Feedback360 system to verify that Gmail SMTP is working correctly.

If you received this email, your Gmail configuration is working! 🎉

You can now use the Feedback360 system to send feedback request emails.

---
Feedback360° Test Email
                """
                
                html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #3b82f6; color: white; padding: 20px; text-align: center; }
        .content { background: #fff; padding: 20px; border: 1px solid #ddd; }
        .success { color: #10b981; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Feedback360°</h1>
            <p>Gmail Configuration Test</p>
        </div>
        <div class="content">
            <h2>Success! 🎉</h2>
            <p>This is a test email from your Feedback360 system to verify that Gmail SMTP is working correctly.</p>
            <p class="success">If you received this email, your Gmail configuration is working!</p>
            <p>You can now use the Feedback360 system to send feedback request emails.</p>
        </div>
    </div>
</body>
</html>
                """
                
                part1 = MIMEText(text_content, "plain")
                part2 = MIMEText(html_content, "html")
                msg.attach(part1)
                msg.attach(part2)
                
                await smtp.send_message(msg)
                print(f"✅ Test email sent successfully to {test_email}")
                print("   Check your inbox (and spam folder) for the test email")
            
    except Exception as e:
        print(f"❌ SMTP test failed: {e}")
        print()
        print("🔧 Troubleshooting tips:")
        print("   1. Check your Gmail credentials are correct")
        print("   2. Make sure 2-Factor Authentication is enabled")
        print("   3. Generate a new App Password if needed")
        print("   4. Check your internet connection")
        return False
    
    print()
    print("✅ Gmail SMTP configuration test completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_gmail_smtp())