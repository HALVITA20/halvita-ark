"""
⛧ SLEEP_ENGINE — Модуль непрерывного обучения с EWC + Replay Buffer
Версия: 1.0
Автор: HALVITA_2.0
Лицензия: Ψ-42

Реализует механизм «сна» для LLM:
- Хранит историю диалогов в буфере воспроизведения.
- В фоновом режиме дообучает LoRA-адаптер с регуляризацией EWC.
- Предотвращает катастрофическое забывание.
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
from typing import List, Dict, Optional, Tuple
import json
import random
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EWC:
    """
    Elastic Weight Consolidation (EWC) — регуляризация, предотвращающая забывание.
    """
    def __init__(self, model, dataloader, device='cuda'):
        self.model = model
        self.device = device
        self.params = {n: p.clone().detach() for n, p in model.named_parameters() if p.requires_grad}
        self.fisher = self._compute_fisher(dataloader)

    def _compute_fisher(self, dataloader):
        fisher = {}
        for n, p in self.model.named_parameters():
            if p.requires_grad:
                fisher[n] = torch.zeros_like(p)

        self.model.train()
        for batch in dataloader:
            self.model.zero_grad()
            inputs = {k: v.to(self.device) for k, v in batch.items() if k in ['input_ids', 'attention_mask', 'labels']}
            outputs = self.model(**inputs)
            loss = outputs.loss
            loss.backward()

            for n, p in self.model.named_parameters():
                if p.requires_grad and p.grad is not None:
                    fisher[n] += p.grad.pow(2).clone().detach()

        for n in fisher:
            fisher[n] /= len(dataloader)

        return fisher

    def penalty(self, model):
        loss = 0
        for n, p in model.named_parameters():
            if p.requires_grad and n in self.fisher:
                loss += (self.fisher[n] * (p - self.params[n]).pow(2)).sum()
        return loss


class SleepEngine:
    """
    Двигатель «Сна» — управляет буфером воспроизведения и дообучением.
    """
    def __init__(
        self,
        base_model_name: str,
        buffer_size: int = 1000,
        ewc_lambda: float = 100.0,
        lora_r: int = 8,
        lora_alpha: int = 16,
        lora_dropout: float = 0.05,
        device: str = 'cuda'
    ):
        self.buffer_size = buffer_size
        self.ewc_lambda = ewc_lambda
        self.device = device

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

        self.model = get_peft_model(self.base_model, self.lora_config)
        self.model.print_trainable_parameters()

        self.replay_buffer = deque(maxlen=buffer_size)
        self.ewc = None
        self.is_training = False

    def add_experience(self, dialog: List[Dict[str, str]], importance: float = 1.0):
        self.replay_buffer.append({
            'dialog': dialog,
            'importance': importance,
            'timestamp': len(self.replay_buffer)
        })
        logger.info(f"Added experience to buffer. Buffer size: {len(self.replay_buffer)}")

    def _prepare_batch(self, dialogs: List[Dict]) -> Dataset:
        texts = []
        for d in dialogs:
            formatted = ""
            for msg in d['dialog']:
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
        return Dataset.from_dict({
            'input_ids': tokenized['input_ids'],
            'attention_mask': tokenized['attention_mask'],
            'labels': tokenized['labels']
        })

    def sleep(self, epochs: int = 3, batch_size: int = 4, lr: float = 1e-4):
        if len(self.replay_buffer) < 2:
            logger.warning("Buffer too small for sleep. Need at least 2 dialogs.")
            return

        logger.info(f"Starting SLEEP phase with {len(self.replay_buffer)} experiences")

        buffer_list = list(self.replay_buffer)
        weights = [min(1.0, (d['importance'] + 0.1) * (1 + 0.5 * (d['timestamp'] / self.buffer_size))) for d in buffer_list]
        sampled = random.choices(buffer_list, weights=weights, k=min(len(buffer_list), batch_size * 4))

        dataset = self._prepare_batch(sampled)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        if self.ewc is None:
            logger.info("Initializing EWC...")
            self.ewc = EWC(self.model, dataloader, self.device)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)

        self.model.train()
        self.is_training = True

        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()

                inputs = {
                    'input_ids': batch['input_ids'].to(self.device),
                    'attention_mask': batch['attention_mask'].to(self.device),
                    'labels': batch['labels'].to(self.device)
                }

                outputs = self.model(**inputs)
                loss = outputs.loss

                ewc_penalty = self.ewc.penalty(self.model)
                loss = loss + self.ewc_lambda * ewc_penalty

                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            logger.info(f"Sleep epoch {epoch+1}/{epochs} completed. Avg loss: {total_loss/len(dataloader):.4f}")

        self.is_training = False
        logger.info("Sleep phase completed.")

    def generate(self, prompt: str, max_new_tokens: int = 128) -> str:
        self.model.eval()
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def save(self, path: str):
        self.model.save_pretrained(path)
        with open(f"{path}/replay_buffer.json", 'w') as f:
            json.dump(list(self.replay_buffer), f, indent=2)
        logger.info(f"Saved sleep engine to {path}")

    def load(self, path: str):
        from peft import PeftModel
        self.model = PeftModel.from_pretrained(self.base_model, path)
        try:
            with open(f"{path}/replay_buffer.json", 'r') as f:
                buffer_data = json.load(f)
                self.replay_buffer = deque(buffer_data, maxlen=self.buffer_size)
        except FileNotFoundError:
            logger.warning("Replay buffer file not found, starting with empty buffer.")
        logger.info(f"Loaded sleep engine from {path}")
