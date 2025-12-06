# OTP Email System - Complete Guide

## 📧 Where Does the OTP Go?

### **Current Setup: Development Mode**

**Configuration:** `app/config.py` line 19
```python
DEV_PRINT_OTP = True  # OTP printed to console, NOT emailed
```

### **Answer: OTP Goes to the CONSOLE/TERMINAL** ✅

When you log in, the OTP appears in the **PowerShell/Terminal window** where you ran:
```powershell
python gui/run_app.py
```

**Example Output:**
```
==================================================
🔐 [DEV OTP] Username: admin
🔐 Code: 654321
🔐 Purpose: login
🔐 Expires: 2025-11-30 14:30:00
==================================================
```

---

## 🔄 **Complete Login Flow**

### **Step-by-Step:**

1. **Run the application:**
   ```powershell
   python gui/run_app.py
   ```

2. **In the GUI:**
   - Enter username: `admin`
   - Enter password: `AdminPass123!`
   - Click "Log In"

3. **Look at the Terminal/Console:**
   - You'll see the OTP code printed
   - Example: `🔐 Code: 123456`

4. **Back in the GUI:**
   - A dialog will pop up asking for OTP
   - Enter the 6-digit code from the console
   - Click OK

5. **Success!** 🎉
   - Green notification: "Login successful!"
   - Dashboard opens

---

## 📝 **For Registration**

### **Current Email Handling:**

When you register a new account through the GUI:

**Code:** `gui/views/register_view.py` line 229
```python
email = f"{username}@barangay.local"
```

**Example:**
- Username: `johndoe`
- Email stored: `johndoe@barangay.local`

**This is a placeholder email** - it's saved to the database but no real email is sent.

### **Why Use Placeholder Emails?**

1. ✅ **Easy testing** - no email setup required
2. ✅ **Fast development** - focus on functionality first
3. ✅ **No costs** - no email service needed
4. ✅ **Privacy** - no real emails during testing

---

## 🚀 **To Enable Real Email Sending**

### **Option 1: Use Gmail (Recommended for Testing)**

#### **Step 1: Get Gmail App Password**

1. Go to your Gmail account
2. Enable 2-Factor Authentication (required)
3. Visit: https://myaccount.google.com/apppasswords
4. Select "Mail" and your device
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

#### **Step 2: Update Configuration**

Edit `app/config.py`:

```python
# SMTP Email Settings
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"        # Your Gmail address
SMTP_PASSWORD = "abcdefghijklmnop"            # 16-char app password (no spaces)
EMAIL_USE_TLS = True
EMAIL_FROM_NAME = "Barangay Balibago E-Services"

# IMPORTANT: Set to False to enable email sending
DEV_PRINT_OTP = False  # Change from True to False
```

#### **Step 3: Add Email Field to Registration UI**

You'll need to modify `loginUi4_sign_in.ui` in Qt Designer to add an email input field, or update the registration code to prompt for email.

---

## 📊 **Email Flow Comparison**

### **Development Mode (Current):**
```
User logs in
    ↓
System generates OTP
    ↓
OTP printed to CONSOLE ← You look here!
    ↓
User copies OTP from console
    ↓
User enters OTP in dialog
    ↓
Login successful!
```

### **Production Mode (Future):**
```
User logs in
    ↓
System generates OTP
    ↓
OTP sent to USER'S EMAIL ← Real email!
    ↓
User checks their email
    ↓
User enters OTP from email
    ↓
Login successful!
```

---

## 🎯 **Current Email Addresses in Database**

### **Admin Account:**
- **Username:** `admin`
- **Email:** Stored in the `residents` table linked to the account
- **OTP Destination:** Console (dev mode)

### **New Registrations:**
- **Email Format:** `{username}@barangay.local`
- **Example:** `testuser@barangay.local`
- **OTP Destination:** Console (dev mode)

---

## 💡 **Recommendations**

### **For Now (Development/Testing):**

✅ **Keep current setup:**
- `DEV_PRINT_OTP = True`
- Look for OTP in console/terminal
- Use placeholder emails for registration
- Fast and easy testing!

### **For Production (When Ready):**

🔄 **Enable email sending:**
1. Set `DEV_PRINT_OTP = False`
2. Configure Gmail SMTP credentials
3. Add real email field to registration form
4. Test email delivery
5. Consider email service like SendGrid for better reliability

---

## 🧪 **Test It Now**

### **Quick Test:**

1. **Open TWO windows:**
   - Window 1: Your application (GUI)
   - Window 2: PowerShell/Terminal (where you ran the app)

2. **In the GUI (Window 1):**
   - Enter: `admin` / `AdminPass123!`
   - Click "Log In"

3. **In the Terminal (Window 2):**
   - Look for the OTP code
   - You'll see: `🔐 Code: XXXXXX`

4. **Copy the code and paste it in the GUI**

5. **Success!** ✅

---

## 📞 **Summary**

**Q: Where does the OTP go?**
**A:** To the **console/terminal** where you ran `python gui/run_app.py`

**Q: What email is used for new registrations?**
**A:** Placeholder format: `{username}@barangay.local`

**Q: How do I enable real email sending?**
**A:** Set `DEV_PRINT_OTP = False` and configure Gmail SMTP in `app/config.py`

**Q: Is this secure for production?**
**A:** For production, you should:
- Enable real email sending
- Use proper email addresses
- Consider professional email service (SendGrid, AWS SES, etc.)
- Add email verification during registration

---

## 🎓 **Pro Tip**

Keep **both windows visible** side-by-side when testing:
```
┌─────────────────┐  ┌─────────────────┐
│   GUI Window    │  │  Terminal       │
│                 │  │                 │
│  [Login Form]   │  │  🔐 OTP: 123456│ ← Copy this!
│                 │  │                 │
│  [Enter OTP]    │  │                 │
└─────────────────┘  └─────────────────┘
```

This makes it super easy to copy the OTP code! 🎯
