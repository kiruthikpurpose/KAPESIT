import { Vector3 } from 'three';
import { type CelestialBody } from '../../types/space';

export class OrbitalMechanics {
  private readonly G = 6.67430e-11;

  public calculateOrbitalElements(body: CelestialBody, centralBody: CelestialBody): OrbitalElements {
    const r = body.position.clone().sub(centralBody.position);
    const v = body.velocity.clone();
    
    const h = this.calculateAngularMomentum(r, v);
    const e = this.calculateEccentricityVector(r, v, centralBody.mass);
    
    return {
      semiMajorAxis: this.calculateSemiMajorAxis(r.length(), v.length(), centralBody.mass),
      eccentricity: e.length(),
      inclination: this.calculateInclination(h),
      longitudeOfAscendingNode: this.calculateLongitudeOfAscendingNode(h),
      argumentOfPeriapsis: this.calculateArgumentOfPeriapsis(e, h)
    };
  }

  private calculateAngularMomentum(r: Vector3, v: Vector3): Vector3 {
    return r.clone().cross(v);
  }

  private calculateEccentricityVector(r: Vector3, v: Vector3, centralMass: number): Vector3 {
    const mu = this.G * centralMass;
    const vSquared = v.lengthSq();
    const rMag = r.length();
    
    return r.clone()
      .multiplyScalar(vSquared / mu - 1 / rMag)
      .sub(v.clone().multiplyScalar(r.dot(v) / mu));
  }

  private calculateSemiMajorAxis(r: number, v: number, centralMass: number): number {
    const mu = this.G * centralMass;
    return 1 / (2 / r - v * v / mu);
  }

  private calculateInclination(h: Vector3): number {
    return Math.acos(h.z / h.length());
  }

  private calculateLongitudeOfAscendingNode(h: Vector3): number {
    return Math.atan2(h.x, -h.y);
  }

  private calculateArgumentOfPeriapsis(e: Vector3, h: Vector3): number {
    const n = new Vector3(-h.y, h.x, 0).normalize();
    return Math.acos(n.dot(e.normalize()));
  }
}

interface OrbitalElements {
  semiMajorAxis: number;
  eccentricity: number;
  inclination: number;
  longitudeOfAscendingNode: number;
  argumentOfPeriapsis: number;
}