from flask import render_template, redirect, request, url_for, session, Blueprint, jsonify
from user_m.user_manager import UserManager
from chat_m.chatbot_manager import ChatbotManager
from main import app

class AppRoutes:
    def __init__(self, app, api, user_manager: UserManager, chatbot_manager: ChatbotManager):
        self.app = app
        self.api = api
        self.user_manager = user_manager
        self.chatbot_manager = chatbot_manager
        self._register_routes()

    def _register_routes(self):
        self.app.add_url_rule("/", "home", self.get_home)
        self.app.add_url_rule("/login", "login", self.get_login, methods=["GET", "POST"])
        self.app.add_url_rule("/logout", "logout", self.get_logout)
        self.app.add_url_rule("/sites/polarai", "get_chat", self.get_chat)
        self.app.add_url_rule("/sites/training", "get_trainingIndex", self.get_trainingIndex)
        self.app.add_url_rule("/sites/user-config", "get_userConfig", self.get_userConfig)
        
        # API routes
        self.app.add_url_rule("/api/send-message", "send-message", self.API_send_message, methods=["POST"])
        self.app.add_url_rule("/api/get-models", "get-models", self.API_get_models, methods=["POST"])
        
    def get_home(self):
        if 'username' not in session:
            return redirect(url_for("login"))
        return render_template("index.html", username=session['username'])

    def get_login(self):
        error_message = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = self.user_manager.login(username, password)
            if user:
                session['username'] = user # Guardamos al usuario en la sesión
                self._send_session_to_managers(session)
                self.chatbot_manager.set_user_bots()
                
                # jwt_token = create_jwt_token(user)
                # MIRAR ESTO
                
                return redirect(url_for("home"))
            else:
                error_message = "incorrect user data, try again"  # Mensaje de error
        
        return render_template("login.html", error_message=error_message)

    def get_logout(self):
        
        self.user_manager.logout()
        # force a refresh
        response = redirect(url_for("login"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    def get_chat(self):
        
        if 'username' not in session:
            return redirect(url_for("login"))
        
        # get logic for personal user model instance
        # if non-existent, create new model instance
        
        # the polaria chat page is only a GUI for the communication 
        # between the user and the model. No logic is implemented in here.
        
        return render_template("sites/polarai-chat.html")
    
    def get_trainingIndex(self):
        
        if 'username' not in session:
            return redirect(url_for("login"))
        
        # get logic for personal user model instance
        # if non-existent, create new model instance
        
        # the training page must implement direct interaction with the model
        # by allowing the user to train the model with custom data.
        
        return render_template("sites/training-index.html")
    
    def get_userConfig(self):
        
        if 'username' not in session:
            return redirect(url_for("login"))
        
        # the user config page must allow the user to configure the model
        # and his profile with custom parameters (wannabe like ChatGPT).
        
        return render_template("sites/user-config.html")
    
    def API_send_message(self, bot_name, context, message, chat_id):
        
        if 'username' not in session:
            return jsonify({"message": "Usuario no autenticado"}), 401  # 401 = Unauthorized
        
        data = request.get_json()
    
        bot_name = data.get('bot_name')
        context = data.get('context')
        message = data.get('message')
        chat_id = data.get('chat_id')
        
        if not bot_name or not message or not chat_id:
            return jsonify({"message": "Faltan parámetros necesarios"}), 400
        
        # Llamada al chatbot manager para procesar el mensaje
        response = self.chatbot_manager.manager_send_message(bot_name, context, message, chat_id)
    
        # Aquí puedes retornar la respuesta que desee el bot
        return jsonify({"response": response})
        
    def API_get_models(self):
        
        if 'username' not in session:
            return jsonify({"message": "Usuario no autenticado"}), 401  # 401 = Unauthorized
    
        try:
            user_bots = self.chatbot_manager.get_user_bots()
            return jsonify({"bots": user_bots})
        except Exception as e:
            return jsonify({"message": str(e)}), 500  # En caso de un error del servidor
    
    def _send_session_to_managers(self, session):
        self.user_manager.set_session(session)
        self.chatbot_manager.set_session(session)