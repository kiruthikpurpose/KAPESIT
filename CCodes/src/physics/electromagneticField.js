export class ElectromagneticField {
  constructor() {
    this.ε0 = 8.8541878128e-12; // Vacuum permittivity
    this.μ0 = 1.25663706212e-6; // Vacuum permeability
    this.c = 299792458; // Speed of light
  }

  calculateElectricField(charge, distance, permittivity = this.ε0) {
    return charge / (4 * Math.PI * permittivity * Math.pow(distance, 2));
  }

  calculateMagneticField(current, distance) {
    return (this.μ0 * current) / (2 * Math.PI * distance);
  }

  calculatePoyntingVector(electricField, magneticField) {
    return {
      magnitude: electricField * magneticField / this.μ0,
      direction: 'perpendicular to E and B'
    };
  }

  calculateRadiationPressure(power, area) {
    return power / (area * this.c);
  }

  calculateWaveImpedance(medium = 'vacuum') {
    if (medium === 'vacuum') {
      return Math.sqrt(this.μ0 / this.ε0);
    }
    // For other media, would need relative permittivity and permeability
    return null;
  }

  calculateSkinDepth(frequency, conductivity, relativePermeability = 1) {
    return Math.sqrt(2 / (2 * Math.PI * frequency * this.μ0 * relativePermeability * conductivity));
  }
}