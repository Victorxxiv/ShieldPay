from models.users import User
from models.messages import Messages
from models.transactions import Transactions
from uuid import uuid4
from db.storage import DB
from bcrypt import hashpw, gensalt, checkpw

class UserAuth:
    _db = DB()
    _db.reload()

    def hash_password(self, password):
        # Hash the password using bcrypt
        password_bytes = password.encode('utf-8')
        salt = gensalt()
        hashed_password = hashpw(password_bytes, salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, candidate_password, hashed_password):
        # Verify if the candidate password matches the hashed password
        candidate_password_bytes = candidate_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return checkpw(candidate_password_bytes, hashed_password_bytes)

    def create_user(self, **kwargs):
        # Create a new user with the provided details
        email = kwargs.get('email')
        password = kwargs.get('password')
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        phone_number = kwargs.get('phone_number')
        location = kwargs.get('location')
        role = kwargs.get('is_superuser')
        is_active = kwargs.get('is_active')
        login_time = kwargs.get('last_login')
        password = self.hash_password(password)
        user = User(email=email, password=password, first_name=first_name, last_name=last_name, phone_number=phone_number, location=location, role=role, is_active=is_active, last_login=login_time)
        self._db.add(user)
        self._db.save()
        return user

    def get_user_by_email(self, email):
        # Retrieve a user by their email address
        try:
            return self._db.query(User).filter_by(email=email).first()
        except Exception as e:
            return None

    def get_user_by_phone_number(self, phone_number):
        # Retrieve a user by their phone number
        try:
            return self._db.query(User).filter_by(phone_number=phone_number).first()
        except Exception as e:
            return None

    def get_user_by_id(self, id):
        # Retrieve a user by their ID
        try:
            return self._db.query(User).filter_by(id=id).first()
        except Exception as e:
            return None

    def get_all_users(self):
        # Retrieve all users
        return self._db.query(User).all()

    def delete_user(self, id):
        # Delete a user by their ID
        user = self.get_user_by_id(id)
        self._db.delete(user)
        self._db.save()
        return True

    def update_user(self, id, email, password):
        # Update a user's email and/or password
        try:
            user = self.get_user_by_id(id)
            if user:
                if email:
                    user.email = email
                if password:
                    user.password = self.hash_password(password)
                self._db.save()
                return user
            return None
        except Exception as e:
            return None
