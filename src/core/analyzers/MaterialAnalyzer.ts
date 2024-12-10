import { type Material, type MaterialProperties } from '../../types/materials';

export class MaterialAnalyzer {
  public analyze(
    material: Material,
    temperature: number,
    pressure: number
  ): MaterialProperties {
    const properties = { ...material.properties };
    
    properties.tensileStrength = this.calculateTensileStrength(
      properties.tensileStrength,
      temperature,
      properties.meltingPoint
    );
    
    properties.thermalConductivity = this.calculateThermalConductivity(
      properties.thermalConductivity,
      pressure
    );

    return properties;
  }

  private calculateTensileStrength(
    baseStrength: number,
    temperature: number,
    meltingPoint: number
  ): number {
    const tempFactor = Math.max(0, 1 - (temperature / meltingPoint));
    return baseStrength * tempFactor;
  }

  private calculateThermalConductivity(
    baseConductivity: number,
    pressure: number
  ): number {
    return baseConductivity * (1 + pressure / 1e5);
  }
}