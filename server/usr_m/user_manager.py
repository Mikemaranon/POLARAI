from werkzeug.security import check_password_hash
from data.database import Database

class UserManager:
    def __init__(self, db: Database):
        self.db = db

    def authenticate(self, username: str, password: str):
        # auth user with username and password
        user = self.db.get_user(username)
        if user and check_password_hash(user["password"], password):
            return True
        return False

    def login(self, username: str, password: str):
        # login and return auth state
        if self.authenticate(username, password):
            return username
        return None
    
    def logout(self, session):
        session.clear()  # clear session
        print("User's session cleared")
        return {'status': 'success'}, 200

