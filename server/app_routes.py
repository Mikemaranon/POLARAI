from flask import render_template, redirect, request, url_for, session, Blueprint, jsonify
from user_m.user_manager import UserManager
from chat_m.chatbot_manager import ChatbotManager
from chat_m.chat import Chat
from data_m.database import USERNAME, PASSWORD, MODEL, CHAT_ID
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
        self.app.add_url_rule("/sites/user-config", "get_userConfig", self.get_userConfig)
        
        # API routes
        self.app.add_url_rule("/sites/training", "get_trainingIndex", self.API_get_trainingIndex, methods=["GET", "POST"])
        self.app.add_url_rule("/sites/polarai", "polarai_chat", self.API_get_model_to_chat, methods=["GET", "POST"])
        self.app.add_url_rule("/api/get-chats", "get_chats", self.API_get_chats, methods=["GET"])
        self.app.add_url_rule("/api/send-message", "send_message", self.API_send_message, methods=["POST"])
        self.app.add_url_rule("/api/get-models", "get_models", self.API_get_models, methods=["POST"])
        self.app.add_url_rule("/api/set-chatId", "set_chatId", self.API_set_chatId, methods=["POST"])
        self.app.add_url_rule("/api/get-singleChat", "get_singleChat", self.API_get_singleChat, methods=["GET"])
        
        self.app.add_url_rule("/api/create-chat", "create_chat", self.API_create_chat, methods=["GET"])
        
    def get_home(self):
        if 'username' not in session:
            return redirect(url_for("login"))
        
        session[MODEL] = None
        session[CHAT_ID] = None
        
        return render_template("index.html", username=session[USERNAME])

    def get_login(self):
        error_message = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = self.user_manager.login(username, password)
            if user:
                session[USERNAME] = user 
                self._send_session_to_managers(session)
                self.chatbot_manager.set_user_bots()
                
                # jwt_token = create_jwt_token(user)
                # MIRAR ESTO
                
                return redirect(url_for("home"))
            else:
                error_message = "incorrect user data, try again"  # error message
        
        return render_template("login.html", error_message=error_message)

    def get_logout(self):
        
        self.user_manager.logout()
        # force a refresh
        response = redirect(url_for("login"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    def get_userConfig(self):
        
        if 'username' not in session:
            return redirect(url_for("login"))
        
        # the user config page must allow the user to configure the model
        # and his profile with custom parameters (wannabe like ChatGPT).
        
        return render_template("sites/user-config.html")
    
    def _send_session_to_managers(self, session):
        self.user_manager.set_session(session)
        self.chatbot_manager.set_session(session)
    
    def get_chats_in_chatbot(self):
        chatbot = self.chatbot_manager.get_chatbot(session[MODEL])
        chats = chatbot.load_chats()
        return chats
    
    # =========================================
    #       API protocols start from here
    # =========================================
    
    def API_get_trainingIndex(self):
        
        if 'username' not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            # Asegura que el request es JSON
            if request.content_type != "application/json":
                return "Unsupported Media Type", 415
            
            data = request.get_json()
            session[MODEL] = data.get('model')
            session[CHAT_ID] = None  # training does not require chats

            # Redirige a la versión GET con el modelo
            return redirect(url_for("get_trainingIndex", model=data.get('model')))

        elif request.method == "GET":
            model = request.args.get("model", "default_model")  # Si no hay modelo, usa uno por defecto
            return render_template("sites/training-index.html", bot_name=model)
    
    def API_get_model_to_chat(self):
        
        if 'username' not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            # Asegura que el request es JSON
            if request.content_type != "application/json":
                return "Unsupported Media Type", 415
            
            data = request.get_json()
            session[MODEL] = data.get('model')
            session[CHAT_ID] = None  # Entra en un nuevo chat

            # Redirige a la versión GET con el modelo
            return redirect(url_for("polarai_chat", model=data.get('model')))

        elif request.method == "GET":
            model = request.args.get("model", "default_model")  # Si no hay modelo, usa uno por defecto
            return render_template("/sites/polarai-chat.html", bot_name=model)
    
    def API_get_chats(self):
        if 'username' not in session:
            return redirect(url_for("login"))
        
        chats = self.get_chats_in_chatbot()

        # Extraer solo 'id' y 'topic' de cada chat
        chats_list = [{"id": chat.id, "topic": chat.topic} for chat in chats]

        return jsonify(chats_list)  # Devolver solo la información necesaria
    
    def API_send_message(self):
        
        if 'username' not in session:
            return jsonify({"message": "Usuario no autenticado"}), 401  # 401 = Unauthorized
        
        data = request.get_json()
    
        bot_name = session[MODEL]
        context = data.get('context') or "none"
        message = data.get('message')
        chat_id = session[CHAT_ID]
        
        if not bot_name or not message or not chat_id:
            return jsonify({"message": "Faltan parámetros necesarios"}), 400
        
        # Llamada al chatbot manager para procesar el mensaje
        response = self.chatbot_manager.manager_send_message(bot_name, context, message, chat_id)
        
        # Aquí puedes retornar la respuesta que desee el bot
        return jsonify({"response": response, "data": bot_name + chat_id})
        
    def API_get_models(self):
        
        if 'username' not in session:
            return jsonify({"message": "Usuario no autenticado"}), 401  # 401 = Unauthorized
    
        try:
            user_bots = self.chatbot_manager.get_user_bots()
            return jsonify({"bots": user_bots})
        except Exception as e:
            return jsonify({"message": str(e)}), 500  # En caso de un error del servidor
    
    def API_set_chatId(self):
        
        data = request.get_json()
        chat_id = data.get("chatId")
    
        # Aquí guardas el chatId en la sesión o base de datos
        session[CHAT_ID] = chat_id
        
        return jsonify({"success": True}), 200
    
    def API_get_singleChat(self):
        
        chats = self.get_chats_in_chatbot()
        
        for chat in chats:
            if chat.id == session[CHAT_ID]:
                return jsonify({"messages": chat.messages})
        
        return jsonify({"error": "Chat no encontrado"}), 404
    
    def API_create_chat(self):
        
        session[CHAT_ID] = Chat._generate_chat_id()
        return jsonify({"success": True}), 200