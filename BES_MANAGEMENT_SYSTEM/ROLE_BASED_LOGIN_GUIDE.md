# Role-Based Login System - Implementation Guide

## Overview
The BES Management System now implements a complete role-based login system that differentiates between Admin and User (Resident) access.

## System Flow

### 1. **User Registration Flow**
Users CANNOT create accounts without first being registered as residents by the admin.

**Steps:**
1. User clicks "Register New Account" on login screen
2. User fills in their information (name, username, password)
3. **VALIDATION**: System checks if user exists in `residents` table
   - If NOT found → Registration BLOCKED with message to visit Barangay Hall
   - If found BUT already has account → Registration BLOCKED, directed to login
   - If found AND no account → Registration proceeds
4. Account is created with `user_role='Resident'` and `account_status='Active'`
5. User can now login immediately

### 2. **Admin Registration Flow (Manual)**
Only admins can add residents to the system:

**Steps:**
1. Admin logs in
2. Admin navigates to "RESIDENTS" section
3. Admin clicks "ADD RESIDENT" button
4. Admin fills in resident information in Data Collection form
5. Resident is added to `residents` table
6. **NOW** this person can create a user account via the registration page

### 3. **Login Flow**

**For ALL Users:**
1. Enter username and password
2. System validates credentials
3. OTP is generated and displayed in console (DEV mode)
4. User enters OTP code
5. **Role Check**: System checks `user_role` in `accounts` table
6. Redirect to appropriate dashboard:
   - `Admin` or `Staff` → **Admin Dashboard** (sidebarhomee.ui)
   - `Resident` → **User Dashboard** (sidebarhomee_USER.ui)

## Dashboard Interfaces

### Admin Dashboard (`sidebarhomee.ui`)
**Features:**
- Residents Management (Add, Edit, View)
- Services Management
- Document Verification
- Payment Verification
- Announcements
- Reports
- Full System Access

### User Dashboard (`sidebarhomee_USER.ui`)
**Features:**
- Dashboard (Personal Info)
- Services (Request Services)
- Notifications
- Announcements
- My Requests (Track Status)
- Payment (Upload Payment Proofs)
- History
- Blotter (View Incidents)
- Officials (View Barangay Officials)
- All About (Barangay Information)
- Profile/Logout

## Database Schema

### `residents` Table
Contains all registered residents of the barangay.
- Added ONLY by admin through Residents interface
- Required fields: first_name, last_name, gender, birth_date, civil_status
- Each resident can have ONE account

### `accounts` Table
Contains user accounts for login.
- `resident_id` → Links to residents table
- `username` → Unique login identifier
- `password_hash` → Encrypted password
- `user_role` → 'Admin', 'Staff', or 'Resident'
- `account_status` → 'Active', 'Deactivated', or 'Pending'

## Security Features

### 1. **Resident Validation**
- Users cannot create accounts unless they exist in residents table
- Prevents unauthorized account creation
- Ensures only verified residents can access the system

### 2. **Role-Based Access Control**
- Admin/Staff see admin interface with full permissions
- Residents see limited user interface
- Each role has appropriate features and restrictions

### 3. **OTP Verification**
- Two-factor authentication for all logins
- OTP expires after use
- OTP has time limit (configurable in config.py)

### 4. **Account Status**
- Accounts can be deactivated by admin
- Deactivated accounts cannot login
- Pending accounts (if any) require admin approval

## File Structure

```
gui/
├── views/
│   ├── login_view.py              # Login with role-based routing
│   ├── register_view.py           # Registration with resident validation
│   ├── sidebar_home_view.py       # ADMIN dashboard
│   └── sidebar_home_user_view.py  # USER dashboard (NEW)
├── ui/
│   ├── loginUi3_revised.ui        # Login interface
│   ├── loginUi4_sign_in.ui        # Registration form
│   ├── sidebarhomee.ui            # Admin dashboard UI
│   └── sidebarhomee_USER.ui       # User dashboard UI
└── widgets/
    └── notification_bar.py        # Universal notifications

app/
├── controllers/
│   └── auth_controllers.py        # Authentication logic
├── models.py                       # Database models
└── config.py                       # Configuration

```

## Testing Instructions

### Test 1: Admin Login
1. Run: `python gui/run_app.py`
2. Login with:
   - Username: `admin`
   - Password: `AdminPass123!`
3. Enter OTP from console
4. **Expected**: Admin dashboard (sidebarhomee.ui) appears

### Test 2: New User Registration (Should Fail)
1. Click "Register New Account"
2. Enter random name not in database
3. Click Register
4. **Expected**: Error message about visiting Barangay Hall

### Test 3: Admin Adds Resident
1. Login as admin
2. Click "RESIDENTS" button
3. Click "ADD RESIDENT"
4. Fill in resident information:
   - First Name: John
   - Last Name: Doe
   - Gender: Male
   - Birth Date: 1990-01-01
   - Civil Status: Single
5. Click Submit
6. **Expected**: Resident added to database

### Test 4: Resident Creates Account
1. Logout from admin
2. Click "Register New Account"
3. Enter matching name:
   - First Name: John
   - Last Name: Doe
4. Choose username and password
5. Click Register
6. **Expected**: Account created successfully

### Test 5: Resident Login
1. Login with new username/password
2. Enter OTP from console
3. **Expected**: User dashboard (sidebarhomee_USER.ui) appears

## Key Points

✅ **Admins must add residents first**
- Use Residents → Add Resident interface
- Fill in complete resident information
- This creates entry in `residents` table

✅ **Residents can then create accounts**
- System validates against `residents` table
- Matches by first_name, last_name, (middle_name if provided)
- Links account to existing resident record

✅ **Login redirects based on role**
- Admin/Staff → Admin Dashboard
- Resident → User Dashboard
- Automatic based on `user_role` field

✅ **Security enforced at multiple levels**
- Registration validation
- Role-based routing
- OTP verification
- Account status checking

## Common Issues & Solutions

### Issue: "You must be registered at Barangay Hall"
**Solution**: Admin must first add this person as a Resident

### Issue: "Account already exists for this resident"
**Solution**: Person should use login page, not registration

### Issue: "Multiple residents found"
**Solution**: Visit Barangay Hall to verify identity (suggests data cleanup needed)

### Issue: Wrong dashboard appears
**Solution**: Check `user_role` in database, should be 'Admin', 'Staff', or 'Resident'

## Next Steps

1. **Implement User Dashboard Pages**
   - Services request page
   - Payment upload page
   - Request tracking page
   - Profile management

2. **Add Admin Features**
   - Resident approval workflow
   - Document verification interface
   - Payment verification interface

3. **Enhanced Security**
   - Password complexity requirements
   - Session timeout
   - Login attempt limiting

4. **User Experience**
   - Forgot password flow
   - Email notifications
   - Real-time OTP sending

---
**Date:** December 2, 2025
**System:** BES Management System v2.0
**Author:** Antigravity AI Assistant
