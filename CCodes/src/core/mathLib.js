import { create, all } from 'mathjs';
const math = create(all);

export class MathLib {
  solveLinearSystem(matrix, vector) {
    return math.lusolve(matrix, vector);
  }

  numericalIntegration(func, start, end, steps) {
    const h = (end - start) / steps;
    let result = 0;
    
    // Simpson's rule implementation
    for (let i = 0; i <= steps; i++) {
      const x = start + i * h;
      const coefficient = i === 0 || i === steps ? 1 : (i % 2 === 0 ? 2 : 4);
      result += coefficient * func(x);
    }
    
    return (h / 3) * result;
  }

  rungeKutta4(f, y0, t0, tn, h) {
    const results = [];
    let t = t0;
    let y = y0;

    while (t <= tn) {
      results.push({ t, y });
      
      const k1 = f(t, y);
      const k2 = f(t + h/2, y + (h/2)*k1);
      const k3 = f(t + h/2, y + (h/2)*k2);
      const k4 = f(t + h, y + h*k3);
      
      y = y + (h/6)*(k1 + 2*k2 + 2*k3 + k4);
      t = t + h;
    }

    return results;
  }
}