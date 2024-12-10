export interface MaterialProperties {
  density: number;           // kg/m³
  meltingPoint: number;      // Kelvin
  tensileStrength: number;   // MPa
  thermalConductivity: number; // W/(m·K)
}

export interface Material {
  name: string;
  properties: MaterialProperties;
}