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
        self._register_APIs()
        
        self.tempToken = None

    # ==================================================================================
    #                     BASIC CLASS FUNCTIONS
    #
    #           [get_chats_in_chatbot]     get the list of chats in the 
    #                                      selected chatbot
    #           [get_request_token]        read the token in the request
    #                                      package and extract it
    #           [check_auth]               checks if the token is still
    #                                      available
    #           [check_user]               checks if selected user is
    #                                      available
    # ================================================================================== 

    def get_chats_in_chatbot(self, user):
        
        model = user.get_session_data(MODEL)
        chatbot = self.chatbot_manager.get_chatbot(user, model)
        chats = chatbot.load_chats()
        return chats
    
    def get_request_token(self):
        
        print("get_request_token")
        # 2. token from URL params
        token = request.args.get("token")
        if token:
            print("token exist in URL: ", token)
            return token
        
        print("get_request_token - no token found in URL")
        # 1. token from header Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            print("token exist in header: ", token)
            return token
    
        return None
    
    def check_auth(self):
        
        token = self.get_request_token()
        
        print("token exist after header: ", token)
        return token

    def check_user(self):
        token = self.check_auth()
        if token:
            user = self.user_manager.get_user(token)
            print("user in check_user: ", user)
            if user:
                return user
        return None
    
    # ==================================================================================
    #                     REGISTERING ROUTES AND APIs
    #
    #            [_register_routes]     instance of every basic route 
    #            [_register_APIs]       instance of every API
    # ================================================================================== 

    def _register_routes(self):
        self.app.add_url_rule("/", "home", self.get_home, methods=["GET"])
        self.app.add_url_rule("/index", "index", self.get_index)
        self.app.add_url_rule("/login", "login", self.get_login, methods=["GET", "POST"])
        self.app.add_url_rule("/logout", "logout", self.get_logout, methods=["POST"])
        self.app.add_url_rule("/sites/user-config", "get_userConfig", self.get_userConfig, methods=["GET"])
        self.app.add_url_rule("/sites/training", "get_trainingIndex", self.API_get_trainingIndex, methods=["GET", "POST"])
        self.app.add_url_rule("/sites/polarai", "polarai_chat", self.API_get_model_to_chat, methods=["GET", "POST"])
        
    def _register_APIs(self):
        self.app.add_url_rule("/api/get-chats", "get_chats", self.API_get_chats, methods=["GET"])
        self.app.add_url_rule("/api/send-message", "send_message", self.API_send_message, methods=["POST"])
        self.app.add_url_rule("/api/get-models", "get_models", self.API_get_models, methods=["POST"])
        self.app.add_url_rule("/api/set-chatId", "set_chatId", self.API_set_chatId, methods=["POST"])
        self.app.add_url_rule("/api/get-singleChat", "get_singleChat", self.API_get_singleChat, methods=["GET"])
        
        self.app.add_url_rule("/api/create-chat", "create_chat", self.API_create_chat, methods=["GET"])
        self.app.add_url_rule("/api/get-last-summary", "get_lastSummary", self.API_get_last_summary, methods=["GET"])
        
        self.app.add_url_rule("/api/set-chat-config", "set_chatConfig", self.API_set_chat_config, methods=["POST"])
        
    # ==================================================================================
    #                           BASIC ROUTINGS URLs
    #
    #            [get_home]             go to index.html
    #            [get_login]            log user and send his token
    #            [get_logout]           log user out, send to index.html 
    #            [get_userConfig]       redirect to users current condiguration
    # ================================================================================== 
    
    def get_index(self):
        return render_template("index.html")
    
    def get_home(self):
        user = self.check_user()
        if user:
                
            print("user in home: ", user)
            print("username: ", user.token)
            user.set_session_data(MODEL, None) 
            user.set_session_data(CHAT_ID, None) 

            return redirect(url_for("index"))  # Redirect to index.html
        return render_template("login.html")

    def get_login(self):
        error_message = None
        if request.method == "POST":
            data = request.get_json()

            username = data.get("username")
            password = data.get("password")

            token = self.user_manager.login(username, password)
            if token:
                self.chatbot_manager.set_session(username)
                response = jsonify({"token": token})
                return response
            
            error_message = "incorrect user data, try again"

        return render_template("login.html", error_message=error_message)

    def get_logout(self):
        
        token = self.get_request_token()
        
        self.user_manager.logout(token)
        response = redirect(url_for("login"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    def get_userConfig(self):
        token = self.get_request_token()
        
        print("token in userConfig: ", token)
        user = self.user_manager.verify_token(token)
        if user:
            print("user in userConfig: ", user)
            return render_template("sites/user-config.html")
        return redirect(url_for("login"))
    
    # =========================================
    #       API protocols start from here
    # =========================================
    
    def API_get_trainingIndex(self):
        
        data = request.get_json()
        user = self.check_user()
                    
        if user:
            if request.method == "POST":
                # Ensure request is a JSON
                if request.content_type != "application/json":
                    return "Unsupported Media Type", 415

                user.set_session_data(MODEL, data.get('model')) 
                user.set_session_data(CHAT_ID, None) # training does not require chats

                # redirects to GET version with model
                return redirect(url_for("get_trainingIndex", model=data.get('model')))

            elif request.method == "GET":
                model = request.args.get("model", "default_model")  # default model if it is missing
                return render_template("sites/training-index.html", bot_name=model)
        
        return redirect(url_for("login"))
    
    def API_get_model_to_chat(self):
        
        if request.method == "GET":
            model = request.args.get("model", "default_model")
            return render_template("/sites/polarai-chat.html", bot_name=model)

        user = self.check_user()
        
        if user:
            if request.method == "POST":

                data = request.get_json()
                # Ensure request is a JSON
                if request.content_type != "application/json":
                    return "Unsupported Media Type", 415
                
                user.set_session_data(MODEL, data.get('model')) 
                user.set_session_data(CHAT_ID, None)  # Enters new chat

                # redirects to GET version with model
                return redirect(url_for("polarai_chat", model=data.get('model')))

            elif request.method == "GET":
                model = request.args.get("model", "default_model")  # default model if it is missing
                return render_template("/sites/polarai-chat.html", bot_name=model)
            
        return redirect(url_for("login"))
    
    def API_get_chats(self):
        
        user = self.check_user()
        chats = self.get_chats_in_chatbot(user)

        # only get 'id' and 'topic' from each chat
        chats_index = [{"id": chat.id, "topic": chat.topic} for chat in chats]

        return jsonify(chats_index)  # return chat index 
    
    # TODO: UPDATE SESSION PROBLEM IN CHAT_M
    def API_send_message(self):
        
        data = request.get_json()
        user = self.check_user()
            
        if user:
        
            bot_name = user.get_session_data(MODEL)
            system_msg = data.get('system_msg') or "none"
            temperature = data.get('temperature')
            context = data.get('context') or "none"
            message = data.get('message')
            chat_id = user.get_session_data(CHAT_ID)
            
            if not bot_name or not message or not chat_id:
                return jsonify({"message": "missing params"}), 400
            
            # chatbot_manager Call to process message
            response = self.chatbot_manager.manager_send_message(bot_name, user.username, system_msg, temperature, context, message, chat_id)
            is_summary = self.chatbot_manager.is_summary(bot_name, chat_id)
            
            # return bots response
            return jsonify({
                "response": response, 
                "sum": is_summary
            })
        return jsonify({"message": "Unidentified user"}), 401  # 401 = Unauthorized
        
    def API_get_last_summary(self):
        
        user = self.check_user()
        
        bot_name = user.get_session_data(MODEL)
        chat_id = user.get_session_data(CHAT_ID)
        
        summary = self.chatbot_manager.get_last_summary(bot_name, chat_id)
        print("summary received: ", summary)
        
        return jsonify({"summary": summary})
        
    def API_get_models(self):
        
        user = self.check_user()
            
        if user:
            try:
                user_bots = self.chatbot_manager.get_user_bots(user.username)
                return jsonify({"bots": user_bots})
            except Exception as e:
                return jsonify({"message": str(e)}), 500  # server error
        
        return jsonify({"message": "Unidentified user"}), 401  # 401 = Unauthorized
    
    def API_set_chatId(self):
        
        data = request.get_json()
        user = self.check_user()
        chat_id = data.get("chatId")
    
        chat_id = user.set_session_data(CHAT_ID, chat_id)
        
        return jsonify({"success": True}), 200
    
    def API_get_singleChat(self):
        
        user = self.check_user()
        chats = self.get_chats_in_chatbot(user)
        
        for chat in chats:
            if chat.id == user.get_session_data(CHAT_ID):                
                return jsonify({
                    "messages": chat.messages,
                    "summary": chat.summary,
                    "temperature": chat.temperature,
                    "system_msg": chat.system_msg
                })
        
        return jsonify({"error": "Chat not found"}), 404
    
    def API_create_chat(self):
        
        user = self.check_user()
        user.set_session_data(CHAT_ID, Chat._generate_chat_id())
        return jsonify({"success": True}), 200
    
    def API_set_chat_config(self):
        
        data = request.get_json()
        user = self.check_user()
        summary_list = data.get("summary_list")
        temperature = data.get("temperature")
        system_msg = data.get("system_msg")
        
        model = user.get_session_data(MODEL)
        chat_id = user.get_session_data(CHAT_ID)
        username = user.get_session_data(USERNAME)
        
        chat = self.chatbot_manager.get_chatbot(model).get_target_chat(chat_id)
        print("[INFO]: chat object loaded - ", chat)
        chat.save_chat_config(username, model, summary_list, temperature, system_msg)
        
        return jsonify({"success": True}), 200