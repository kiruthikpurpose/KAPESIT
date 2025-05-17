import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from typing import Dict, List, Optional, Tuple
import numpy as np

class KapesitAGI(nn.Module):
    def __init__(
        self,
        model_name: str = "gpt2",
        hidden_size: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        dropout: float = 0.1
    ):
        super().__init__()
        self.model_name = model_name
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        
        self.transformer = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=num_heads,
            dropout=dropout
        )
        
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Linear(hidden_size * 4, hidden_size),
            nn.Dropout(dropout)
        )
        
        self.layer_norm1 = nn.LayerNorm(hidden_size)
        self.layer_norm2 = nn.LayerNorm(hidden_size)
        
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        transformer_output = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        hidden_states = transformer_output.last_hidden_state
        
        # Self-attention
        attn_output, attn_weights = self.attention(
            hidden_states,
            hidden_states,
            hidden_states
        )
        
        # Add & Norm
        hidden_states = self.layer_norm1(hidden_states + attn_output)
        
        # Feed Forward
        ff_output = self.feed_forward(hidden_states)
        
        # Add & Norm
        output = self.layer_norm2(hidden_states + ff_output)
        
        return output, attn_weights
    
    def generate(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9
    ) -> str:
        self.eval()
        with torch.no_grad():
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"]
            
            for _ in range(max_length):
                outputs, _ = self(input_ids)
                next_token_logits = outputs[:, -1, :] / temperature
                
                # Top-k filtering
                indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                next_token_logits[indices_to_remove] = float('-inf')
                
                # Top-p (nucleus) filtering
                sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                next_token_logits[indices_to_remove] = float('-inf')
                
                probs = torch.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                input_ids = torch.cat([input_ids, next_token], dim=1)
                
                if next_token.item() == self.tokenizer.eos_token_id:
                    break
            
            return self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
    
    def learn_from_examples(
        self,
        examples: List[Tuple[str, str]],
        batch_size: int = 8,
        learning_rate: float = 1e-5,
        num_epochs: int = 3
    ) -> Dict[str, float]:
        self.train()
        optimizer = torch.optim.AdamW(self.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        total_loss = 0
        for epoch in range(num_epochs):
            epoch_loss = 0
            for i in range(0, len(examples), batch_size):
                batch = examples[i:i + batch_size]
                
                input_texts = [ex[0] for ex in batch]
                target_texts = [ex[1] for ex in batch]
                
                inputs = self.tokenizer(
                    input_texts,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                )
                
                targets = self.tokenizer(
                    target_texts,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                )
                
                outputs, _ = self(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"]
                )
                
                loss = criterion(
                    outputs.view(-1, outputs.size(-1)),
                    targets["input_ids"].view(-1)
                )
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
            
            total_loss += epoch_loss
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss/len(examples):.4f}")
        
        return {"average_loss": total_loss / (num_epochs * len(examples))} 