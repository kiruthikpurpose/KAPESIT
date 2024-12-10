export class CrystalStructure {
  calculateLatticeDensity(latticeConstant, atomsPerUnit, atomicMass) {
    const NA = 6.022e23; // Avogadro's number
    const volumeUnit = Math.pow(latticeConstant, 3); // m³
    return (atomsPerUnit * atomicMass) / (NA * volumeUnit);
  }

  calculateMillerIndices(a, b, c) {
    const gcd = this.findGCD(this.findGCD(a, b), c);
    return {
      h: a / gcd,
      k: b / gcd,
      l: c / gcd
    };
  }

  findGCD(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);
    while (b) {
      const temp = b;
      b = a % b;
      a = temp;
    }
    return a;
  }

  calculateInterplanarSpacing(millerIndices, latticeConstant) {
    const { h, k, l } = millerIndices;
    return latticeConstant / Math.sqrt(h*h + k*k + l*l);
  }
}