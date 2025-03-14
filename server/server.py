import json, os
from flask import Flask
from data_m.database import Database
from user_m.user_manager import UserManager
from app_routes import AppRoutes
from chat_m.chatbot_manager import ChatbotManager

CF_FILE = "data/config.json"

class Server:
    def __init__(self, app: Flask):
        self.app = app
        self.app.secret_key = os.urandom(24)
        self.config = self.load_config()
        self.PORT = int(self.config["PORT"])
        self.IP = self.config["IP"]
        
        self.database = self.ini_database()
        self.user_manager = self.ini_user_manager()
        self.app_routes = self.ini_app_routes()

        # Clave secreta para la sesión
        app.secret_key = os.urandom(24)
        
        app.run(debug=True, host=self.IP, port=self.PORT)
        
    # Leer configuración desde data/config.json
    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), CF_FILE)
        with open(config_path, "r") as f:
            return json.load(f)

    def ini_database(self):
        return Database()

    def ini_user_manager(self):
        return UserManager(self.database)
    
    def ini_app_routes(self):
        return AppRoutes(self.app, self.user_manager)
    
    def ini_chatbot_manager(self):
        return ChatbotManager(self.database)