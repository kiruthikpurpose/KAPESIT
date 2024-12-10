import { Vector3 } from 'three';
import { type CelestialBody } from '../../types/space';

export class RadiationSimulator {
  private readonly SOLAR_RADIATION_CONSTANT = 1361; // W/m² at 1 AU

  public calculateRadiationExposure(
    body: CelestialBody,
    position: Vector3,
    shieldingFactor: number
  ): number {
    const distanceToSun = position.length();
    const radiationIntensity = this.calculateBaseRadiation(distanceToSun);
    const attenuatedRadiation = this.applyShielding(radiationIntensity, shieldingFactor);
    return this.calculateTotalExposure(attenuatedRadiation, body);
  }

  private calculateBaseRadiation(distance: number): number {
    const astronomicalUnit = 149.6e9; // meters
    const distanceInAU = distance / astronomicalUnit;
    return this.SOLAR_RADIATION_CONSTANT / (distanceInAU * distanceInAU);
  }

  private applyShielding(radiation: number, shieldingFactor: number): number {
    return radiation * Math.exp(-shieldingFactor);
  }

  private calculateTotalExposure(radiation: number, body: CelestialBody): number {
    const crossSectionalArea = Math.PI * body.radius * body.radius;
    return radiation * crossSectionalArea;
  }
}