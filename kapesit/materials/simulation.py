import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import minimize
from ase import Atoms
from ase.io import read, write
from ase.optimize import BFGS
from ase.constraints import ExpCellFilter

@dataclass
class Atom:
    symbol: str
    position: np.ndarray
    charge: float = 0.0
    mass: float = 0.0

class MaterialSimulator:
    def __init__(self):
        self.atoms: List[Atom] = []
        self.lattice_vectors: Optional[np.ndarray] = None
        self.energy: float = 0.0
        self.forces: Optional[np.ndarray] = None
    
    def add_atom(self, atom: Atom) -> None:
        self.atoms.append(atom)
    
    def set_lattice(self, vectors: np.ndarray) -> None:
        self.lattice_vectors = vectors
    
    def calculate_energy(self) -> float:
        if not self.atoms:
            return 0.0
        
        total_energy = 0.0
        for i, atom1 in enumerate(self.atoms):
            for j, atom2 in enumerate(self.atoms[i+1:], i+1):
                r = atom2.position - atom1.position
                r_mag = np.linalg.norm(r)
                
                # Lennard-Jones potential
                sigma = 3.4  # Angstroms
                epsilon = 0.0103  # eV
                total_energy += 4 * epsilon * ((sigma/r_mag)**12 - (sigma/r_mag)**6)
        
        self.energy = total_energy
        return total_energy
    
    def calculate_forces(self) -> np.ndarray:
        if not self.atoms:
            return np.zeros((0, 3))
        
        forces = np.zeros((len(self.atoms), 3))
        for i, atom1 in enumerate(self.atoms):
            for j, atom2 in enumerate(self.atoms[i+1:], i+1):
                r = atom2.position - atom1.position
                r_mag = np.linalg.norm(r)
                
                # Force from Lennard-Jones potential
                sigma = 3.4
                epsilon = 0.0103
                force = 24 * epsilon * (2 * (sigma/r_mag)**12 - (sigma/r_mag)**6) * r / (r_mag**2)
                
                forces[i] += force
                forces[j] -= force
        
        self.forces = forces
        return forces
    
    def optimize_structure(self, max_steps: int = 100) -> Dict[str, float]:
        if not self.atoms:
            return {"energy": 0.0, "converged": True}
        
        def objective(x):
            positions = x.reshape(-1, 3)
            for i, atom in enumerate(self.atoms):
                atom.position = positions[i]
            return self.calculate_energy()
        
        def gradient(x):
            positions = x.reshape(-1, 3)
            for i, atom in enumerate(self.atoms):
                atom.position = positions[i]
            return -self.calculate_forces().flatten()
        
        initial_positions = np.array([atom.position for atom in self.atoms])
        result = minimize(
            objective,
            initial_positions.flatten(),
            method='L-BFGS-B',
            jac=gradient,
            options={'maxiter': max_steps}
        )
        
        return {
            "energy": result.fun,
            "converged": result.success,
            "iterations": result.nit
        }
    
    def to_ase_atoms(self) -> Atoms:
        symbols = [atom.symbol for atom in self.atoms]
        positions = [atom.position for atom in self.atoms]
        
        if self.lattice_vectors is not None:
            return Atoms(
                symbols=symbols,
                positions=positions,
                cell=self.lattice_vectors,
                pbc=True
            )
        else:
            return Atoms(symbols=symbols, positions=positions)
    
    def save_structure(self, filename: str) -> None:
        atoms = self.to_ase_atoms()
        write(filename, atoms)
    
    def load_structure(self, filename: str) -> None:
        atoms = read(filename)
        self.atoms = [
            Atom(
                symbol=atom.symbol,
                position=atom.position,
                charge=atom.charge,
                mass=atom.mass
            )
            for atom in atoms
        ]
        self.lattice_vectors = atoms.cell.array if atoms.cell.any() else None
    
    def calculate_elastic_constants(self) -> Dict[str, float]:
        if not self.atoms or self.lattice_vectors is None:
            return {}
        
        atoms = self.to_ase_atoms()
        ecf = ExpCellFilter(atoms)
        opt = BFGS(ecf)
        opt.run(fmax=0.05)
        
        # Calculate elastic constants using finite differences
        # This is a simplified version - real implementation would be more complex
        c11 = 100.0  # Example values
        c12 = 50.0
        c44 = 30.0
        
        return {
            "c11": c11,
            "c12": c12,
            "c44": c44,
            "bulk_modulus": (c11 + 2*c12) / 3,
            "shear_modulus": (c11 - c12) / 2
        }
    
    def predict_phase_stability(self) -> Dict[str, float]:
        if not self.atoms:
            return {}
        
        # Simplified phase stability calculation
        energy = self.calculate_energy()
        volume = np.linalg.det(self.lattice_vectors) if self.lattice_vectors is not None else 0.0
        
        return {
            "formation_energy": energy,
            "volume": volume,
            "energy_per_atom": energy / len(self.atoms) if self.atoms else 0.0,
            "stability_score": -energy / volume if volume > 0 else 0.0
        } 