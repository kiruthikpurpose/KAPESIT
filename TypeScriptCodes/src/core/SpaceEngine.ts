import { Vector3 } from 'three';
import { calculateGravitationalForce } from '../utils/physics';
import type { CelestialBody } from '../types/space';

export class SpaceEngine {
  private bodies: CelestialBody[] = [];

  constructor() {
    this.initializeSolarSystem();
  }

  private initializeSolarSystem(): void {
    this.bodies = [
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

  public updatePositions(deltaTime: number): void {
    for (let i = 0; i < this.bodies.length; i++) {
      const body = this.bodies[i];
      
      // Calculate gravitational forces from all other bodies
      const totalForce = new Vector3(0, 0, 0);
      
      for (let j = 0; j < this.bodies.length; j++) {
        if (i !== j) {
          const force = calculateGravitationalForce(body, this.bodies[j]);
          totalForce.add(force);
        }
      }

      // Update velocity and position using basic Euler integration
      const acceleration = totalForce.multiplyScalar(1 / body.mass);
      body.velocity.add(acceleration.multiplyScalar(deltaTime));
      body.position.add(body.velocity.clone().multiplyScalar(deltaTime));
    }
  }

  public getBodies(): CelestialBody[] {
    return this.bodies;
  }
}