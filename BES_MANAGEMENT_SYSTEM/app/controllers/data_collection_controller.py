# app/controllers/data_collection_controller.py
from app.db import SessionLocal
from app.models import Resident, Account
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class DataCollectionController:
    """Controller for handling resident data collection and registration"""
    
    @staticmethod
    def save_resident(data: dict):
        """
        Save resident data from the data collection form.
        After saving, automatically approve any pending account linked to this user.
        
        Args:
            data: Dictionary containing resident information from the form
            
        Returns:
            dict: {"success": True/False, "resident": Resident object, "error": str}
        """
        db = SessionLocal()
        try:
            # Map form field names to database columns
            # You'll need to adjust these based on actual UI field names
            resident_data = {
                'last_name': data.get('lineEdit_lastname', '').strip(),
                'first_name': data.get('lineEdit_firstname', '').strip(),
                'middle_name': data.get('lineEdit_middlename', '').strip(),
                'suffix': data.get('lineEdit_suffix', '').strip() or None,
                
                'gender': data.get('comboBox_gender', 'Male'),
                'birth_date': data.get('dateEdit_birthdate', datetime.now().date()),
                'birth_place': data.get('lineEdit_birthplace', '').strip() or None,
                'civil_status': data.get('comboBox_civilstatus', 'Single'),
                
                'spouse_name': data.get('lineEdit_spouse', '').strip() or None,
                'no_of_children': int(data.get('spinBox_children', 0) or 0),
                'no_of_siblings': int(data.get('spinBox_siblings', 0) or 0),
                'mother_full_name': data.get('lineEdit_mother', '').strip() or None,
                'father_full_name': data.get('lineEdit_father', '').strip() or None,
                
                'nationality': data.get('lineEdit_nationality', 'Filipino').strip(),
                'religion': data.get('lineEdit_religion', '').strip() or None,
                'occupation': data.get('lineEdit_occupation', '').strip() or None,
                'highest_educational_attainment': data.get('comboBox_education', '').strip() or None,
                
                'contact_number': data.get('lineEdit_contact', '').strip() or None,
                'emergency_contact_name': data.get('lineEdit_emergency_name', '').strip() or None,
                'emergency_contact_number': data.get('lineEdit_emergency_contact', '').strip() or None,
                
                'sitio': data.get('comboBox_sitio', '').strip() or None,
                'barangay': data.get('lineEdit_barangay', 'Barangay Balibago').strip(),
                'municipality': data.get('lineEdit_municipality', 'Calatagan').strip(),
                
                'registered_voter': data.get('checkBox_voter', False),
                'indigent': data.get('checkBox_indigent', False),
                'solo_parent': data.get('checkBox_soloparent', False),
                'solo_parent_id_no': data.get('lineEdit_sp_id', '').strip() or None,
                'fourps_member': data.get('checkBox_4ps', False),
            }
            
            # Calculate age from birth_date
            if isinstance(resident_data['birth_date'], datetime):
                birth_date = resident_data['birth_date'].date()
            else:
                birth_date = resident_data['birth_date']
            
            today = datetime.now().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            resident_data['age'] = age
            
            # Create resident
            resident = Resident(**resident_data)
            db.add(resident)
            db.flush()  # Get resident_id
            
            # Check if there's a pending account with matching name
            # This links the newly registered resident to their existing account
            full_name = f"{resident.first_name} {resident.middle_name} {resident.last_name}".strip()
            
            # Try to find and approve pending accounts
            pending_accounts = db.query(Account).filter(
                Account.account_status == 'Pending'
            ).all()
            
            for account in pending_accounts:
                if account.resident and account.resident.full_name().lower() == full_name.lower():
                    # Found matching account - approve it!
                    account.account_status = 'Active'
                    print(f"✅ Auto-approved account for {full_name}")
                    break
            
            db.commit()
            db.refresh(resident)
            
            return {
                "success": True,
                "resident": resident,
                "message": f"Resident {resident.full_name()} registered successfully"
            }
            
        except IntegrityError as e:
            db.rollback()
            return {"success": False, "error": "Resident already exists or database constraint error"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_pending_accounts():
        """Get all pending accounts that need verification"""
        db = SessionLocal()
        try:
            accounts = db.query(Account).filter(
                Account.account_status == 'Pending'
            ).all()
            
            return {"success": True, "accounts": accounts}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def approve_account_by_name(first_name: str, last_name: str):
        """
        Approve a pending account by matching first and last name.
        Used when admin registers a resident at the Barangay Hall.
        """
        db = SessionLocal()
        try:
            # Find resident by name
            resident = db.query(Resident).filter(
                Resident.first_name == first_name,
                Resident.last_name == last_name
            ).first()
            
            if not resident:
                return {"success": False, "error": "Resident not found"}
            
            # Find associated account
            if resident.account:
                if resident.account.account_status == 'Pending':
                    resident.account.account_status = 'Active'
                    db.commit()
                    return {
                        "success": True,
                        "message": f"Account approved for {resident.full_name()}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Account is already {resident.account.account_status}"
                    }
            else:
                return {"success": False, "error": "No account found for this resident"}
                
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
