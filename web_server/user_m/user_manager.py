import jwt
import datetime
from werkzeug.security import check_password_hash
from data_m.database import Database
from user_m.user import User

class UserManager:
    def __init__(self, secret_key="your-secret-key"):
        self.db = Database()
        self.users = {}  # Aquí almacenaremos los usuarios por su token
        self.secret_key = secret_key  # Clave secreta para generar y verificar el JWT

    def authenticate(self, username: str, password: str):
        # Autenticación del usuario con nombre de usuario y contraseña
        user = self.db.get_user(username)
        if user and check_password_hash(user["password"], password):
            return True
        return False
    
    def generate_token(self, user_id: int, username: str):
        # 1 hour expiration token
        expiration_time = datetime.datetime + datetime.timedelta(hours=1)
        token = jwt.encode({
            'username': username,
            'exp': expiration_time
        }, self.secret_key, algorithm='HS256')
        return token

    def login(self, username: str, password: str):
        if self.authenticate(username, password):
            user_data = self.db.get_user(username)
            user_id = user_data["id"]

            # generate token
            token = self.generate_token(user_id, username)

            if token not in self.users:
                self.users[token] = User(user_id, username)

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
        if self.verify_token(token):
            return self.users[token]

    def verify_token(self, token):
        # Verificar y decodificar el token, si es válido y no ha expirado
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            if datetime.datetime.fromtimestamp(payload['exp'], tz=datetime.UTC) < datetime.datetime.now(datetime.UTC):
                # if token expired, call logout()
                print("Token expired. Logging out user.")
                self.logout(token)
                return False
            # El token es válido, verificamos si el usuario está en el mapa
            if token in self.users:
                return True  # valid token, existent user
            return False  # unexistent user
        
        except jwt.ExpiredSignatureError:
            return False  # expired
        except jwt.InvalidTokenError:
            return False  # invalid
