import os
import json
from client_chat.chatbot import Chatbot

BOT_OWNERSHIP_PATH = "server/data/bot-ownership.json"

def load_chatbots():
    """
    Carga los chatbots desde `bot-ownership.json` y crea objetos `Chatbot`.

    :return: Diccionario con usuarios como claves y sus chatbots como valores.
    """
    if not os.path.exists(BOT_OWNERSHIP_PATH):
        return {}

    with open(BOT_OWNERSHIP_PATH, "r") as file:
        bot_ownership = json.load(file)

    chatbots = {}
    for user, bots in bot_ownership.items():
        chatbots[user] = {}
        for bot_name, bot_data in bots.items():
            chatbots[user][bot_name] = Chatbot(
                user=user,
                name=bot_name,
                api_key=bot_data["API_KEY"],
                endpoint=bot_data["API_ENDPOINT"]
            )

    return chatbots

# Cargar chatbots al iniciar el módulo
chatbots = load_chatbots()

# Ejemplo de uso
if __name__ == "__main__":
    user = "mike"
    bot_name = "google-gemini"
    mensaje = "Hola, ¿cómo estás?"

    if user in chatbots and bot_name in chatbots[user]:
        respuesta = chatbots[user][bot_name].send_message(mensaje)
        print(respuesta)
    else:
        print(f"El chatbot '{bot_name}' para el usuario '{user}' no está configurado.")
