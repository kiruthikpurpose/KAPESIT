import { Vector3 } from 'three';
import { type CelestialBody } from '../../types/space';

export class SolarSystemData {
  public static getInitialBodies(): CelestialBody[] {
    return [
      {
        name: 'Sun',
        mass: 1.989e30,
        radius: 696340000,
        position: new Vector3(0, 0, 0),
        velocity: new Vector3(0, 0, 0)
      },
      {
        name: 'Earth',
        mass: 5.972e24,
        radius: 6371000,
        position: new Vector3(149.6e9, 0, 0),
        velocity: new Vector3(0, 29.78e3, 0)
      }
    ];
  }
}