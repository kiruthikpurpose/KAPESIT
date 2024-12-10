import { Matrix } from 'ml-matrix';

export class FluidSimulator {
  private size: number;
  private density: Matrix;
  private velocity: { x: Matrix; y: Matrix };
  private diffusion: number;
  private viscosity: number;

  constructor(size: number, diffusion: number, viscosity: number) {
    this.size = size;
    this.diffusion = diffusion;
    this.viscosity = viscosity;
    
    this.density = new Matrix(size, size);
    this.velocity = {
      x: new Matrix(size, size),
      y: new Matrix(size, size)
    };
  }

  public step(dt: number): void {
    this.diffuse(this.velocity.x, this.viscosity, dt);
    this.diffuse(this.velocity.y, this.viscosity, dt);
    
    this.project();
    this.advect(this.velocity.x, dt);
    this.advect(this.velocity.y, dt);
    
    this.project();
    this.diffuse(this.density, this.diffusion, dt);
    this.advect(this.density, dt);
  }

  private diffuse(x: Matrix, diff: number, dt: number): void {
    const a = dt * diff * (this.size - 2) * (this.size - 2);
    this.linearSolve(x, a, 1 + 6 * a);
  }

  private project(): void {
    const div = new Matrix(this.size, this.size);
    const p = new Matrix(this.size, this.size);

    for (let i = 1; i < this.size - 1; i++) {
      for (let j = 1; j < this.size - 1; j++) {
        div.set(i, j, -0.5 * (
          this.velocity.x.get(i + 1, j) -
          this.velocity.x.get(i - 1, j) +
          this.velocity.y.get(i, j + 1) -
          this.velocity.y.get(i, j - 1)
        ) / this.size);
      }
    }

    this.linearSolve(p, 1, 6);

    for (let i = 1; i < this.size - 1; i++) {
      for (let j = 1; j < this.size - 1; j++) {
        this.velocity.x.set(i, j, this.velocity.x.get(i, j) - 0.5 * (p.get(i + 1, j) - p.get(i - 1, j)) * this.size);
        this.velocity.y.set(i, j, this.velocity.y.get(i, j) - 0.5 * (p.get(i, j + 1) - p.get(i, j - 1)) * this.size);
      }
    }
  }

  private advect(d: Matrix, dt: number): void {
    const d0 = d.clone();
    
    for (let i = 1; i < this.size - 1; i++) {
      for (let j = 1; j < this.size - 1; j++) {
        let x = i - dt * this.velocity.x.get(i, j) * this.size;
        let y = j - dt * this.velocity.y.get(i, j) * this.size;
        
        x = Math.max(0.5, Math.min(this.size - 1.5, x));
        y = Math.max(0.5, Math.min(this.size - 1.5, y));
        
        const i0 = Math.floor(x);
        const i1 = i0 + 1;
        const j0 = Math.floor(y);
        const j1 = j0 + 1;
        
        const s1 = x - i0;
        const s0 = 1 - s1;
        const t1 = y - j0;
        const t0 = 1 - t1;
        
        d.set(i, j,
          s0 * (t0 * d0.get(i0, j0) + t1 * d0.get(i0, j1)) +
          s1 * (t0 * d0.get(i1, j0) + t1 * d0.get(i1, j1))
        );
      }
    }
  }

  private linearSolve(x: Matrix, a: number, c: number): void {
    for (let k = 0; k < 20; k++) {
      for (let i = 1; i < this.size - 1; i++) {
        for (let j = 1; j < this.size - 1; j++) {
          x.set(i, j,
            (x.get(i - 1, j) + x.get(i + 1, j) +
             x.get(i, j - 1) + x.get(i, j + 1) +
             a * x.get(i, j)) / c
          );
        }
      }
    }
  }
}