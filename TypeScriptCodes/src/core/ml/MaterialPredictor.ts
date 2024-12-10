import * as tf from '@tensorflow/tfjs';
import { Material, MaterialProperties } from '../../types/materials';

export class MaterialPredictor {
  private model: tf.LayersModel;

  constructor() {
    this.initializeModel();
  }

  private async initializeModel(): Promise<void> {
    this.model = tf.sequential({
      layers: [
        tf.layers.dense({ units: 64, activation: 'relu', inputShape: [4] }),
        tf.layers.dense({ units: 32, activation: 'relu' }),
        tf.layers.dense({ units: 4 })
      ]
    });

    this.model.compile({
      optimizer: tf.train.adam(),
      loss: 'meanSquaredError'
    });
  }

  public async trainOnMaterial(material: Material, conditions: number[][]): Promise<void> {
    const inputData = tf.tensor2d(conditions);
    const outputData = tf.tensor2d(conditions.map(c => [
      material.properties.density,
      material.properties.meltingPoint,
      material.properties.tensileStrength,
      material.properties.thermalConductivity
    ]));

    await this.model.fit(inputData, outputData, {
      epochs: 100,
      batchSize: 32
    });

    inputData.dispose();
    outputData.dispose();
  }

  public async predictProperties(
    conditions: number[]
  ): Promise<MaterialProperties> {
    const input = tf.tensor2d([conditions]);
    const prediction = this.model.predict(input) as tf.Tensor;
    const values = await prediction.data();

    input.dispose();
    prediction.dispose();

    return {
      density: values[0],
      meltingPoint: values[1],
      tensileStrength: values[2],
      thermalConductivity: values[3]
    };
  }
}