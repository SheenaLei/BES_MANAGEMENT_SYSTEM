#!/usr/bin/env python3
"""
Test script to verify BES Management System setup
"""

import sys
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version too old: {version.major}.{version.minor}.{version.micro}")
        print("   Required: Python 3.8+")
        return False

def test_imports():
    """Test if required packages can be imported"""
    print("\nTesting package imports...")
    packages = {
        'sqlalchemy': 'SQLAlchemy',
        'pymysql': 'PyMySQL',
        'passlib': 'Passlib',
        'PyQt5': 'PyQt5',
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Not installed")
            all_ok = False
    
    return all_ok

def test_project_structure():
    """Test if project structure is correct"""
    print("\nTesting project structure...")
    base_dir = Path(__file__).resolve().parent
    
    required_paths = [
        'app/models.py',
        'app/db.py',
        'app/config.py',
        'app/auth.py',
        'app/emailer.py',
        'gui/run_app.py',
        'scripts/seed_admin.py',
        'requirements.txt',
    ]
    
    all_ok = True
    for path in required_paths:
        full_path = base_dir / path
        if full_path.exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path} - Missing")
            all_ok = False
    
    return all_ok

def test_config():
    """Test configuration file"""
    print("\nTesting configuration...")
    try:
        from app.config import SQLALCHEMY_DATABASE_URI, BASE_DIR
        print(f"✅ Config loaded")
        print(f"   Database: {SQLALCHEMY_DATABASE_URI.split('@')[1] if '@' in SQLALCHEMY_DATABASE_URI else 'N/A'}")
        print(f"   Base Dir: {BASE_DIR}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_models():
    """Test if models can be imported"""
    print("\nTesting database models...")
    try:
        from app.models import Resident, Account, Service, Request
        print(f"✅ Models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from app.db import engine
        with engine.connect() as conn:
            print(f"✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Make sure MySQL is running and database is created")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("BES Management System - Setup Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Package Imports", test_imports()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Configuration", test_config()))
    results.append(("Models", test_models()))
    results.append(("Database Connection", test_database_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nTo run the application:")
        print("  python3 gui/run_app.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nRefer to SETUP_GUIDE.md for troubleshooting.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
