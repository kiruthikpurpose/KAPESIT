import { Vector3 } from 'three';

export interface CelestialBody {
  name: string;
  mass: number;
  radius: number;
  position: Vector3;
  velocity: Vector3;
}