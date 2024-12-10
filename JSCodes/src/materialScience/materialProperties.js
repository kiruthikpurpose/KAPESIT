import { create, all } from 'mathjs';
const math = create(all);

export class MaterialProperties {
  calculateThermalConductivity(temperature, pressure, materialConstants) {
    const { k0, alpha, beta } = materialConstants;
    return k0 * Math.pow(temperature, alpha) * Math.pow(pressure, beta);
  }

  calculateStressStrain(stress, youngsModulus) {
    return stress / youngsModulus;
  }

  calculateRadiationEffect(initialProperties, radiationDose, decayConstant) {
    return initialProperties * Math.exp(-decayConstant * radiationDose);
  }
}