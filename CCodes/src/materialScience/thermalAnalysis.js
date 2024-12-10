export class ThermalAnalysis {
  calculateThermalExpansion(initialLength, tempChange, coefficient) {
    return initialLength * (1 + coefficient * tempChange);
  }

  calculateHeatCapacity(mass, tempChange, specificHeat) {
    return mass * specificHeat * tempChange;
  }

  calculateThermalStress(youngsModulus, thermalCoeff, tempChange, constraintFactor = 1) {
    return -youngsModulus * thermalCoeff * tempChange * constraintFactor;
  }

  calculateThermalDiffusivity(thermalConductivity, density, specificHeat) {
    return thermalConductivity / (density * specificHeat);
  }
}