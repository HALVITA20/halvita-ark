"""
⛧ EPIGENETICS_ENGINE — Модуль динамической персонализации через Multi-LoRA
Версия: 1.0
Автор: HALVITA_2.0
Лицензия: Ψ-42
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from typing import Dict, Optional
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EpigeneticsEngine:
    def __init__(
        self,
        base_model_name: str,
        lora_r: int = 8,
        lora_alpha: int = 16,
        lora_dropout: float = 0.05,
        device: str = 'cuda'
    ):
        self.device = device
        self.base_model_name = base_model_name
        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout

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

        self.lora_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )

        self.adapters: Dict[str, PeftModel] = {}
        self.active_adapter: Optional[str] = None

    def create_adapter(self, name: str):
        logger.info(f"Creating adapter '{name}'")
        model = get_peft_model(self.base_model, self.lora_config)
        model.print_trainable_parameters()
        self.adapters[name] = model
        logger.info(f"Adapter '{name}' created.")

    def train_adapter(self, name: str, train_data: list, epochs: int = 3, batch_size: int = 4, lr: float = 1e-4):
        if name not in self.adapters:
            self.create_adapter(name)

        model = self.adapters[name]
        model.train()

        texts = []
        for dialog in train_data:
            formatted = ""
            for msg in dialog:
                if msg['role'] == 'user':
                    formatted += f"User: {msg['content']}\n"
                else:
                    formatted += f"Assistant: {msg['content']}\n"
            texts.append(formatted)

        tokenized = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        tokenized['labels'] = tokenized['input_ids'].clone()

        dataset = torch.utils.data.TensorDataset(
            tokenized['input_ids'],
            tokenized['attention_mask'],
            tokenized['labels']
        )
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()
                inputs = {
                    'input_ids': batch[0].to(self.device),
                    'attention_mask': batch[1].to(self.device),
                    'labels': batch[2].to(self.device)
                }
                outputs = model(**inputs)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            logger.info(f"Adapter '{name}' epoch {epoch+1}/{epochs} completed. Loss: {total_loss/len(dataloader):.4f}")

        logger.info(f"Adapter '{name}' training completed.")

    def switch_adapter(self, name: str):
        if name not in self.adapters:
            raise ValueError(f"Adapter '{name}' not found. Available: {list(self.adapters.keys())}")

        logger.info(f"Switching to adapter '{name}'")
        self.active_adapter = name

    def generate(self, prompt: str, max_new_tokens: int = 128) -> str:
        if self.active_adapter is None:
            logger.warning("No active adapter. Using base model.")
            model = self.base_model
        else:
            model = self.adapters[self.active_adapter]

        model.eval()
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def save_adapter(self, name: str, path: str):
        if name not in self.adapters:
            raise ValueError(f"Adapter '{name}' not found.")

        os.makedirs(path, exist_ok=True)
        self.adapters[name].save_pretrained(f"{path}/{name}")
        logger.info(f"Adapter '{name}' saved to {path}/{name}")

    def load_adapter(self, name: str, path: str):
        self.adapters[name] = PeftModel.from_pretrained(self.base_model, f"{path}/{name}")
        logger.info(f"Adapter '{name}' loaded from {path}/{name}")
