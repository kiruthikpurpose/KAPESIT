import { create, all } from 'mathjs';
const math = create(all);

export class OrbitalMechanics {
  constructor() {
    this.G = 6.67430e-11; // Universal gravitational constant
  }

  calculateOrbitalVelocity(mass, radius) {
    return Math.sqrt((this.G * mass) / radius);
  }

  calculateOrbitalPeriod(mass, semiMajorAxis) {
    return 2 * Math.PI * Math.sqrt(Math.pow(semiMajorAxis, 3) / (this.G * mass));
  }

  calculateEscapeVelocity(mass, radius) {
    return Math.sqrt((2 * this.G * mass) / radius);
  }
}