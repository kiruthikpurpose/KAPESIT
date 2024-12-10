export class ParticlePhysics {
  constructor() {
    this.c = 299792458; // speed of light in m/s
  }

  calculateRelativisticMass(restMass, velocity) {
    const beta = velocity / this.c;
    return restMass / Math.sqrt(1 - beta * beta);
  }

  calculateDeBroglieWavelength(momentum) {
    const h = 6.62607015e-34; // Planck constant
    return h / momentum;
  }

  calculateComptonWavelength(restMass) {
    const h = 6.62607015e-34;
    return h / (restMass * this.c);
  }

  calculatePairProductionEnergy(particleMass) {
    return 2 * particleMass * Math.pow(this.c, 2);
  }

  calculateUncertainty(positionUncertainty, momentumUncertainty) {
    const ℏ = 1.054571817e-34;
    return positionUncertainty * momentumUncertainty >= ℏ / 2;
  }
}