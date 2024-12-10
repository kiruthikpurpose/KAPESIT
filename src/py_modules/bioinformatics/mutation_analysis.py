from typing import Dict, List, Set
import math
import random

class MutationSimulator:
    def __init__(self, base_sequence: str):
        self.original_sequence = base_sequence.upper()
        self.current_sequence = self.original_sequence
        self.mutation_history = []
        
    def apply_point_mutation(self, position: int, new_base: str) -> str:
        if 0 <= position < len(self.current_sequence):
            self.current_sequence = (self.current_sequence[:position] + 
                                   new_base + 
                                   self.current_sequence[position + 1:])
            self.mutation_history.append(("point", position, new_base))
        return self.current_sequence
    
    def simulate_random_mutations(self, mutation_rate: float, 
                                generations: int) -> List[str]:
        sequence_history = [self.current_sequence]
        
        for _ in range(generations):
            for position in range(len(self.current_sequence)):
                if random.random() < mutation_rate:
                    new_base = random.choice(['A', 'T', 'C', 'G'])
                    self.apply_point_mutation(position, new_base)
            sequence_history.append(self.current_sequence)
            
        return sequence_history
    
    def calculate_mutation_impact(self) -> Dict[str, float]:
        differences = sum(1 for i in range(len(self.original_sequence))
                        if self.original_sequence[i] != self.current_sequence[i])
        
        return {
            "mutation_count": len(self.mutation_history),
            "sequence_identity": 1 - (differences / len(self.original_sequence)),
            "gc_content_change": (
                self.current_sequence.count('G') + self.current_sequence.count('C')
            ) / len(self.current_sequence) - (
                self.original_sequence.count('G') + self.original_sequence.count('C')
            ) / len(self.original_sequence)
        }