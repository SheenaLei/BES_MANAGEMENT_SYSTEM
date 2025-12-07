# Barangay E-Services Management System

A desktop/web-assisted system for streamlining barangay services: resident registration, document requests, blotter logging, announcements, and notifications. Built for course requirements in **Object-Oriented Programming (OOP)**, **Advanced Computer Programming**, and **Database Management Systems**.

## Project Contributors
- Benitez, John Kester A.
- Delmo, Sheena Lei M.
- Gomez, John Marie L.

## What this project is about
The system digitizes barangay processes so residents can request documents, track requests, and receive updates, while officials manage records securely. It replaces manual paperwork with a centralized, automated workflow.

## Key Features
- Resident portal with authentication (email/OTP) and role-based access.
- Online requests for barangay documents (e.g., clearance, indigency) with status tracking.
- Blotter logging and history for incidents.
- Announcements and premium/notification modules for residents.
- Officials management and data collection tooling.
- Database setup and migration scripts for schema changes.
- GUI built with PyQt (Qt Designer .ui files) for admin and user flows.

## Technology Stack
- Python 3
- PyQt for the GUI; Qt Designer for UI definitions
- SQLite/MySQL (via provided SQL scripts) for persistence
- Email/OTP utilities for verification

## Getting Started
1. Create and activate a virtual environment (Windows example):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Initialize the database using the SQL scripts in `db/` (e.g., `schema.sql`, updates/migrations).
4. Seed data (optional): run scripts like `scripts/seed_admin.py`, `create_test_user.py`, or `seed_user_transactions.py` as needed.
5. Launch the application:
   ```powershell
   python gui/run_app.py
   ```

## Repository Structure (high level)
- `app/` — core application modules (auth, db, models, controllers)
- `gui/` — PyQt entrypoint and Qt Designer `.ui` files for admin/user views
- `db/` — schema and migration SQL scripts
- `scripts/` — utilities for backups and seeding data
- `tests/` — automated tests for auth/setup
- root `*.py` — helper scripts for migrations, validation, and maintenance

## Notes
- Customize database connection and email settings in config modules before deployment.
- Use the provided update scripts when altering the schema to keep migrations consistent.
- OTP/email features require valid SMTP configuration.
