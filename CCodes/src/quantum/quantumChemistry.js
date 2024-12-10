import { create, all } from 'mathjs';
const math = create(all);

export class QuantumChemistry {
  constructor() {
    this.ℏ = 1.054571817e-34;  // Reduced Planck constant
    this.me = 9.1093837015e-31; // Electron mass
    this.e = 1.602176634e-19;   // Elementary charge
    this.a0 = 5.29177210903e-11; // Bohr radius
  }

  calculateHydrogenWavefunction(n, l, m, r, theta, phi) {
    const normalizedR = r / this.a0;
    const radialPart = this.calculateRadialWavefunction(n, l, normalizedR);
    const angularPart = this.calculateSphericalHarmonic(l, m, theta, phi);
    return radialPart * angularPart;
  }

  calculateRadialWavefunction(n, l, r) {
    // Simplified Laguerre polynomial calculation for hydrogen-like atoms
    const rho = (2 * r) / n;
    const L = this.calculateAssociatedLaguerre(n - l - 1, 2 * l + 1, rho);
    const norm = Math.sqrt(Math.pow((2 / n), 3) * 
                math.factorial(n - l - 1) / (2 * n * math.factorial(n + l)));
    return norm * Math.exp(-rho / 2) * Math.pow(rho, l) * L;
  }

  calculateSphericalHarmonic(l, m, theta, phi) {
    const P = this.calculateLegendrePolynomial(l, m, Math.cos(theta));
    const norm = Math.sqrt(((2 * l + 1) * math.factorial(l - m)) / 
                (4 * Math.PI * math.factorial(l + m)));
    return norm * P * Math.exp(1i * m * phi);
  }

  calculateAssociatedLaguerre(n, alpha, x) {
    if (n === 0) return 1;
    if (n === 1) return 1 + alpha - x;
    return ((2 * n - 1 + alpha - x) * this.calculateAssociatedLaguerre(n - 1, alpha, x) - 
            (n - 1 + alpha) * this.calculateAssociatedLaguerre(n - 2, alpha, x)) / n;
  }

  calculateLegendrePolynomial(l, m, x) {
    if (l === m) return Math.pow(-1, m) * math.factorial(2 * m - 1) * 
                  Math.pow(1 - x * x, m / 2);
    if (l === m + 1) return x * (2 * m + 1) * this.calculateLegendrePolynomial(m, m, x);
    return (x * (2 * l - 1) * this.calculateLegendrePolynomial(l - 1, m, x) - 
            (l + m - 1) * this.calculateLegendrePolynomial(l - 2, m, x)) / (l - m);
  }

  calculateMolecularOrbital(coordinates, basisFunctions, coefficients) {
    return coordinates.map(coord => {
      return basisFunctions.reduce((sum, basis, i) => 
        sum + coefficients[i] * basis(...coord), 0);
    });
  }
}