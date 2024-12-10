export class RelativisticPhysics {
  constructor() {
    this.c = 299792458; // Speed of light in m/s
  }

  calculateLorentzFactor(velocity) {
    const beta = velocity / this.c;
    return 1 / Math.sqrt(1 - beta * beta);
  }

  calculateTimeDilation(properTime, velocity) {
    return properTime * this.calculateLorentzFactor(velocity);
  }

  calculateLengthContraction(properLength, velocity) {
    return properLength / this.calculateLorentzFactor(velocity);
  }

  calculateRelativisticMomentum(restMass, velocity) {
    return restMass * velocity * this.calculateLorentzFactor(velocity);
  }

  calculateRelativisticEnergy(restMass, velocity) {
    const gamma = this.calculateLorentzFactor(velocity);
    return restMass * Math.pow(this.c, 2) * gamma;
  }

  calculateRestEnergy(mass) {
    return mass * Math.pow(this.c, 2);
  }

  calculateRelativisticDopplerEffect(frequency, velocity, angle = 0) {
    const beta = velocity / this.c;
    const gamma = this.calculateLorentzFactor(velocity);
    return frequency * gamma * (1 - beta * Math.cos(angle));
  }

  calculateGravitationalRedshift(frequency, gravitationalPotential) {
    return frequency * Math.sqrt(1 + 2 * gravitationalPotential / Math.pow(this.c, 2));
  }

  calculateSchwarzschildRadius(mass) {
    const G = 6.67430e-11; // Gravitational constant
    return (2 * G * mass) / Math.pow(this.c, 2);
  }
}