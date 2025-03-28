import json

class MessageProcessor:
    def process_message(self, message):
        """Procesa mensajes JSON y ejecuta acciones."""
        try:
            data = json.loads(message)  # Convertir a JSON
            action = data.get("action")
            payload = data.get("data", {})

            if action == "ping":
                return json.dumps({"response": "pong"})

            elif action == "create_model":
                return json.dumps({"response": f"Creating model {payload.get('name', 'unknown')}"})

            return json.dumps({"error": "Acción no reconocida"})

        except json.JSONDecodeError:
            return json.dumps({"error": "Formato JSON inválido"})