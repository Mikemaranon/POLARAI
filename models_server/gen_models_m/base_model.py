from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import os
from flask import Flask, request, jsonify

# Rutas de los modelos
MODEL_PATH = "available_models/"
MODEL = "model."

class BaseModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH + model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_PATH + model_name + "/" + MODEL,
            torch_dtype=torch.float16,
            device_map="auto"
        )

    def send_input_to_model(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        output = self.model.generate(**inputs, max_length=512)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)