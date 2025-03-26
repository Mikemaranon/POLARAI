import json
from chat_m.chat import Chat
from data_m.database import Database  # Importar la instancia del gestor de base de datos

class SummaryMaker:
    
    def __init__(self):
        self.buffer = []  # n-message Buffer
        self.db = Database()     
        
    def set_session_info(self, user, bot_name, chat_id):
        self.user = user
        self.bot_name = bot_name
        self.chat_id = chat_id

    def add_message(self, sender, content):
        # Añadir mensaje al buffer
        self.buffer.append({"sender": sender, "content": content})

        # Verificar si se han acumulado 6 mensajes (3 del usuario y 3 del bot)
        if len(self.buffer) == 6:
            return self.generate_summary()
        else:
            return 0

    def generate_summary(self):
        # Crear un texto con los mensajes para enviar al modelo
        chat_text = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in self.buffer])

        # Generar el resumen llamando a la API
        summary = [
            {
                "summary_text": "?"
            }           
        ] #FIXME

        # Guardar el resumen en la base de datos
        # TODO: REVISAR FORMATO GUARDADO
        self.save_summary(summary[0]['summary_text'])

        # Limpiar el buffer después de generar el resumen
        self.reset_buffer()
        
        # Return the content for the chat to save it
        return summary[0]['summary_text']

    def save_summary(self, summary_text):
        
        current_sum_list = self.db.load_summary_list(self.user, self.bot_name, self.chat_id)
        new_sum_list = current_sum_list.append({
            "id": len(current_sum_list) + 1, 
            "content": summary_text,
            "activated": "true"
        })
        
        self.db.save_summary_list(self.chat_id, self.user, self.bot_name, new_sum_list)
    
    def reset_buffer(self):
        # Resetear el buffer si es necesario
        self.buffer = []
        
    # TODO: método para guardar el estado activo de los resumenes