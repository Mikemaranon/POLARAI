import jwt
import datetime
from werkzeug.security import check_password_hash
from data_m.database import Database
from user_m.user import User

class UserManager:
    
    # static ini
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UserManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance
    
    def __init__(self, secret_key="your-secret-key"):
        self.db = Database()
        self.users = {}  # store users by token
        self.secret_key = secret_key  # key to handle and generate JWT
        
    # ================ class content ================ #

    def authenticate(self, username: str, password: str):
        # Autenticación del usuario con nombre de usuario y contraseña
        user = self.db.get_user(username)
        if user and check_password_hash(user["password"], password):
            return True
        return False
    
    def generate_token(self, username: str):
        # 1 hour expiration token
        expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        token = jwt.encode({
            'username': username,
            'exp': expiration_time
        }, self.secret_key, algorithm='HS256')
        return token

    def login(self, username: str, password: str):
        if self.authenticate(username, password):
            token = self.generate_token(username)
            self.users[username] = User(token, username)
                
            return token # return the token
        return None

    def logout(self, token):
        # delete user by his token
        if token in self.users:
            del self.users[token]
            print(f"User's session with token {token} cleared")
            return {'status': 'success'}, 200
        return {'status': 'not found'}, 404

    def get_user(self, token):
        x = self.verify_token(token)
        if x:
            print("TRUE")
            return x
        return None

    def verify_token(self, token):
        try:
            print("VERIFYING TOKEN: ", token)
            for user in self.users.values():
                print("user TOKEN: ", user.token)
                if token == user.token:
                    print("USER EXIST")
                    return user  # valid token, existent user
            print("USER DONT EXIST")
            return False  # unexistent user
        
        except jwt.ExpiredSignatureError:
            print("ERROR: Token expired")
            return False  
        except jwt.InvalidTokenError:
            print("ERROR: Invalid token")
            return False  

    def get_users(self):
        return self.users