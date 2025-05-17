import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from transformers import AutoModel, AutoTokenizer
from torch.utils.data import Dataset, DataLoader
import wandb
from tqdm import tqdm

class MetaLearningDataset(Dataset):
    def __init__(self, tasks: List[Dict[str, Any]], max_length: int = 512):
        self.tasks = tasks
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    def __len__(self) -> int:
        return len(self.tasks)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        task = self.tasks[idx]
        inputs = self.tokenizer(
            task["input"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        targets = self.tokenizer(
            task["output"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids": inputs["input_ids"].squeeze(),
            "attention_mask": inputs["attention_mask"].squeeze(),
            "labels": targets["input_ids"].squeeze()
        }

class MetaLearner:
    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 1e-4,
        meta_learning_rate: float = 1e-3,
        num_inner_steps: int = 5,
        num_meta_steps: int = 1000
    ):
        self.model = model
        self.learning_rate = learning_rate
        self.meta_learning_rate = meta_learning_rate
        self.num_inner_steps = num_inner_steps
        self.num_meta_steps = num_meta_steps
        self.meta_optimizer = optim.Adam(model.parameters(), lr=meta_learning_rate)
        
        # Initialize wandb for experiment tracking
        wandb.init(project="kapesit-agi", name="meta-learning")
    
    def adapt_to_task(
        self,
        task_data: Dict[str, torch.Tensor],
        num_steps: Optional[int] = None
    ) -> nn.Module:
        if num_steps is None:
            num_steps = self.num_inner_steps
        
        # Create a copy of the model for task-specific adaptation
        adapted_model = type(self.model)(**self.model.__dict__)
        adapted_model.load_state_dict(self.model.state_dict())
        
        # Create task-specific optimizer
        task_optimizer = optim.Adam(adapted_model.parameters(), lr=self.learning_rate)
        
        # Adapt the model to the specific task
        for _ in range(num_steps):
            task_optimizer.zero_grad()
            outputs = adapted_model(
                input_ids=task_data["input_ids"],
                attention_mask=task_data["attention_mask"]
            )
            loss = nn.CrossEntropyLoss()(
                outputs.view(-1, outputs.size(-1)),
                task_data["labels"].view(-1)
            )
            loss.backward()
            task_optimizer.step()
        
        return adapted_model
    
    def meta_update(
        self,
        meta_batch: List[Dict[str, torch.Tensor]],
        validation_batch: List[Dict[str, torch.Tensor]]
    ) -> Dict[str, float]:
        meta_loss = 0.0
        meta_acc = 0.0
        
        for task_data in meta_batch:
            # Adapt model to current task
            adapted_model = self.adapt_to_task(task_data)
            
            # Evaluate on validation data
            with torch.no_grad():
                val_outputs = adapted_model(
                    input_ids=validation_batch[0]["input_ids"],
                    attention_mask=validation_batch[0]["attention_mask"]
                )
                val_loss = nn.CrossEntropyLoss()(
                    val_outputs.view(-1, val_outputs.size(-1)),
                    validation_batch[0]["labels"].view(-1)
                )
                meta_loss += val_loss.item()
                
                # Calculate accuracy
                predictions = torch.argmax(val_outputs, dim=-1)
                meta_acc += (predictions == validation_batch[0]["labels"]).float().mean().item()
        
        # Average metrics
        meta_loss /= len(meta_batch)
        meta_acc /= len(meta_batch)
        
        # Update meta-parameters
        self.meta_optimizer.zero_grad()
        meta_loss.backward()
        self.meta_optimizer.step()
        
        return {
            "meta_loss": meta_loss,
            "meta_accuracy": meta_acc
        }
    
    def train(
        self,
        train_dataset: MetaLearningDataset,
        val_dataset: MetaLearningDataset,
        batch_size: int = 8
    ) -> Dict[str, List[float]]:
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        metrics = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
        
        for step in tqdm(range(self.num_meta_steps)):
            # Sample meta-batch
            meta_batch = next(iter(train_loader))
            val_batch = next(iter(val_loader))
            
            # Perform meta-update
            meta_metrics = self.meta_update(meta_batch, val_batch)
            
            # Log metrics
            wandb.log({
                "step": step,
                "meta_loss": meta_metrics["meta_loss"],
                "meta_accuracy": meta_metrics["meta_accuracy"]
            })
            
            metrics["train_loss"].append(meta_metrics["meta_loss"])
            metrics["train_acc"].append(meta_metrics["meta_accuracy"])
        
        return metrics

class SelfImprovingAGI:
    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 1e-4,
        improvement_threshold: float = 0.1
    ):
        self.model = model
        self.learning_rate = learning_rate
        self.improvement_threshold = improvement_threshold
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode="min",
            factor=0.5,
            patience=5
        )
        
        # Initialize performance tracking
        self.performance_history = []
        self.improvement_history = []
    
    def evaluate_performance(self, eval_data: Dict[str, torch.Tensor]) -> float:
        with torch.no_grad():
            outputs = self.model(
                input_ids=eval_data["input_ids"],
                attention_mask=eval_data["attention_mask"]
            )
            loss = nn.CrossEntropyLoss()(
                outputs.view(-1, outputs.size(-1)),
                eval_data["labels"].view(-1)
            )
            return loss.item()
    
    def generate_training_data(self, num_samples: int = 100) -> List[Dict[str, Any]]:
        # Generate synthetic training data based on current model performance
        training_data = []
        for _ in range(num_samples):
            # Generate input-output pairs
            input_text = self._generate_input()
            output_text = self._generate_output(input_text)
            training_data.append({
                "input": input_text,
                "output": output_text
            })
        return training_data
    
    def _generate_input(self) -> str:
        # Implement input generation logic
        return "Sample input text"
    
    def _generate_output(self, input_text: str) -> str:
        # Implement output generation logic
        return "Sample output text"
    
    def self_improve(
        self,
        eval_data: Dict[str, torch.Tensor],
        num_iterations: int = 100
    ) -> Dict[str, List[float]]:
        improvement_metrics = {
            "performance": [],
            "improvement": []
        }
        
        for iteration in range(num_iterations):
            # Evaluate current performance
            current_performance = self.evaluate_performance(eval_data)
            self.performance_history.append(current_performance)
            
            # Generate new training data
            training_data = self.generate_training_data()
            
            # Train on new data
            for batch in training_data:
                self.optimizer.zero_grad()
                outputs = self.model(
                    input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"]
                )
                loss = nn.CrossEntropyLoss()(
                    outputs.view(-1, outputs.size(-1)),
                    batch["labels"].view(-1)
                )
                loss.backward()
                self.optimizer.step()
            
            # Evaluate improvement
            new_performance = self.evaluate_performance(eval_data)
            improvement = current_performance - new_performance
            self.improvement_history.append(improvement)
            
            # Update learning rate
            self.scheduler.step(new_performance)
            
            # Log metrics
            improvement_metrics["performance"].append(new_performance)
            improvement_metrics["improvement"].append(improvement)
            
            # Check if improvement threshold is met
            if improvement < self.improvement_threshold:
                print(f"Stopping self-improvement at iteration {iteration}")
                break
        
        return improvement_metrics
    
    def analyze_improvement(self) -> Dict[str, Any]:
        if not self.performance_history or not self.improvement_history:
            return {}
        
        return {
            "total_improvement": self.performance_history[0] - self.performance_history[-1],
            "average_improvement": np.mean(self.improvement_history),
            "improvement_rate": np.polyfit(
                range(len(self.improvement_history)),
                self.improvement_history,
                1
            )[0],
            "convergence_point": np.argmax(self.improvement_history)
        } 