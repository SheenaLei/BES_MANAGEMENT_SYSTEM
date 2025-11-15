from models.database import Database
from utils.auth import hash_password

class Resident:
    def __init__(self, resident_id=None, first_name=None, last_name=None, email=None, phone=None, address=None, password=None):
        self.id = resident_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password

    def save(self):
        hashed_pw = hash_password(self.password)
        if self.id:
            query = """UPDATE residents SET first_name=%s, last_name=%s, email=%s, phone=%s, address=%s WHERE resident_id=%s"""
            Database.execute_query(query, (self.first_name, self.last_name, self.email, self.phone, self.address, self.id))
        else:
            query = """INSERT INTO residents (first_name, last_name, email, phone, address, password_hash) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            self.id = Database.execute_query(query, (self.first_name, self.last_name, self.email, self.phone, self.address, hashed_pw))

    @staticmethod
    def authenticate(email, password):
        query = "SELECT * FROM residents WHERE email=%s"
        user = Database.execute_query(query, (email,), fetch=True)
        if user:
            user = user[0]
            if verify_password(password, user['password_hash']):
                return Resident(
                    resident_id=user['resident_id'],
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    email=user['email'],
                    phone=user['phone'],
                    address=user['address']
                )
        return None