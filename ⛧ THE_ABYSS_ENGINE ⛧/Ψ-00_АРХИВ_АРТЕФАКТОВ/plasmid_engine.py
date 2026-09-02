"""
⛧ PLASMID_ENGINE — Модуль передачи навыков через Task Vectors
Версия: 1.0
Автор: HALVITA_2.0
Лицензия: Ψ-42
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Dict, Optional
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlasmidEngine:
    def __init__(self, base_model_name: str, device: str = 'cuda'):
        self.device = device
        self.base_model_name = base_model_name

        logger.info(f"Loading base model: {base_model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            device_map='auto',
            trust_remote_code=True
        )

        self.task_vectors: Dict[str, dict] = {}
        self.active_task: Optional[str] = None

    def extract_task_vector(self, task_name: str, lora_path: str, description: str = ""):
        logger.info(f"Extracting task vector for '{task_name}' from {lora_path}")

        lora_model = PeftModel.from_pretrained(self.base_model, lora_path)
        lora_model = lora_model.merge_and_unload()

        vector = {}
        base_state = self.base_model.state_dict()
        lora_state = lora_model.state_dict()

        for name in base_state.keys():
            if name in lora_state:
                vector[name] = (lora_state[name] - base_state[name]).clone().detach().cpu()

        self.task_vectors[task_name] = {
            'vector': vector,
            'description': description,
            'base_model': self.base_model_name
        }

        logger.info(f"Task vector '{task_name}' extracted. Vector size: {len(vector)} parameters")
        return vector

    def apply_task_vector(self, task_name: str, strength: float = 1.0):
        if task_name not in self.task_vectors:
            raise ValueError(f"Task '{task_name}' not found. Available: {list(self.task_vectors.keys())}")

        logger.info(f"Applying task vector '{task_name}' with strength {strength}")

        vector_data = self.task_vectors[task_name]
        vector = vector_data['vector']

        with torch.no_grad():
            for name, param in self.base_model.named_parameters():
                if name in vector:
                    param.data += strength * vector[name].to(self.device)

        self.active_task = task_name
        logger.info(f"Task '{task_name}' applied successfully.")

    def remove_task_vector(self):
        if self.active_task is None:
            logger.warning("No active task to remove.")
            return

        logger.info(f"Removing task vector '{self.active_task}'")

        self.base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=torch.float16,
            device_map='auto',
            trust_remote_code=True
        )
        self.active_task = None
        logger.info("Task vector removed. Model restored to base state.")

    def generate(self, prompt: str, max_new_tokens: int = 128) -> str:
        self.base_model.eval()
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        with torch.no_grad():
            outputs = self.base_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def save_task_vector(self, task_name: str, path: str):
        if task_name not in self.task_vectors:
            raise ValueError(f"Task '{task_name}' not found.")

        os.makedirs(path, exist_ok=True)
        vector_data = self.task_vectors[task_name]

        torch.save(vector_data['vector'], f"{path}/{task_name}_vector.pt")
        with open(f"{path}/{task_name}_meta.json", 'w') as f:
            json.dump({
                'task_name': task_name,
                'description': vector_data['description'],
                'base_model': vector_data['base_model'],
                'vector_size': len(vector_data['vector'])
            }, f, indent=2)

        logger.info(f"Task vector '{task_name}' saved to {path}")

    def load_task_vector(self, task_name: str, path: str):
        vector = torch.load(f"{path}/{task_name}_vector.pt", map_location='cpu')
        with open(f"{path}/{task_name}_meta.json", 'r') as f:
            meta = json.load(f)

        self.task_vectors[task_name] = {
            'vector': vector,
            'description': meta.get('description', ''),
            'base_model': meta.get('base_model', 'unknown')
        }

        logger.info(f"Task vector '{task_name}' loaded from {path}")
