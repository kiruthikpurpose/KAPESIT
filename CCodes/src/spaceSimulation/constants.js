export const ASTRONOMICAL_CONSTANTS = {
  G: 6.67430e-11,  // Universal gravitational constant (m³/kg/s²)
  c: 299792458,    // Speed of light (m/s)
  AU: 149597870700 // Astronomical Unit (m)
};

export const PLANETARY_DATA = {
  EARTH: {
    mass: 5.972e24,    // kg
    radius: 6.371e6,   // m
    atmosphere: {
      pressure: 101325, // Pa at sea level
      composition: {
        nitrogen: 0.78,
        oxygen: 0.21,
        other: 0.01
      }
    }
  },
  MARS: {
    mass: 6.39e23,     // kg
    radius: 3.389e6,   // m
    atmosphere: {
      pressure: 600,    // Pa average
      composition: {
        carbonDioxide: 0.95,
        nitrogen: 0.027,
        other: 0.023
      }
    }
  }
};