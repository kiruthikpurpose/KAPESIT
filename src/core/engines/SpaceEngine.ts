import { Vector3 } from 'three';
import { calculateGravitationalForce } from '../../utils/physics';
import { type CelestialBody } from '../../types/space';
import { SolarSystemData } from '../data/SolarSystemData';

export class SpaceEngine {
  private bodies: CelestialBody[] = [];

  constructor() {
    this.initializeSolarSystem();
  }

  private initializeSolarSystem(): void {
    this.bodies = SolarSystemData.getInitialBodies();
  }

  public updatePositions(deltaTime: number): void {
    for (let i = 0; i < this.bodies.length; i++) {
      const body = this.bodies[i];
      const totalForce = this.calculateTotalForce(body, i);
      this.updateBodyPosition(body, totalForce, deltaTime);
    }
  }

  private calculateTotalForce(body: CelestialBody, bodyIndex: number): Vector3 {
    const totalForce = new Vector3(0, 0, 0);
    
    for (let j = 0; j < this.bodies.length; j++) {
      if (bodyIndex !== j) {
        const force = calculateGravitationalForce(body, this.bodies[j]);
        totalForce.add(force);
      }
    }

    return totalForce;
  }

  private updateBodyPosition(body: CelestialBody, force: Vector3, deltaTime: number): void {
    const acceleration = force.multiplyScalar(1 / body.mass);
    body.velocity.add(acceleration.multiplyScalar(deltaTime));
    body.position.add(body.velocity.clone().multiplyScalar(deltaTime));
  }

  public getBodies(): CelestialBody[] {
    return this.bodies;
  }
}