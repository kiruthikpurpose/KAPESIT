import numpy as np
from pymatgen.core import Structure, Lattice
from kapesit.materials.prediction import MaterialPropertyPredictor, MaterialDiscovery
import matplotlib.pyplot as plt
import seaborn as sns

def create_training_data():
    """Create a small dataset of structures and their formation energies."""
    structures = []
    properties = []
    
    # Create some simple binary compounds
    elements = ["Fe", "O", "Si", "Al"]
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            # Create a simple cubic structure
            lattice = Lattice.cubic(4.0)
            structure = Structure(
                lattice=lattice,
                species=[elements[i], elements[j]],
                coords=[[0, 0, 0], [0.5, 0.5, 0.5]]
            )
            structures.append(structure)
            
            # Assign a random formation energy
            # In practice, these would come from DFT calculations
            properties.append(np.random.rand() * 2 - 1)
    
    return structures, properties

def plot_optimization_history(history):
    """Plot the optimization history."""
    properties = [m["best_property"] for m in history]
    iterations = range(len(properties))
    
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    plt.plot(iterations, properties, 'b-', label='Best Property')
    plt.fill_between(iterations, properties, alpha=0.2)
    
    plt.xlabel('Iteration')
    plt.ylabel('Formation Energy (eV/atom)')
    plt.title('Material Discovery Optimization History')
    plt.legend()
    
    plt.savefig('optimization_history.png')
    plt.close()

def main():
    # Create training data
    print("Creating training data...")
    structures, properties = create_training_data()
    
    # Initialize predictor
    print("Initializing property predictor...")
    predictor = MaterialPropertyPredictor(
        model_type="neural_network",
        feature_type="composition",
        target_property="formation_energy"
    )
    
    # Train the model
    print("Training the model...")
    history = predictor.train(
        structures=structures,
        properties=properties,
        num_epochs=50,
        batch_size=4,
        learning_rate=1e-3
    )
    
    # Plot training history
    plt.figure(figsize=(10, 6))
    plt.plot(history["train_losses"], label='Training Loss')
    plt.plot(history["val_losses"], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Model Training History')
    plt.legend()
    plt.savefig('training_history.png')
    plt.close()
    
    # Initialize material discovery
    print("Initializing material discovery...")
    search_space = {
        "Fe": ["Fe"],
        "O": ["O"],
        "Si": ["Si"],
        "Al": ["Al"]
    }
    
    discovery = MaterialDiscovery(
        predictor=predictor,
        search_space=search_space,
        target_property="formation_energy",
        optimization_direction="minimize"
    )
    
    # Run optimization
    print("Running material discovery optimization...")
    results = discovery.optimize(
        num_iterations=20,
        candidates_per_iteration=5
    )
    
    # Plot optimization history
    plot_optimization_history(results["optimization_history"])
    
    # Analyze results
    analysis = discovery.analyze_results()
    print("\nOptimization Results:")
    print(f"Final Formation Energy: {analysis['final_property']:.4f} eV/atom")
    print(f"Total Improvement: {analysis['improvement']:.4f} eV/atom")
    print(f"Convergence Point: Iteration {analysis['convergence_point']}")
    print("\nProperty Statistics:")
    for stat, value in analysis["property_statistics"].items():
        print(f"{stat}: {value:.4f}")
    
    # Save the best model
    print("\nSaving the best model...")
    predictor.save_model("best_material_predictor")

if __name__ == "__main__":
    main() 