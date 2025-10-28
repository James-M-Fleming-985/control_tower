# Gmail Setup Guide for Feedback 360 Email System

## 🚨 Current Issue
The feedback 360 email system is not working because Gmail SMTP credentials are not configured. When users try to send feedback requests, they see:
```
⚠️ Email not sent to recipient@email.com - SMTP not configured
```

## 📧 Gmail Configuration Steps

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled
3. This is **required** for app passwords

### Step 2: Generate Gmail App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "App passwords" (you may need to search for it)
3. Select "Mail" as the app type
4. Generate a new app password
5. **Save this password** - you'll need it for `SMTP_PASSWORD`

### Step 3: Configure Environment Variables
Edit `/workspaces/control_tower/feedback-collector-mvp/backend/.env`:

```bash
# Gmail/Email Configuration for Feedback 360
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-actual-gmail@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=your-actual-gmail@gmail.com
FROM_NAME=Feedback360
FRONTEND_URL=http://localhost:3000
```

**Example:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=james.feedback360@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=james.feedback360@gmail.com
FROM_NAME=Feedback360
FRONTEND_URL=http://localhost:3000
```

### Step 4: Restart the Backend
```bash
cd /workspaces/control_tower/feedback-collector-mvp/backend
# Kill existing process
pkill -f "python main.py"
# Restart
python main.py
```

### Step 5: Test Email Functionality
```bash
curl -X POST "http://localhost:8000/api/feedback/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "professional",
    "mode": "standard", 
    "emails": ["test@example.com"],
    "custom_message": "Testing Gmail integration"
  }'
```

**Success Response:**
```json
{
  "request_id": "abc123",
  "sent": 1,
  "total": 1,
  "failed": [],
  "message": "Sent to 1/1 recipients"
}
```

**You should see in backend logs:**
```
✅ Email sent to test@example.com
```

## 🔧 Troubleshooting

### Issue: "Authentication failed"
- Double-check your Gmail email and app password
- Make sure 2FA is enabled on your Google account
- Regenerate the app password if needed

### Issue: "Connection refused" or "Network error"
- Check your internet connection
- Gmail might be temporarily blocking connections
- Try again in a few minutes

### Issue: "Emails not being received"
- Check spam/junk folders
- Try sending to a different email address
- Verify the recipient email is correct

### Issue: "SSL/TLS errors"
- The code uses `starttls()` which is correct for Gmail
- Port 587 is the correct port for Gmail SMTP with STARTTLS

## 📊 Testing Checklist

- [ ] Gmail app password generated
- [ ] Environment variables configured
- [ ] Backend restarted
- [ ] Test email sent successfully
- [ ] Email received in recipient's inbox
- [ ] Links in email work correctly
- [ ] Feedback submission works end-to-end

## 🌐 Production Considerations

For production deployment:

1. **Use a dedicated Gmail account** for the service (not personal)
2. **Consider Gmail's sending limits**: 500 emails/day for free accounts
3. **For high volume**, consider switching to:
   - SendGrid
   - Mailgun
   - Amazon SES
   - Postmark

## 🔒 Security Notes

- **Never commit** real passwords to Git
- The `.env` file is in `.gitignore` 
- Use strong, unique app passwords
- Rotate passwords regularly
- Monitor for unusual sending activity

## 📈 Next Steps After Gmail Works

1. Test the full feedback flow:
   - Send feedback request → Email received → Click link → Submit feedback
2. Test with multiple recipients
3. Test different context types (professional, personal, growth)
4. Verify email templates look good in different email clients
5. Set up proper error handling and retry logic

---

**Last Updated:** October 28, 2025  
**Status:** Ready for Gmail configuration