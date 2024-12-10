export class SequenceAnalysis {
  calculateGCContent(sequence) {
    const gcCount = (sequence.match(/[GC]/g) || []).length;
    return (gcCount / sequence.length) * 100;
  }

  calculateHammingDistance(seq1, seq2) {
    if (seq1.length !== seq2.length) {
      throw new Error('Sequences must be of equal length');
    }
    
    let distance = 0;
    for (let i = 0; i < seq1.length; i++) {
      if (seq1[i] !== seq2[i]) distance++;
    }
    return distance;
  }

  predictViability(sequence, environmentalFactors) {
    const { temperature, radiation, pressure } = environmentalFactors;
    const gcContent = this.calculateGCContent(sequence);
    
    // Simplified viability score based on GC content and environmental factors
    const temperatureScore = 1 - Math.abs(temperature - 310) / 310;
    const radiationResistance = gcContent / 100;
    const pressureAdaptation = Math.exp(-Math.abs(pressure - 1) / 10);
    
    return (temperatureScore + radiationResistance + pressureAdaptation) / 3;
  }
}