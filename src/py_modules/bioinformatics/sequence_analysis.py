from typing import Dict, List, Set
import math

class SequenceAnalyzer:
    def __init__(self, sequence: str):
        self.sequence = sequence.upper()
        self.length = len(sequence)
        self.composition = self._calculate_composition()
        
    def _calculate_composition(self) -> Dict[str, int]:
        return {base: self.sequence.count(base) for base in set(self.sequence)}
    
    def find_repeats(self, min_length: int = 3, 
                    max_length: int = 10) -> Dict[str, List[int]]:
        repeats = {}
        
        for length in range(min_length, max_length + 1):
            for i in range(len(self.sequence) - length + 1):
                substr = self.sequence[i:i + length]
                if self.sequence.count(substr) > 1:
                    if substr not in repeats:
                        repeats[substr] = []
                    repeats[substr].append(i)
                    
        return repeats
    
    def calculate_entropy(self) -> float:
        entropy = 0
        for count in self.composition.values():
            p = count / self.length
            entropy -= p * math.log2(p) if p > 0 else 0
        return entropy
    
    def find_motifs(self, motif_pattern: str) -> List[int]:
        positions = []
        pattern_length = len(motif_pattern)
        
        for i in range(len(self.sequence) - pattern_length + 1):
            match = True
            for j in range(pattern_length):
                if motif_pattern[j] != 'N' and motif_pattern[j] != self.sequence[i + j]:
                    match = False
                    break
            if match:
                positions.append(i)
                
        return positions