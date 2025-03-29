import jwt
from flask import render_template, redirect, request, url_for, jsonify
from user_m.user_manager import UserManager
from chat_m.chatbot_manager import ChatbotManager
from chat_m.chat import Chat
from data_m.database import USERNAME, PASSWORD, MODEL, CHAT_ID
from main import app

class AppRoutes:
    def __init__(self, app, user_manager: UserManager, chatbot_manager: ChatbotManager):
        self.app = app
        self.user_manager = user_manager
        self.chatbot_manager = chatbot_manager
        self._register_routes()

    def _register_routes(self):
        self.app.add_url_rule("/", "home", self.get_home, methods=["POST"])
        self.app.add_url_rule("/login", "login", self.get_login, methods=["GET", "POST"])
        self.app.add_url_rule("/logout", "logout", self.get_logout, methods=["POST"])
        self.app.add_url_rule("/sites/user-config", "get_userConfig", self.get_userConfig, methods=["POST"])
        
        # API routes
        self.app.add_url_rule("/sites/training", "get_trainingIndex", self.API_get_trainingIndex, methods=["GET", "POST"])
        self.app.add_url_rule("/sites/polarai", "polarai_chat", self.API_get_model_to_chat, methods=["GET", "POST"])
        self.app.add_url_rule("/api/get-chats", "get_chats", self.API_get_chats, methods=["GET"])
        self.app.add_url_rule("/api/send-message", "send_message", self.API_send_message, methods=["POST"])
        self.app.add_url_rule("/api/get-models", "get_models", self.API_get_models, methods=["POST"])
        self.app.add_url_rule("/api/set-chatId", "set_chatId", self.API_set_chatId, methods=["POST"])
        self.app.add_url_rule("/api/get-singleChat", "get_singleChat", self.API_get_singleChat, methods=["GET"])
        
        self.app.add_url_rule("/api/create-chat", "create_chat", self.API_create_chat, methods=["GET"])
        self.app.add_url_rule("/api/get-last-summary", "get_lastSummary", self.API_get_last_summary, methods=["GET"])
        
        self.app.add_url_rule("/api/set-chat-config", "set_chatConfig", self.API_set_chat_config, methods=["POST"])
        
    def get_request_token():
        
        # 1. Intentar obtener el token del header Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        # 2. Intentar obtener el token del body JSON
        if request.is_json:
            json_data = request.get_json(silent=True)  # Evita errores si no hay JSON
            if json_data and "token" in json_data:
                return json_data["token"]

        # 3. Intentar obtener el token desde los parámetros de la URL (query string)
        token = request.args.get("token")
        if token:
            return token

        # Si no se encontró el token, devolver None
        return None

        
    def get_home(self):
        
        data = request.get_json()
        token = data.get("token")
        
        if not token or token not in self.user_manager.users:
            return redirect(url_for("login"))
        
        user = self.user_manager.users[token]
        user.model = None
        user.chat_id = None
        
        return render_template("index.html", username=user.username)

    def get_login(self, token=None):
        error_message = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            token = self.user_manager.login(username, password)
            if token:
                # render home with token
                return render_template("index.html", token=token)
            else:
                error_message = "incorrect user data, try again"  # error message
        
        return render_template("login.html", error_message=error_message)


    def get_logout(self):
        
        data = request.get_json()
        token = data.get("token")
        
        self.user_manager.logout(token)
        response = redirect(url_for("login"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    def get_userConfig(self):
        
        data = request.get_json()
        token = data.get("token")
        user = self.user_manager.verify_token(token)
        if user:
            return redirect(url_for("login"))
        
        return render_template("sites/user-config.html")
    
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
        system_msg = data.get('system_msg') or "none"
        temperature = data.get('temperature')
        context = data.get('context') or "none"
        message = data.get('message')
        chat_id = session[CHAT_ID]
        
        if not bot_name or not message or not chat_id:
            return jsonify({"message": "Faltan parámetros necesarios"}), 400
        
        # Llamada al chatbot manager para procesar el mensaje
        response = self.chatbot_manager.manager_send_message(bot_name, system_msg, temperature, context, message, chat_id)
        is_summary = self.chatbot_manager.is_summary(bot_name, chat_id)
        
        # Aquí puedes retornar la respuesta que desee el bot
        return jsonify({
            "response": response, 
            "sum": is_summary
        })
        
    def API_get_last_summary(self):
        
        if 'username' not in session:
            return jsonify({"message": "Usuario no autenticado"}), 401  # 401 = Unauthorized
        
        bot_name = session[MODEL]
        chat_id = session[CHAT_ID]
        
        summary = self.chatbot_manager.get_last_summary(bot_name, chat_id)
        print("summary received: ", summary)
        
        return jsonify({"summary": summary})
        
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
    
        session[CHAT_ID] = chat_id
        
        return jsonify({"success": True}), 200
    
    def API_get_singleChat(self):
        
        chats = self.get_chats_in_chatbot()
        print(chats)
        
        for chat in chats:
            if chat.id == session[CHAT_ID]:                
                return jsonify({
                    "messages": chat.messages,
                    "summary": chat.summary,
                    "temperature": chat.temperature,
                    "system_msg": chat.system_msg
                })
        
        return jsonify({"error": "Chat no encontrado"}), 404
    
    def API_create_chat(self):
        
        session[CHAT_ID] = Chat._generate_chat_id()
        return jsonify({"success": True}), 200
    
    def API_set_chat_config(self):
        
        data = request.get_json()
        summary_list = data.get("summary_list")
        temperature = data.get("temperature")
        system_msg = data.get("system_msg")
        
        chat = self.chatbot_manager.get_chatbot(session[MODEL]).get_target_chat(session[CHAT_ID])
        print("[INFO]: chat object loaded - ", chat)
        chat.save_chat_config(session[USERNAME], session[MODEL], summary_list, temperature, system_msg)
        
        return jsonify({"success": True}), 200