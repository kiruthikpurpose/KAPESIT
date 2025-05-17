import unittest
import numpy as np
from pymatgen.core import Structure, Lattice
from kapesit.materials.prediction import MaterialPropertyPredictor, MaterialDiscovery

class TestMaterialPropertyPredictor(unittest.TestCase):
    def setUp(self):
        # Create a simple test structure
        self.lattice = Lattice.cubic(4.0)
        self.structure = Structure(
            lattice=self.lattice,
            species=["Fe", "O"],
            coords=[[0, 0, 0], [0.5, 0.5, 0.5]]
        )
        
        # Create predictor
        self.predictor = MaterialPropertyPredictor(
            model_type="neural_network",
            feature_type="composition",
            target_property="formation_energy"
        )
    
    def test_feature_extraction(self):
        features = self.predictor._extract_features(self.structure)
        self.assertIsInstance(features, np.ndarray)
        self.assertTrue(len(features) > 0)
    
    def test_model_creation(self):
        model = self.predictor._create_neural_network(10)
        self.assertIsNotNone(model)
    
    def test_training(self):
        # Create dummy training data
        structures = [self.structure] * 10
        properties = np.random.rand(10)
        
        # Train model
        history = self.predictor.train(
            structures=structures,
            properties=properties,
            num_epochs=2  # Use small number for testing
        )
        
        self.assertIn("train_losses", history)
        self.assertIn("val_losses", history)
    
    def test_prediction(self):
        # Train model first
        structures = [self.structure] * 10
        properties = np.random.rand(10)
        self.predictor.train(structures, properties, num_epochs=2)
        
        # Make prediction
        prediction = self.predictor.predict(self.structure)
        self.assertIsInstance(prediction, float)
    
    def test_model_persistence(self):
        # Train model
        structures = [self.structure] * 10
        properties = np.random.rand(10)
        self.predictor.train(structures, properties, num_epochs=2)
        
        # Save model
        self.predictor.save_model("test_model")
        
        # Create new predictor and load model
        new_predictor = MaterialPropertyPredictor()
        new_predictor.load_model("test_model")
        
        # Compare predictions
        pred1 = self.predictor.predict(self.structure)
        pred2 = new_predictor.predict(self.structure)
        self.assertAlmostEqual(pred1, pred2)

class TestMaterialDiscovery(unittest.TestCase):
    def setUp(self):
        # Create predictor
        self.predictor = MaterialPropertyPredictor()
        
        # Create search space
        self.search_space = {
            "Fe": ["Fe"],
            "O": ["O"],
            "Si": ["Si"]
        }
        
        # Create discovery engine
        self.discovery = MaterialDiscovery(
            predictor=self.predictor,
            search_space=self.search_space,
            target_property="formation_energy",
            optimization_direction="minimize"
        )
    
    def test_candidate_generation(self):
        candidates = self.discovery.generate_candidates(num_candidates=5)
        self.assertEqual(len(candidates), 5)
        self.assertTrue(all(isinstance(s, Structure) for s in candidates))
    
    def test_optimization(self):
        # Train predictor first
        structures = [self.discovery._generate_structure({"Fe": 1, "O": 1})] * 10
        properties = np.random.rand(10)
        self.predictor.train(structures, properties, num_epochs=2)
        
        # Run optimization
        results = self.discovery.optimize(
            num_iterations=2,  # Use small number for testing
            candidates_per_iteration=2
        )
        
        self.assertIn("best_property", results)
        self.assertIn("best_structure", results)
        self.assertIn("optimization_history", results)
    
    def test_results_analysis(self):
        # Run optimization first
        structures = [self.discovery._generate_structure({"Fe": 1, "O": 1})] * 10
        properties = np.random.rand(10)
        self.predictor.train(structures, properties, num_epochs=2)
        self.discovery.optimize(num_iterations=2, candidates_per_iteration=2)
        
        # Analyze results
        analysis = self.discovery.analyze_results()
        self.assertIn("final_property", analysis)
        self.assertIn("improvement", analysis)
        self.assertIn("convergence_point", analysis)
        self.assertIn("property_statistics", analysis)

if __name__ == "__main__":
    unittest.main() 