import os
from typing import Dict, Optional
from base_model import BaseModel

class ModelLoader:
    """
    Se encarga de la carga y descarga de modelos en caché.
    Gestiona el ciclo de vida de los modelos en memoria.
    """
    
    def __init__(self, models_dir: str = "available_models"):
        self.models_dir = models_dir
        self.loaded_models: Dict[str, BaseModel] = {}  # Modelos cargados en memoria
        self.model_configs: Dict[str, Dict] = {
            # Configuraciones por defecto para modelos conocidos
            "flan-t5-base": {"type": "seq2seq", "model_file": "model"},
            "deepseek-r1": {"type": "causal", "model_file": "model"}
        }
    
    def get_model_path(self, model_name: str) -> str:
        """
        Obtiene la ruta completa a un modelo
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            Ruta al directorio del modelo
        """
        # Convierte guiones a guiones bajos para la ruta del directorio
        directory_name = model_name.replace('-', '_')
        return os.path.join(self.models_dir, directory_name)
    
    def is_model_loaded(self, model_name: str) -> bool:
        """
        Verifica si un modelo está cargado en memoria
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            True si el modelo está cargado, False en caso contrario
        """
        return model_name in self.loaded_models
    
    def load_model(self, model_name: str) -> BaseModel:
        """
        Carga un modelo en memoria si no está ya cargado
        
        Args:
            model_name: Nombre del modelo a cargar
            
        Returns:
            Instancia del modelo cargado
            
        Raises:
            ValueError: Si el modelo no está disponible
        """
        # Si ya está cargado, devolver la instancia existente
        if self.is_model_loaded(model_name):
            return self.loaded_models[model_name]
        
        # Verificar que el modelo existe
        model_path = self.get_model_path(model_name)
        if not os.path.exists(model_path):
            raise ValueError(f"Modelo '{model_name}' no encontrado en {model_path}")
        
        # Obtener configuración del modelo
        config = self.model_configs.get(model_name, {"type": "seq2seq", "model_file": "model"})
        
        # Crear instancia del modelo
        model = BaseModel(
            model_name=model_name,
            model_path=model_path,
            model_type=config.get("type", "seq2seq"),
            model_file=config.get("model_file", "model")
        )
        
        # Guardar en caché
        self.loaded_models[model_name] = model
        return model
    
    def unload_model(self, model_name: str) -> bool:
        """
        Descarga un modelo de la memoria
        
        Args:
            model_name: Nombre del modelo a descargar
            
        Returns:
            True si se descargó correctamente, False si no estaba cargado
        """
        if not self.is_model_loaded(model_name):
            return False
        
        # Eliminar referencias al modelo y tokenizador
        del self.loaded_models[model_name]
        import gc
        gc.collect()
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return True
    
    def get_prediction(self, model_name: str, prompt: str) -> str:
        """
        Obtiene una predicción de un modelo
        
        Args:
            model_name: Nombre del modelo a utilizar
            prompt: Texto de entrada para el modelo
            
        Returns:
            Texto generado por el modelo
        """
        # Cargar modelo si no está cargado
        model = self.load_model(model_name)
        
        # Generar predicción
        return model.generate(prompt)
    
    def list_available_models(self) -> list:
        """
        Lista los modelos disponibles en el directorio de modelos
        
        Returns:
            Lista de nombres de modelos disponibles
        """
        model_dirs = []
        
        # Buscar directorios en el directorio de modelos
        if os.path.exists(self.models_dir):
            for item in os.listdir(self.models_dir):
                if os.path.isdir(os.path.join(self.models_dir, item)):
                    # Convertir guiones bajos a guiones para el nombre del modelo
                    model_dirs.append(item.replace('_', '-'))
        
        return model_dirs