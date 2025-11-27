# BES Management System - Setup Guide

## Issues Found and Fixed

### 1. ✅ Fixed `requirements.txt`
- **Problem**: File contained Python code instead of package dependencies
- **Solution**: Created proper requirements.txt with all necessary packages

### 2. ✅ Fixed `app/config.py` syntax errors
- **Problem 1**: Extra space in `Path(__file__). resolve()` 
- **Problem 2**: Space in database password `StrongPass123! @127.0.0.1`
- **Solution**: Removed syntax errors

## Setup Instructions

### Prerequisites
1. **Python 3.8+** ✅ (You have Python 3.12.3)
2. **MySQL Server** (needs to be installed and running)
3. **pip** (Python package manager)

### Installation Steps

#### Step 1: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows (WSL):
source venv/bin/activate
# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
```

#### Step 2: Install Python Packages
```bash
pip install -r requirements.txt
```

#### Step 3: Set Up MySQL Database
You need to:
1. Install MySQL Server if not already installed
2. Create the database and user:

```sql
CREATE DATABASE barangay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'barangay_user'@'localhost' IDENTIFIED BY 'StrongPass123!';
GRANT ALL PRIVILEGES ON barangay_db.* TO 'barangay_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Step 4: Initialize Database Tables
```bash
python3 scripts/seed_admin.py
```

This will:
- Create all database tables
- Create an admin account (username: `admin`, password: `AdminPass123!`)
- Add default services

#### Step 5: Run the Application
```bash
python3 gui/run_app.py
```

## Configuration

### Email Settings (Optional)
Edit `app/config.py` to configure email:
- Set `SMTP_USERNAME` to your Gmail address
- Set `SMTP_PASSWORD` to your Gmail App Password
- Set `DEV_PRINT_OTP = False` for production

### File Uploads
The system will create these folders automatically:
- `uploads/` - For document uploads
- `backups/` - For database backups

## Testing the Setup

### Test Database Connection
```bash
python3 -c "from app.db import engine; print('Database connection:', engine.connect())"
```

### Test Imports
```bash
python3 -c "from app.models import Resident, Account; print('Models imported successfully')"
```

## Common Issues

### Issue: MySQL not installed
**Solution**: Install MySQL Server
```bash
# On Ubuntu/WSL:
sudo apt update
sudo apt install mysql-server
sudo service mysql start
```

### Issue: Permission denied for MySQL
**Solution**: Check MySQL is running and credentials are correct

### Issue: PyQt5 installation fails
**Solution**: Install system dependencies
```bash
# On Ubuntu/WSL:
sudo apt install python3-pyqt5
```

## Project Structure
```
BES_MANAGEMENT_SYSTEM/
├── app/                    # Core application logic
│   ├── models.py          # Database models
│   ├── db.py              # Database connection
│   ├── config.py          # Configuration
│   ├── auth.py            # Authentication
│   ├── emailer.py         # Email functionality
│   └── controllers/       # Business logic
├── gui/                   # PyQt5 GUI
│   ├── run_app.py        # Main entry point
│   └── views/            # GUI views
├── scripts/              # Utility scripts
│   ├── seed_admin.py    # Database seeding
│   └── backup_db.py     # Database backup
├── tests/               # Unit tests
├── uploads/             # File uploads
├── backups/             # Database backups
└── requirements.txt     # Python dependencies
```

## Next Steps

1. ✅ Install packages: `pip install -r requirements.txt`
2. ⚠️ Set up MySQL database
3. ⚠️ Run database seed script
4. ⚠️ Test the application

## Support

If you encounter any issues:
1. Check that MySQL is running
2. Verify database credentials in `app/config.py`
3. Ensure all packages are installed
4. Check Python version compatibility
