from transformers import AutoModelForSeq2SeqLM, AutoModelForCausalLM, AutoTokenizer
import torch
import os
from typing import Dict, Any, Tuple

class BaseModel:
    """
    Clase base para comunicarse con modelos de lenguaje.
    Su única responsabilidad es recibir inputs y devolver outputs del modelo.
    """
    
    MODEL_TYPES = {
        "seq2seq": AutoModelForSeq2SeqLM,
        "causal": AutoModelForCausalLM
    }
    
    def __init__(self, model_name: str, model_path: str, model_type: str = "seq2seq", model_file: str = "model"):
        """
        Inicializa un modelo base
        
        Args:
            model_name: Nombre del modelo
            model_path: Ruta al directorio del modelo
            model_type: Tipo de modelo ('seq2seq' o 'causal')
            model_file: Nombre del archivo del modelo
        """
        self.model_name = model_name
        self.model_path = model_path
        self.model_type = model_type
        
        # Verificar tipo de modelo válido
        if model_type not in self.MODEL_TYPES:
            raise ValueError(f"Tipo de modelo '{model_type}' no soportado. Opciones: {list(self.MODEL_TYPES.keys())}")
        
        # Cargar tokenizador
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Cargar modelo
        model_class = self.MODEL_TYPES[model_type]
        self.model = model_class.from_pretrained(
            os.path.join(model_path, model_file),
            torch_dtype=torch.float16,
            device_map="auto"
        )
    
    def generate(self, prompt: str) -> str:
        """
        Genera una respuesta a partir de un prompt
        
        Args:
            prompt: Texto de entrada para el modelo
            
        Returns:
            Texto generado por el modelo
        """
        # Tokenizar entrada
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        # Mover a GPU si está disponible
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generar respuesta según tipo de modelo
        if self.model_type == "seq2seq":
            output = self.model.generate(**inputs, max_length=512)
        else:  # causal
            output = self.model.generate(**inputs, max_new_tokens=512)
        
        # Decodificar y devolver respuesta
        return self.tokenizer.decode(output[0], skip_special_tokens=True)