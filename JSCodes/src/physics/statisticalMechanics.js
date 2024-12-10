import { create, all } from 'mathjs';
const math = create(all);

export class StatisticalMechanics {
  constructor() {
    this.kB = 1.380649e-23; // Boltzmann constant
    this.h = 6.62607015e-34; // Planck constant
  }

  calculatePartitionFunction(energyLevels, temperature) {
    return energyLevels.reduce((sum, energy) => 
      sum + Math.exp(-energy / (this.kB * temperature)), 0);
  }

  calculateBoseEinsteinDistribution(energy, temperature, chemicalPotential = 0) {
    return 1 / (Math.exp((energy - chemicalPotential) / (this.kB * temperature)) - 1);
  }

  calculateFermiDiracDistribution(energy, temperature, fermiEnergy) {
    return 1 / (Math.exp((energy - fermiEnergy) / (this.kB * temperature)) + 1);
  }

  calculateMaxwellBoltzmannDistribution(velocity, mass, temperature) {
    const factor = mass / (2 * Math.PI * this.kB * temperature);
    return 4 * Math.PI * Math.pow(factor, 1.5) * 
           Math.pow(velocity, 2) * 
           Math.exp(-mass * velocity * velocity / (2 * this.kB * temperature));
  }

  calculateEntropyStatistical(microstates) {
    return this.kB * Math.log(microstates);
  }
}