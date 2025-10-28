import os
import secrets
from typing import List
from datetime import datetime, timedelta
from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    """Service for sending feedback request emails"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Feedback360")
        self.frontend_url = os.getenv("FRONTEND_URL", "https://frontend-4qlhn5nhq-james-flemings-projects.vercel.app")
    
    async def send_feedback_request(
        self,
        recipient_email: str,
        request_id: str,
        token: str,
        context: str = "professional",
        custom_message: str = ""
    ):
        """Send a feedback request email to a recipient"""
        
        if not self.smtp_user or not self.smtp_password:
            print(f"⚠️ Email not sent to {recipient_email} - SMTP not configured")
            return False
        
        # Generate unique response link
        response_url = f"{self.frontend_url}/respond?token={token}"
        
        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Someone requested your anonymous feedback"
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = recipient_email
        
        # Context-specific greeting
        context_text = {
            "professional": "your professional work",
            "personal": "your relationship with them",
            "growth": "their personal growth journey"
        }.get(context, "you")
        
        # Email body
        text_content = f"""
Hi there,

Someone who values your opinion has requested your anonymous feedback about {context_text}.

{custom_message if custom_message else ''}

Your feedback will be completely anonymous - the requester will never know who said what.

Click here to provide your feedback:
{response_url}

This link is unique to you and will expire in 7 days.

Thank you for taking the time to share your honest thoughts!

---
Feedback360° - 100% Anonymous Feedback
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e5e7eb; border-top: none; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: 600; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 0.875rem; margin-top: 30px; }}
        .custom-message {{ background: #f0f9ff; padding: 15px; border-left: 3px solid #3b82f6; margin: 20px 0; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; font-size: 2rem;">Feedback360°</h1>
            <p style="margin: 10px 0 0 0;">Anonymous Feedback Request</p>
        </div>
        <div class="content">
            <h2>Hi there,</h2>
            <p>Someone who values your opinion has requested your anonymous feedback about <strong>{context_text}</strong>.</p>
            
            {f'<div class="custom-message">{custom_message}</div>' if custom_message else ''}
            
            <p>Your feedback will be <strong>completely anonymous</strong> - the requester will never know who said what.</p>
            
            <center>
                <a href="{response_url}" class="button">Provide Your Feedback</a>
            </center>
            
            <p style="color: #6b7280; font-size: 0.875rem;">This link is unique to you and will expire in 7 days.</p>
            
            <p>Thank you for taking the time to share your honest thoughts!</p>
        </div>
        <div class="footer">
            <p>Feedback360° - 100% Anonymous Feedback</p>
            <p>If you didn't expect this email, you can safely ignore it.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        try:
            async with SMTP(hostname=self.smtp_host, port=self.smtp_port, use_tls=True) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(msg)
            print(f"✅ Email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email to {recipient_email}: {e}")
            return False

# Global email service instance
email_service = EmailService()
