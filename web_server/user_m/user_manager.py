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
            # generate token
            token = self.generate_token(username)

            if token not in self.users:
                self.users[token] = User(username)
                print("user created: ", self.users[token].username)
                print("with exp: ", jwt.decode(token, self.secret_key, algorithms=['HS256'])['exp'])
                print("with token: ", token)
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
        
        print("token:", token)
        
        if self.verify_token(token):
            return self.users[token]

    def verify_token(self, token):
        try:
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            print("alo")
            exp_time = datetime.datetime.fromtimestamp(payload['exp'], tz=datetime.timezone.utc)
            print("aloooooooooooooo")
            
            if exp_time < datetime.datetime.now(datetime.timezone.utc):
                # if token expired, call logout()
                print("Token expired. Logging out user.")
                self.logout(token)
                return False
            if token in self.users:
                print("TOKEN EXIST")
                return True  # valid token, existent user
            print("USER DONT EXIST")
            return False  # unexistent user
        
        except jwt.ExpiredSignatureError:
            print("ERROR 1")
            return False  # expired
        except jwt.InvalidTokenError:
            print("ERROR 2")
            return False  # invalid
