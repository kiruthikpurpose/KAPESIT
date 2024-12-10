from typing import Dict, List, Set
import math
from datetime import datetime

class GeneticSequence:
    def __init__(self, sequence: str, metadata: Dict[str, str] = None):
        self.sequence = sequence.upper()
        self.metadata = metadata or {}
        self.analysis_results = {}

    def calculate_gc_content(self) -> float:
        """Calculate GC content percentage"""
        if not self.sequence:
            return 0.0
        gc_count = sum(1 for base in self.sequence if base in 'GC')
        return (gc_count / len(self.sequence)) * 100

    def find_motifs(self, motif_length: int = 6) -> Dict[str, int]:
        """Find recurring motifs in the sequence"""
        motifs = {}
        for i in range(len(self.sequence) - motif_length + 1):
            motif = self.sequence[i:i + motif_length]
            motifs[motif] = motifs.get(motif, 0) + 1
        return {k: v for k, v in motifs.items() if v > 1}

class SpaceBioinformatics:
    def __init__(self):
        self.radiation_tolerance_threshold = 0.75
        self.mutation_rate_space = 2.5e-8  # mutations per base per year in space
        self.sequences_database = {}

    def analyze_radiation_resistance(self, sequence: GeneticSequence) -> Dict[str, float]:
        """Analyze potential radiation resistance of genetic sequence"""
        results = {}
        
        # GC content correlation with radiation resistance
        gc_content = sequence.calculate_gc_content()
        gc_factor = min(gc_content / 65.0, 1.0)  # 65% GC content as optimal
        
        # DNA repair gene motifs (simplified)
        repair_motifs = {"GAATTC", "GATATC", "TCTAGA", "CTGCAG"}
        found_motifs = sequence.find_motifs()
        repair_score = sum(1 for motif in found_motifs if motif in repair_motifs)
        
        # Calculate overall radiation resistance score
        results["gc_contribution"] = gc_factor
        results["repair_capacity"] = repair_score / len(repair_motifs)
        results["overall_resistance"] = (gc_factor * 0.6 + 
                                       (repair_score / len(repair_motifs)) * 0.4)
        
        return results

    def predict_space_viability(self, 
                              sequence: GeneticSequence, 
                              exposure_time_years: float,
                              radiation_level: float) -> Dict[str, float]:
        """Predict genetic viability in space conditions"""
        results = {}
        
        # Analyze radiation resistance
        radiation_analysis = self.analyze_radiation_resistance(sequence)
        
        # Calculate mutation accumulation
        expected_mutations = (len(sequence.sequence) * 
                            self.mutation_rate_space * 
                            exposure_time_years * 
                            radiation_level)
        
        # Viability calculations
        radiation_protection = radiation_analysis["overall_resistance"]
        mutation_tolerance = math.exp(-expected_mutations / 1000)  # simplified model
        
        results["radiation_protection"] = radiation_protection
        results["mutation_tolerance"] = mutation_tolerance
        results["viability_score"] = (radiation_protection * 0.7 + 
                                    mutation_tolerance * 0.3)
        
        return results