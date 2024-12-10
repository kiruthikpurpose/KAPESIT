import type { Material, MaterialProperties } from '../types/materials';

export class MaterialEngine {
  private materials: Map<string, Material> = new Map();

  constructor() {
    this.initializeMaterials();
  }

  private initializeMaterials(): void {
    this.addMaterial({
      name: 'Titanium Alloy',
      properties: {
        density: 4500,
        meltingPoint: 1668,
        tensileStrength: 1000,
        thermalConductivity: 21.9
      }
    });
  }

  public addMaterial(material: Material): void {
    this.materials.set(material.name, material);
  }

  public analyzeMaterial(
    materialName: string,
    temperature: number,
    pressure: number
  ): MaterialProperties | null {
    const material = this.materials.get(materialName);
    if (!material) return null;

    // Simulate material property changes under different conditions
    const properties = { ...material.properties };
    
    // Adjust tensile strength based on temperature
    const tempFactor = Math.max(0, 1 - (temperature / material.properties.meltingPoint));
    properties.tensileStrength *= tempFactor;

    // Adjust thermal conductivity based on pressure
    properties.thermalConductivity *= (1 + pressure / 1e5);

    return properties;
  }
}