import { type Material } from '../../types/materials';

export class MaterialsData {
  public static getInitialMaterials(): Material[] {
    return [
      {
        name: 'Titanium Alloy',
        properties: {
          density: 4500,
          meltingPoint: 1668,
          tensileStrength: 1000,
          thermalConductivity: 21.9
        }
      }
    ];
  }
}