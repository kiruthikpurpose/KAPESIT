import { OrbitalMechanics } from './spaceSimulation/orbitalMechanics.js';
import { AtmosphericModel } from './spaceSimulation/atmosphericModel.js';
import { MaterialProperties } from './materialScience/materialProperties.js';
import { CrystalStructure } from './materialScience/crystalStructure.js';
import { ThermalAnalysis } from './materialScience/thermalAnalysis.js';
import { FluidDynamics } from './fluidMechanics/fluidDynamics.js';
import { SequenceAnalysis } from './bioinformatics/sequenceAnalysis.js';
import { MathLib } from './core/mathLib.js';
import { WaveFunctions } from './quantum/waveFunctions.js';
import { ParticlePhysics } from './quantum/particlePhysics.js';
import { QuantumField } from './quantum/quantumField.js';
import { StatisticalMechanics } from './physics/statisticalMechanics.js';
import { ElectromagneticField } from './physics/electromagneticField.js';
import { QuantumChemistry } from './quantum/quantumChemistry.js';
import { RelativisticPhysics } from './physics/relativisticPhysics.js';
import { QuantumOptics } from './quantum/quantumOptics.js';
import { CondensedMatter } from './physics/condensedMatter.js';
import { PLANETARY_DATA, ASTRONOMICAL_CONSTANTS } from './spaceSimulation/constants.js';

// Initialize all classes
const orbital = new OrbitalMechanics();
const atmosphere = new AtmosphericModel();
const materials = new MaterialProperties();
const crystal = new CrystalStructure();
const thermal = new ThermalAnalysis();
const fluids = new FluidDynamics();
const bioinfo = new SequenceAnalysis();
const mathLib = new MathLib();
const waves = new WaveFunctions();
const particles = new ParticlePhysics();
const quantum = new QuantumField();
const statMech = new StatisticalMechanics();
const emField = new ElectromagneticField();
const qChem = new QuantumChemistry();
const relativity = new RelativisticPhysics();
const qOptics = new QuantumOptics();
const condMatter = new CondensedMatter();

// Example calculations
console.log('\nQuantum Optics:');
const coherentState = qOptics.calculateCoherentState(1.5, 2);
console.log('Coherent state |α=1.5⟩ in n=2 Fock basis:', coherentState);

console.log('\nCondensed Matter:');
const bandStructure = condMatter.calculateBandStructure(0.5, k => Math.sin(k));
console.log('Band structure at k=0.5:', bandStructure);

// Previous calculations
console.log('\nQuantum Chemistry:');
const hydrogenWavefunction = qChem.calculateHydrogenWavefunction(1, 0, 0, 5.29177210903e-11, 0, 0);
console.log('Hydrogen 1s orbital at Bohr radius:', hydrogenWavefunction);

console.log('\nRelativistic Physics:');
const velocity = 0.8 * relativity.c;
console.log('Lorentz factor at 0.8c:', relativity.calculateLorentzFactor(velocity));
console.log('Time dilation at 0.8c (1 second proper time):', 
  relativity.calculateTimeDilation(1, velocity), 'seconds');