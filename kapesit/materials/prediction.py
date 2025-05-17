import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Any
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
from ase import Atoms
from ase.io import read
from matminer.featurizers.base import ElementProperty
from matminer.featurizers.composition import ElementFraction
from matminer.featurizers.structure import SiteStatsFingerprint
from pymatgen.core import Structure, Lattice
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.transformations.standard_transformations import SupercellTransformation
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.elasticity import ElasticTensor
from pymatgen.analysis.defects import DefectEntry
from pymatgen.analysis.phase_diagram import PhaseDiagram
import joblib
import os
from scipy.optimize import minimize
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

class MaterialPropertyPredictor:
    def __init__(
        self,
        model_type: str = "neural_network",
        feature_type: str = "composition",
        target_property: str = "formation_energy"
    ):
        self.model_type = model_type
        self.feature_type = feature_type
        self.target_property = target_property
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        
        # Initialize feature generators
        self.element_property = ElementProperty.from_preset("magpie")
        self.element_fraction = ElementFraction()
        self.site_stats = SiteStatsFingerprint()
    
    def _create_neural_network(self, input_size: int) -> nn.Module:
        return nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    
    def _extract_features(self, structure: Structure) -> np.ndarray:
        if self.feature_type == "composition":
            features = self.element_fraction.featurize(structure.composition)
        elif self.feature_type == "element_property":
            features = self.element_property.featurize(structure.composition)
        elif self.feature_type == "site_stats":
            features = self.site_stats.featurize(structure)
        else:
            raise ValueError(f"Unknown feature type: {self.feature_type}")
        
        self.feature_names = self.element_fraction.feature_labels()
        return np.array(features)
    
    def prepare_training_data(
        self,
        structures: List[Structure],
        properties: List[float]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # Extract features
        X = np.array([self._extract_features(s) for s in structures])
        y = np.array(properties)
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Convert to PyTorch tensors
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y).reshape(-1, 1)
        
        return X_tensor, y_tensor
    
    def train(
        self,
        structures: List[Structure],
        properties: List[float],
        validation_split: float = 0.2,
        batch_size: int = 32,
        num_epochs: int = 100,
        learning_rate: float = 1e-3
    ) -> Dict[str, List[float]]:
        # Prepare data
        X, y = self.prepare_training_data(structures, properties)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Create model
        if self.model_type == "neural_network":
            self.model = self._create_neural_network(X.shape[1])
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Training setup
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", factor=0.5, patience=5
        )
        
        # Training loop
        train_losses = []
        val_losses = []
        
        for epoch in range(num_epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train[i:i+batch_size]
                batch_y = y_train[i:i+batch_size]
                
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(X_train)
            train_losses.append(train_loss)
            
            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val)
                val_loss = criterion(val_outputs, y_val).item()
                val_losses.append(val_loss)
            
            # Update learning rate
            scheduler.step(val_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{num_epochs}")
                print(f"Train Loss: {train_loss:.4f}")
                print(f"Val Loss: {val_loss:.4f}")
        
        return {
            "train_losses": train_losses,
            "val_losses": val_losses
        }
    
    def predict(self, structure: Structure) -> float:
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Extract features
        features = self._extract_features(structure)
        features = self.scaler.transform(features.reshape(1, -1))
        
        # Make prediction
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(torch.FloatTensor(features))
        
        return prediction.item()
    
    def save_model(self, path: str) -> None:
        if self.model is None:
            raise ValueError("No model to save")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and scaler
        torch.save(self.model.state_dict(), f"{path}_model.pt")
        joblib.dump(self.scaler, f"{path}_scaler.joblib")
        
        # Save feature names
        with open(f"{path}_features.txt", "w") as f:
            f.write("\n".join(self.feature_names))
    
    def load_model(self, path: str) -> None:
        # Load model
        self.model = self._create_neural_network(len(self.feature_names))
        self.model.load_state_dict(torch.load(f"{path}_model.pt"))
        
        # Load scaler
        self.scaler = joblib.load(f"{path}_scaler.joblib")
        
        # Load feature names
        with open(f"{path}_features.txt", "r") as f:
            self.feature_names = f.read().splitlines()

class MaterialDiscovery:
    def __init__(
        self,
        predictor: MaterialPropertyPredictor,
        search_space: Dict[str, List[str]],
        target_property: str = "formation_energy",
        optimization_direction: str = "minimize"
    ):
        self.predictor = predictor
        self.search_space = search_space
        self.target_property = target_property
        self.optimization_direction = optimization_direction
        self.best_materials = []
    
    def generate_candidates(self, num_candidates: int = 100) -> List[Structure]:
        candidates = []
        for _ in range(num_candidates):
            # Generate random composition
            composition = {
                element: np.random.choice(self.search_space[element])
                for element in self.search_space.keys()
            }
            
            # Generate random structure
            structure = self._generate_structure(composition)
            candidates.append(structure)
        
        return candidates
    
    def _generate_structure(self, composition: Dict[str, float]) -> Structure:
        # Implement structure generation logic
        # This is a simplified version - real implementation would be more complex
        return Structure(
            lattice=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            species=list(composition.keys()),
            coords=[[0, 0, 0]]
        )
    
    def optimize(
        self,
        num_iterations: int = 100,
        candidates_per_iteration: int = 10
    ) -> Dict[str, Any]:
        best_property = float('inf') if self.optimization_direction == "minimize" else float('-inf')
        best_structure = None
        
        for iteration in range(num_iterations):
            # Generate candidates
            candidates = self.generate_candidates(candidates_per_iteration)
            
            # Evaluate candidates
            properties = [self.predictor.predict(s) for s in candidates]
            
            # Update best material
            if self.optimization_direction == "minimize":
                best_idx = np.argmin(properties)
                if properties[best_idx] < best_property:
                    best_property = properties[best_idx]
                    best_structure = candidates[best_idx]
            else:
                best_idx = np.argmax(properties)
                if properties[best_idx] > best_property:
                    best_property = properties[best_idx]
                    best_structure = candidates[best_idx]
            
            # Store results
            self.best_materials.append({
                "iteration": iteration,
                "best_property": best_property,
                "structure": best_structure
            })
        
        return {
            "best_property": best_property,
            "best_structure": best_structure,
            "optimization_history": self.best_materials
        }
    
    def analyze_results(self) -> Dict[str, Any]:
        if not self.best_materials:
            return {}
        
        properties = [m["best_property"] for m in self.best_materials]
        
        return {
            "final_property": properties[-1],
            "improvement": properties[0] - properties[-1],
            "convergence_point": np.argmin(np.diff(properties)),
            "property_statistics": {
                "mean": np.mean(properties),
                "std": np.std(properties),
                "min": np.min(properties),
                "max": np.max(properties)
            }
        }

class CrystalOptimizer:
    def __init__(self, structure: Structure, energy_calculator: Any):
        self.structure = structure
        self.energy_calculator = energy_calculator
        self.spacegroup = SpacegroupAnalyzer(structure).get_space_group_symbol()
        self.matcher = StructureMatcher()
    
    def optimize_lattice(self, max_iterations: int = 100) -> Structure:
        def objective(params):
            a, b, c, alpha, beta, gamma = params
            new_lattice = Lattice.from_parameters(a, b, c, alpha, beta, gamma)
            new_structure = Structure(
                lattice=new_lattice,
                species=self.structure.species,
                coords=self.structure.frac_coords
            )
            return self.energy_calculator.get_energy(new_structure)
        
        initial_params = [
            self.structure.lattice.a,
            self.structure.lattice.b,
            self.structure.lattice.c,
            self.structure.lattice.alpha,
            self.structure.lattice.beta,
            self.structure.lattice.gamma
        ]
        
        bounds = [(0.8 * p, 1.2 * p) for p in initial_params]
        result = minimize(
            objective,
            initial_params,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': max_iterations}
        )
        
        optimized_lattice = Lattice.from_parameters(*result.x)
        return Structure(
            lattice=optimized_lattice,
            species=self.structure.species,
            coords=self.structure.frac_coords
        )
    
    def optimize_atomic_positions(self, max_iterations: int = 100) -> Structure:
        def objective(coords):
            new_structure = Structure(
                lattice=self.structure.lattice,
                species=self.structure.species,
                coords=coords.reshape(-1, 3)
            )
            return self.energy_calculator.get_energy(new_structure)
        
        initial_coords = self.structure.frac_coords.flatten()
        bounds = [(0, 1) for _ in initial_coords]
        
        result = minimize(
            objective,
            initial_coords,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': max_iterations}
        )
        
        return Structure(
            lattice=self.structure.lattice,
            species=self.structure.species,
            coords=result.x.reshape(-1, 3)
        )
    
    def create_supercell(self, scaling_matrix: List[int]) -> Structure:
        transformation = SupercellTransformation(scaling_matrix=scaling_matrix)
        return transformation.apply_transformation(self.structure)
    
    def analyze_symmetry(self) -> Dict[str, Any]:
        analyzer = SpacegroupAnalyzer(self.structure)
        return {
            "spacegroup": analyzer.get_space_group_symbol(),
            "point_group": analyzer.get_point_group_symbol(),
            "crystal_system": analyzer.get_crystal_system(),
            "symmetry_operations": len(analyzer.get_symmetry_operations())
        }

class MultiPropertyPredictor(MaterialPropertyPredictor):
    def __init__(
        self,
        model_type: str = "neural_network",
        feature_type: str = "composition",
        target_properties: List[str] = None
    ):
        super().__init__(model_type, feature_type)
        self.target_properties = target_properties or ["formation_energy", "band_gap", "elastic_modulus"]
        self.models = {}
        self.scalers = {}
    
    def _create_multi_output_network(self, input_size: int) -> nn.Module:
        return nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, len(self.target_properties))
        )
    
    def train(
        self,
        structures: List[Structure],
        properties: Dict[str, List[float]],
        validation_split: float = 0.2,
        batch_size: int = 32,
        num_epochs: int = 100,
        learning_rate: float = 1e-3
    ) -> Dict[str, List[float]]:
        X, y = self.prepare_training_data(structures, properties)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split)
        
        self.model = self._create_multi_output_network(X.shape[1])
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=5)
        
        train_losses = []
        val_losses = []
        
        for epoch in range(num_epochs):
            self.model.train()
            train_loss = 0.0
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train[i:i+batch_size]
                batch_y = y_train[i:i+batch_size]
                
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(X_train)
            train_losses.append(train_loss)
            
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val)
                val_loss = criterion(val_outputs, y_val).item()
                val_losses.append(val_loss)
            
            scheduler.step(val_loss)
        
        return {"train_losses": train_losses, "val_losses": val_losses}
    
    def predict(self, structure: Structure) -> Dict[str, float]:
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        features = self._extract_features(structure)
        features = self.scaler.transform(features.reshape(1, -1))
        
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(torch.FloatTensor(features))
        
        return dict(zip(self.target_properties, predictions[0].numpy()))

class AdvancedMaterialDiscovery(MaterialDiscovery):
    def __init__(
        self,
        predictor: MultiPropertyPredictor,
        search_space: Dict[str, List[str]],
        target_properties: Dict[str, str],
        constraints: Dict[str, Tuple[float, float]] = None
    ):
        super().__init__(predictor, search_space)
        self.target_properties = target_properties
        self.constraints = constraints or {}
        self.phase_diagram = None
    
    def _generate_structure(self, composition: Dict[str, float]) -> Structure:
        # Advanced structure generation with symmetry constraints
        lattice = Lattice.cubic(4.0)
        structure = Structure(
            lattice=lattice,
            species=list(composition.keys()),
            coords=[[0, 0, 0]]
        )
        
        optimizer = CrystalOptimizer(structure, self.predictor)
        return optimizer.optimize_lattice()
    
    def _check_constraints(self, properties: Dict[str, float]) -> bool:
        for prop, (min_val, max_val) in self.constraints.items():
            if prop in properties:
                if not (min_val <= properties[prop] <= max_val):
                    return False
        return True
    
    def optimize(
        self,
        num_iterations: int = 100,
        candidates_per_iteration: int = 10,
        parallel: bool = True
    ) -> Dict[str, Any]:
        best_properties = {prop: float('inf') if direction == "minimize" else float('-inf')
                          for prop, direction in self.target_properties.items()}
        best_structures = {}
        
        def evaluate_candidate(candidate):
            properties = self.predictor.predict(candidate)
            if self._check_constraints(properties):
                return candidate, properties
            return None, None
        
        for iteration in range(num_iterations):
            candidates = self.generate_candidates(candidates_per_iteration)
            
            if parallel:
                with ThreadPoolExecutor() as executor:
                    results = list(executor.map(evaluate_candidate, candidates))
            else:
                results = [evaluate_candidate(c) for c in candidates]
            
            for structure, properties in results:
                if structure is not None:
                    for prop, direction in self.target_properties.items():
                        if direction == "minimize":
                            if properties[prop] < best_properties[prop]:
                                best_properties[prop] = properties[prop]
                                best_structures[prop] = structure
                        else:
                            if properties[prop] > best_properties[prop]:
                                best_properties[prop] = properties[prop]
                                best_structures[prop] = structure
            
            self.best_materials.append({
                "iteration": iteration,
                "best_properties": best_properties.copy(),
                "best_structures": best_structures.copy()
            })
        
        return {
            "best_properties": best_properties,
            "best_structures": best_structures,
            "optimization_history": self.best_materials
        }
    
    def analyze_phase_stability(self, structures: List[Structure]) -> Dict[str, Any]:
        entries = []
        for structure in structures:
            energy = self.predictor.predict(structure)["formation_energy"]
            entries.append(DefectEntry(structure, energy))
        
        self.phase_diagram = PhaseDiagram(entries)
        return {
            "stable_phases": len(self.phase_diagram.stable_entries),
            "unstable_phases": len(self.phase_diagram.unstable_entries),
            "hull_distance": {entry.name: self.phase_diagram.get_hull_distance(entry)
                            for entry in entries}
        }
    
    def analyze_results(self) -> Dict[str, Any]:
        if not self.best_materials:
            return {}
        
        analysis = {}
        for prop in self.target_properties:
            properties = [m["best_properties"][prop] for m in self.best_materials]
            analysis[prop] = {
                "final_value": properties[-1],
                "improvement": properties[0] - properties[-1],
                "convergence_point": np.argmin(np.diff(properties)),
                "statistics": {
                    "mean": np.mean(properties),
                    "std": np.std(properties),
                    "min": np.min(properties),
                    "max": np.max(properties)
                }
            }
        
        return analysis 