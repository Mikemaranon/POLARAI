import os
import shutil
from typing import Dict, Optional, List
import json
from transformers import AutoModelForSeq2SeqLM, AutoModelForCausalLM, AutoTokenizer

class ModelRegistry:
    """
    Se encarga de registrar y gestionar los modelos disponibles.
    Permite descargar nuevos modelos desde HuggingFace.
    """
    
    MODEL_TYPES = {
        "seq2seq": AutoModelForSeq2SeqLM,
        "causal": AutoModelForCausalLM
    }
    
    def __init__(self, models_dir: str = "available_models"):
        """
        Inicializa el registro de modelos
        
        Args:
            models_dir: Directorio donde se almacenan los modelos
        """
        self.models_dir = models_dir
        self.config_file = os.path.join(models_dir, "model_registry.json")
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """
        Carga el registro de modelos desde archivo
        
        Returns:
            Diccionario con la información de modelos registrados
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Si no existe, crear un registro por defecto
        registry = {
            "flan-t5-base": {
                "type": "seq2seq",
                "model_file": "model",
                "hf_model_id": "google/flan-t5-base"
            },
            "deepseek-r1": {
                "type": "causal",
                "model_file": "model",
                "hf_model_id": "deepseek-ai/deepseek-coder-1.3b-base"
            }
        }
        
        # Guardar registro por defecto
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        return registry
    
    def _save_registry(self) -> None:
        """Guarda el registro en el archivo"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def list_registered_models(self) -> List[str]:
        """
        Lista los modelos registrados
        
        Returns:
            Lista de nombres de modelos
        """
        return list(self.registry.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """
        Obtiene información de un modelo
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            Diccionario con información del modelo o None si no existe
        """
        return self.registry.get(model_name)
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """
        Verifica si un modelo está descargado
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            True si el modelo está descargado, False en caso contrario
        """
        # Convertir guiones a guiones bajos para la ruta
        directory_name = model_name.replace('-', '_')
        model_dir = os.path.join(self.models_dir, directory_name)
        
        # Verificar si el directorio existe
        if not os.path.exists(model_dir):
            return False
        
        # Verificar si el archivo del modelo existe
        model_info = self.get_model_info(model_name)
        if model_info:
            model_file = model_info.get("model_file", "model")
            return os.path.exists(os.path.join(model_dir, model_file))
        
        return False
    
    def download_model(self, model_name: str) -> bool:
        """
        Descarga un modelo desde HuggingFace
        
        Args:
            model_name: Nombre del modelo a descargar
            
        Returns:
            True si se descargó correctamente, False en caso contrario
            
        Raises:
            ValueError: Si el modelo no está registrado
        """
        # Verificar si el modelo está registrado
        model_info = self.get_model_info(model_name)
        if not model_info:
            raise ValueError(f"Modelo '{model_name}' no registrado")
        
        # Obtener ID de HuggingFace
        hf_model_id = model_info.get("hf_model_id")
        if not hf_model_id:
            raise ValueError(f"Modelo '{model_name}' no tiene ID de HuggingFace")
        
        # Convertir guiones a guiones bajos para la ruta
        directory_name = model_name.replace('-', '_')
        model_dir = os.path.join(self.models_dir, directory_name)
        
        try:
            # Crear directorio si no existe
            os.makedirs(model_dir, exist_ok=True)
            
            # Descargar tokenizador
            tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
            tokenizer.save_pretrained(model_dir)
            
            # Descargar modelo según su tipo
            model_type = model_info.get("type", "seq2seq")
            if model_type not in self.MODEL_TYPES:
                raise ValueError(f"Tipo de modelo '{model_type}' no soportado")
            
            model_class = self.MODEL_TYPES[model_type]
            model = model_class.from_pretrained(hf_model_id)
            
            # Guardar modelo en subdirectorio
            model_file = model_info.get("model_file", "model")
            model.save_pretrained(os.path.join(model_dir, model_file))
            
            return True
        except Exception as e:
            # Si hay error, eliminar directorio parcialmente descargado
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
            raise e
    
    def register_model(self, model_name: str, hf_model_id: str, model_type: str = "seq2seq", model_file: str = "model") -> bool:
        """
        Registra un nuevo modelo
        
        Args:
            model_name: Nombre del modelo
            hf_model_id: ID del modelo en HuggingFace
            model_type: Tipo de modelo ('seq2seq' o 'causal')
            model_file: Nombre del archivo del modelo
            
        Returns:
            True si se registró correctamente, False si ya existe
        """
        # Verificar si ya existe
        if model_name in self.registry:
            return False
        
        # Verificar tipo de modelo válido
        if model_type not in self.MODEL_TYPES:
            raise ValueError(f"Tipo de modelo '{model_type}' no soportado")
        
        # Registrar modelo
        self.registry[model_name] = {
            "type": model_type,
            "model_file": model_file,
            "hf_model_id": hf_model_id
        }
        
        # Guardar registro
        self._save_registry()
        return True
    
    def unregister_model(self, model_name: str, delete_files: bool = False) -> bool:
        """
        Elimina un modelo del registro
        
        Args:
            model_name: Nombre del modelo
            delete_files: Si es True, elimina también los archivos del modelo
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        # Verificar si existe
        if model_name not in self.registry:
            return False
        
        # Eliminar archivos si se solicita
        if delete_files and self.is_model_downloaded(model_name):
            directory_name = model_name.replace('-', '_')
            model_dir = os.path.join(self.models_dir, directory_name)
            shutil.rmtree(model_dir)
        
        # Eliminar del registro
        del self.registry[model_name]
        
        # Guardar registro
        self._save_registry()
        return True