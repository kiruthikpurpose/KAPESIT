import Complex from 'complex.js';

export class QuantumSimulator {
  private numQubits: number;
  private stateVector: Complex[];

  constructor(numQubits: number) {
    this.numQubits = numQubits;
    this.stateVector = new Array(1 << numQubits).fill(new Complex(0));
    this.stateVector[0] = new Complex(1); // Initialize to |0⟩ state
  }

  public applyHadamard(qubit: number): void {
    const factor = 1 / Math.sqrt(2);
    for (let i = 0; i < this.stateVector.length; i++) {
      if ((i & (1 << qubit)) === 0) {
        const zero = this.stateVector[i];
        const one = this.stateVector[i | (1 << qubit)];
        this.stateVector[i] = zero.add(one).mul(factor);
        this.stateVector[i | (1 << qubit)] = zero.sub(one).mul(factor);
      }
    }
  }

  public measure(qubit: number): boolean {
    let probability = 0;
    for (let i = 0; i < this.stateVector.length; i++) {
      if ((i & (1 << qubit)) !== 0) {
        probability += Math.pow(this.stateVector[i].abs(), 2);
      }
    }
    
    const result = Math.random() < probability;
    this.collapse(qubit, result);
    return result;
  }

  private collapse(qubit: number, value: boolean): void {
    const newState: Complex[] = new Array(this.stateVector.length).fill(new Complex(0));
    let norm = 0;

    for (let i = 0; i < this.stateVector.length; i++) {
      if (((i & (1 << qubit)) !== 0) === value) {
        newState[i] = this.stateVector[i];
        norm += Math.pow(this.stateVector[i].abs(), 2);
      }
    }

    this.stateVector = newState.map(amp => amp.div(Math.sqrt(norm)));
  }
}