---
description: How to run the login system
---

# How to Run the Login System

This guide explains how to run the BES Management System login interface with the new notification system.

## ✨ New Features

- **Modern Notification Bars**: Visual feedback for login/registration success, errors, and info
- **Updated UI**: Uses `loginUi3_revised.ui` for login and `loginUi4_sign_in.ui` for registration
- **Smart Error Messages**: Specific notifications for different error scenarios
- **Smooth Animations**: Slide-in/slide-out notification animations

## Prerequisites

Before running the login system, ensure you have:

1. **Python 3.8+** installed (you have Python 3.12.3 ✅)
2. **Laragon** running with MySQL started
3. **Virtual environment** set up
4. **Database** created and seeded

## Quick Start (Easiest Method)

### Option 1: Using the Windows Batch File

The simplest way to run the application on Windows:

```batch
run_windows.bat
```

This script will automatically:
- Create a virtual environment if needed
- Install all required packages
- Test the database connection
- Launch the login interface

### Option 2: Manual PowerShell Commands

If you prefer manual control:

```powershell
# 1. Navigate to project directory
cd d:\pycharm\BES_MANAGEMENT_SYSTEM

# 2. Activate virtual environment (if exists)
.\venv\Scripts\Activate.ps1

# 3. Install/update dependencies
pip install -r requirements.txt

# 4. Run the application
python gui/run_app.py
```

## First-Time Setup

If this is your first time running the system:

### Step 1: Ensure Laragon MySQL is Running

1. Open **Laragon**
2. Click **Start All** button
3. Verify MySQL is running (green indicator)

### Step 2: Create the Database

Open Laragon's MySQL terminal or HeidiSQL and run:

```sql
CREATE DATABASE IF NOT EXISTS barangay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 3: Initialize Database Tables and Admin Account

```powershell
python scripts/seed_admin.py
```

This creates:
- All necessary database tables
- Default admin account:
  - **Username**: `admin`
  - **Password**: `AdminPass123!`
- Default services

### Step 4: Run the Application

```powershell
python gui/run_app.py
```

## Using the Login Interface

### Login Flow

1. **Enter Credentials**
   - Username: `admin` (or any registered username)
   - Password: `AdminPass123!` (or your password)

2. **Click "Log In" button**

3. **Enter OTP Code**
   - In development mode (`DEV_PRINT_OTP = True`), the OTP will be printed to the console
   - Check the terminal/console window for the 6-digit code
   - Enter the code in the popup dialog

4. **Access Dashboard**
   - After successful OTP verification, you'll be redirected to the dashboard

### Register New Account

1. Click **"Register New Account"** button on the login screen
2. Fill in the registration form
3. Submit to create a new account

### Forgot Password

1. Click **"Forgot Password?"** link
2. Follow the password recovery process

## UI File Information

The login interface uses:
- **UI File**: `gui/ui/loginUi3_revised.ui` (Qt Designer file)
- **Python View**: `gui/views/login_view.py` (Logic implementation)
- **Main Entry**: `gui/run_app.py` (Application launcher)

### UI Components

The login UI (`loginUi3_revised.ui`) contains:
- `lineEdit` - Username input field
- `lineEdit_2` - Password input field (masked)
- `pushButton` - Log In button
- `pushButton_2` - Register New Account button
- `pushButton_3` - Forgot Password button

## Troubleshooting

### Issue: "Database connection failed"

**Solution**: 
- Ensure Laragon is running
- Check MySQL service is started
- Verify database exists: `SHOW DATABASES;`

### Issue: "No module named 'PyQt5'"

**Solution**:
```powershell
pip install PyQt5
```

### Issue: "Could not load UI file"

**Solution**:
- Verify the UI file exists at `gui/ui/login.ui`
- The code references `login.ui` but you have `loginUi3_revised.ui`
- You may need to rename or update the path in `login_view.py`

### Issue: OTP not received

**Solution**:
- In development mode, OTP is printed to console (check terminal)
- For email OTP, configure SMTP settings in `app/config.py`
- Set `DEV_PRINT_OTP = False` for production email sending

### Issue: "Widget not found" errors

**Solution**:
The `login_view.py` expects these widget names in the UI file:
- `inputUsername` - but your UI has `lineEdit`
- `inputPassword` - but your UI has `lineEdit_2`
- `btnLogin` - but your UI has `pushButton`
- `btnRegister` - but your UI has `pushButton_2`

You need to either:
1. Update the UI file widget names in Qt Designer, OR
2. Update `login_view.py` to match your current widget names

## Configuration

### Database Settings

Edit `app/config.py`:
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1:3306/barangay_db"
```

Current settings:
- **Host**: 127.0.0.1 (localhost)
- **Port**: 3306 (MySQL default)
- **User**: root
- **Password**: (empty - Laragon default)
- **Database**: barangay_db

### Email Settings (Optional)

For production email OTP:
```python
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
DEV_PRINT_OTP = False
```

## Next Steps

After successful login:
1. You'll be redirected to the **Dashboard**
2. From there you can access all system features
3. Manage residents, services, appointments, etc.

## File Structure Reference

```
BES_MANAGEMENT_SYSTEM/
├── gui/
│   ├── run_app.py              # Main entry point - START HERE
│   ├── views/
│   │   ├── login_view.py       # Login logic
│   │   ├── register_view.py    # Registration logic
│   │   └── dashboard_view.py   # Dashboard after login
│   └── ui/
│       └── loginUi3_revised.ui # Login UI design (Qt Designer)
├── app/
│   ├── config.py               # Configuration settings
│   ├── controllers/
│   │   └── auth_controllers.py # Authentication logic
│   └── models.py               # Database models
├── scripts/
│   └── seed_admin.py           # Database initialization
├── run_windows.bat             # Windows launcher script
└── requirements.txt            # Python dependencies
```

## Quick Reference Commands

```powershell
# Run the application
python gui/run_app.py

# Or use the batch file
run_windows.bat

# Test database connection
python test_db_connection.py

# Initialize database
python scripts/seed_admin.py

# Install dependencies
pip install -r requirements.txt
```
