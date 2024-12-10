import { PLANETARY_DATA } from './constants.js';

export class AtmosphericModel {
  calculateDensity(altitude, planet = 'EARTH') {
    const planetData = PLANETARY_DATA[planet];
    const baseP = planetData.atmosphere.pressure;
    const g = 9.81; // m/s²
    const R = 287.05; // specific gas constant for air
    const T = this.calculateTemperature(altitude);
    
    return baseP * Math.exp(-g * altitude / (R * T));
  }

  calculateTemperature(altitude) {
    // Simplified atmospheric temperature model
    const baseTemp = 288.15; // K (15°C) at sea level
    const lapseRate = -0.0065; // K/m standard temperature lapse rate
    return baseTemp + lapseRate * altitude;
  }

  calculatePressure(altitude, planet = 'EARTH') {
    const density = this.calculateDensity(altitude, planet);
    const temperature = this.calculateTemperature(altitude);
    const R = 287.05;
    
    return density * R * temperature;
  }
}