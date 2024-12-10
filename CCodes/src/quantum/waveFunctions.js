import { create, all } from 'mathjs';
const math = create(all);

export class WaveFunctions {
  calculateSchrodingerEquation(psi, V, E, m, x) {
    const ℏ = 1.054571817e-34; // Planck's constant / 2π
    
    // Solving time-independent Schrödinger equation
    // -ℏ²/2m * d²ψ/dx² + Vψ = Eψ
    const d2psi = math.derivative(psi, x, 2);
    return (-Math.pow(ℏ, 2) / (2 * m)) * d2psi + V * psi - E * psi;
  }

  harmonicOscillator(n, x) {
    const ℏ = 1.054571817e-34;
    const m = 9.1093837015e-31; // electron mass
    const ω = 1e15; // angular frequency
    
    // Calculate Hermite polynomial
    const hermite = this.calculateHermitePolynomial(n, x);
    
    // Normalization constant
    const N = 1 / Math.sqrt(Math.pow(2, n) * math.factorial(n)) * 
              Math.pow(m * ω / (Math.PI * ℏ), 0.25);
    
    // Wave function
    return N * hermite * Math.exp(-m * ω * x * x / (2 * ℏ));
  }

  calculateHermitePolynomial(n, x) {
    if (n === 0) return 1;
    if (n === 1) return 2 * x;
    return 2 * x * this.calculateHermitePolynomial(n - 1, x) - 
           2 * (n - 1) * this.calculateHermitePolynomial(n - 2, x);
  }
}