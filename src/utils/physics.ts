import { Vector3 } from 'three';
import { type CelestialBody } from '../types/space';

const G = 6.67430e-11; // Gravitational constant

export function calculateGravitationalForce(body1: CelestialBody, body2: CelestialBody): Vector3 {
  const direction = body2.position.clone().sub(body1.position);
  const distance = direction.length();
  
  const forceMagnitude = (G * body1.mass * body2.mass) / (distance * distance);
  
  return direction.normalize().multiplyScalar(forceMagnitude);
}