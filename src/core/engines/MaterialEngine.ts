import { type Material, type MaterialProperties } from '../../types/materials';
import { MaterialsData } from '../data/MaterialsData';
import { MaterialAnalyzer } from '../analyzers/MaterialAnalyzer';

export class MaterialEngine {
  private materials: Map<string, Material> = new Map();
  private analyzer: MaterialAnalyzer;

  constructor() {
    this.analyzer = new MaterialAnalyzer();
    this.initializeMaterials();
  }

  private initializeMaterials(): void {
    MaterialsData.getInitialMaterials().forEach(material => {
      this.addMaterial(material);
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

    return this.analyzer.analyze(material, temperature, pressure);
  }
}