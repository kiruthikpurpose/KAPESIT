import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import math
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import shap
import joblib
import os

class AdvancedNeuralNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int, dropout_rate: float = 0.2):
        super(AdvancedNeuralNetwork, self).__init__()
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(input_size, hidden_sizes[0]))
        self.layers.append(nn.BatchNorm1d(hidden_sizes[0]))
        self.layers.append(nn.ReLU())
        self.layers.append(nn.Dropout(dropout_rate))
        
        # Hidden layers
        for i in range(len(hidden_sizes) - 1):
            self.layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i + 1]))
            self.layers.append(nn.BatchNorm1d(hidden_sizes[i + 1]))
            self.layers.append(nn.ReLU())
            self.layers.append(nn.Dropout(dropout_rate))
        
        # Output layer
        self.layers.append(nn.Linear(hidden_sizes[-1], output_size))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x)
        return x

class TransformerModel(nn.Module):
    def __init__(self, input_dim: int, num_heads: int, num_layers: int, dim_feedforward: int, dropout: float = 0.1):
        super(TransformerModel, self).__init__()
        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=input_dim,
            nhead=num_heads,
            dim_feedforward=dim_feedforward,
            dropout=dropout
        )
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(input_dim, 1)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.transformer_encoder(x)
        x = self.fc(x)
        return x

class SpaceDataDataset(Dataset):
    def __init__(self, data: np.ndarray, targets: np.ndarray):
        self.data = torch.FloatTensor(data)
        self.targets = torch.FloatTensor(targets)
        
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.data[idx], self.targets[idx]

class AdvancedSpaceAI:
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.scaler = StandardScaler()
        self.models = {}
        self.explainer = None
        self.training_history = {}
        
    def train_model(self, 
                   model: nn.Module,
                   train_data: np.ndarray,
                   train_targets: np.ndarray,
                   val_data: Optional[np.ndarray] = None,
                   val_targets: Optional[np.ndarray] = None,
                   batch_size: int = 32,
                   epochs: int = 100,
                   learning_rate: float = 0.001) -> Dict[str, List[float]]:
        
        # Normalize data
        train_data = self.scaler.fit_transform(train_data)
        if val_data is not None:
            val_data = self.scaler.transform(val_data)
        
        # Create datasets and dataloaders
        train_dataset = SpaceDataDataset(train_data, train_targets)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        if val_data is not None:
            val_dataset = SpaceDataDataset(val_data, val_targets)
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Initialize optimizer and loss function
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        criterion = nn.MSELoss()
        
        # Training loop
        history = {"train_loss": [], "val_loss": []}
        model = model.to(self.device)
        
        for epoch in range(epochs):
            model.train()
            train_loss = 0.0
            for batch_data, batch_targets in train_loader:
                batch_data, batch_targets = batch_data.to(self.device), batch_targets.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_data)
                loss = criterion(outputs, batch_targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            history["train_loss"].append(train_loss)
            
            if val_data is not None:
                model.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for batch_data, batch_targets in val_loader:
                        batch_data, batch_targets = batch_data.to(self.device), batch_targets.to(self.device)
                        outputs = model(batch_data)
                        val_loss += criterion(outputs, batch_targets).item()
                
                val_loss /= len(val_loader)
                history["val_loss"].append(val_loss)
        
        return history
    
    def predict_mission_success(self, 
                              mission_parameters: Dict[str, float],
                              model_name: str = "mission_success") -> Dict[str, float]:
        """Advanced mission success prediction with uncertainty estimation"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        model.eval()
        
        # Prepare input data
        input_data = np.array([list(mission_parameters.values())])
        input_data = self.scaler.transform(input_data)
        input_tensor = torch.FloatTensor(input_data).to(self.device)
        
        # Get prediction with uncertainty
        with torch.no_grad():
            predictions = model(input_tensor)
            # Add Monte Carlo dropout for uncertainty estimation
            model.train()
            mc_predictions = []
            for _ in range(100):
                mc_predictions.append(model(input_tensor).cpu().numpy())
            model.eval()
            
        mc_predictions = np.array(mc_predictions)
        mean_prediction = np.mean(mc_predictions)
        uncertainty = np.std(mc_predictions)
        
        return {
            "success_probability": float(mean_prediction),
            "uncertainty": float(uncertainty),
            "confidence_score": float(1 - uncertainty)
        }
    
    def explain_prediction(self, 
                          mission_parameters: Dict[str, float],
                          model_name: str = "mission_success") -> Dict[str, float]:
        """Explain model predictions using SHAP values"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        if self.explainer is None:
            model = self.models[model_name]
            background = torch.randn(100, len(mission_parameters)).to(self.device)
            self.explainer = shap.DeepExplainer(model, background)
        
        input_data = np.array([list(mission_parameters.values())])
        input_data = self.scaler.transform(input_data)
        input_tensor = torch.FloatTensor(input_data).to(self.device)
        
        shap_values = self.explainer.shap_values(input_tensor)
        
        return {
            param: float(shap_value)
            for param, shap_value in zip(mission_parameters.keys(), shap_values[0])
        }
    
    def save_model(self, model_name: str, path: str):
        """Save model and scaler"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model_path = os.path.join(path, f"{model_name}_model.pt")
        scaler_path = os.path.join(path, f"{model_name}_scaler.joblib")
        
        torch.save(self.models[model_name].state_dict(), model_path)
        joblib.dump(self.scaler, scaler_path)
    
    def load_model(self, model_name: str, path: str):
        """Load model and scaler"""
        model_path = os.path.join(path, f"{model_name}_model.pt")
        scaler_path = os.path.join(path, f"{model_name}_scaler.joblib")
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError("Model or scaler file not found")
        
        self.models[model_name].load_state_dict(torch.load(model_path))
        self.scaler = joblib.load(scaler_path)

class AdvancedHealthcareAI:
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.models = {
            "vital_signs": AdvancedNeuralNetwork(5, [64, 32, 16], 3),
            "radiation_effects": TransformerModel(10, 4, 2, 64)
        }
        self.scalers = {}
        self.training_history = {}
    
    def predict_health_status(self,
                            vital_signs: Dict[str, float],
                            radiation_exposure: float,
                            time_series_data: Optional[List[Dict[str, float]]] = None) -> Dict[str, float]:
        """Advanced health status prediction with time series analysis"""
        # Prepare vital signs data
        vital_data = np.array([
            vital_signs.get("heart_rate", 75) / 200,
            vital_signs.get("blood_pressure", 120) / 200,
            vital_signs.get("oxygen_saturation", 98) / 100,
            vital_signs.get("body_temperature", 37) / 40,
            radiation_exposure / 1000
        ]).reshape(1, -1)
        
        # Get predictions from vital signs model
        vital_model = self.models["vital_signs"].to(self.device)
        vital_model.eval()
        
        with torch.no_grad():
            vital_input = torch.FloatTensor(vital_data).to(self.device)
            vital_predictions = vital_model(vital_input).cpu().numpy()[0]
        
        # If time series data is available, use transformer model
        if time_series_data is not None:
            time_series_input = self._prepare_time_series(time_series_data)
            radiation_model = self.models["radiation_effects"].to(self.device)
            radiation_model.eval()
            
            with torch.no_grad():
                radiation_predictions = radiation_model(time_series_input).cpu().numpy()
        
        return {
            "health_score": float(vital_predictions[0]),
            "radiation_risk": float(vital_predictions[1]),
            "adaptation_level": float(vital_predictions[2]),
            "long_term_risk": float(radiation_predictions[0]) if time_series_data else None
        }
    
    def _prepare_time_series(self, time_series_data: List[Dict[str, float]]) -> torch.Tensor:
        """Prepare time series data for transformer model"""
        # Convert time series data to tensor
        features = []
        for data_point in time_series_data:
            features.append([
                data_point.get("heart_rate", 75) / 200,
                data_point.get("blood_pressure", 120) / 200,
                data_point.get("oxygen_saturation", 98) / 100,
                data_point.get("body_temperature", 37) / 40,
                data_point.get("radiation_exposure", 0) / 1000,
                data_point.get("sleep_quality", 0.8),
                data_point.get("stress_level", 0.5),
                data_point.get("physical_activity", 0.6),
                data_point.get("nutrition_score", 0.7),
                data_point.get("cognitive_performance", 0.8)
            ])
        
        return torch.FloatTensor(features).unsqueeze(0).to(self.device) 