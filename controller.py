import tensorflow as tf
import numpy as np
import os


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class NeuralNetwork:
    def __init__(self, input_size=5, hidden_size=8, output_size=2):
        self.input_shape = (input_size,)

        self.model = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(input_shape=(input_size,)),
                tf.keras.layers.Dense(hidden_size, activation="tanh"),
                tf.keras.layers.Dense(output_size, activation="tanh"),
            ]
        )

        self.model.build((None, input_size))

    def forward(self, sensors):
        """
        Fast inference using __call__ instead of .predict() to reduce overhead
        """

        input_tensor = tf.convert_to_tensor([sensors], dtype=tf.float32)

        output_tensor = self.model(input_tensor, training=False)

        return output_tensor.numpy().flatten()

    def get_flat_weights(self):
        """
        Extracts all weights/biases and flattens them into a single 1D array.
        Used to create the 'DNA' for the Genetic Algorithm.
        """
        weights = self.model.get_weights()
        flat_weights = np.concatenate([w.flatten() for w in weights])
        return flat_weights

    def set_flat_weights(self, flat_weights):
        """
        Takes a 1D array (DNA) and reshapes it back into the model's layers.
        """
        weights = []
        offset = 0

        for w in self.model.get_weights():
            shape = w.shape
            size = np.prod(shape)

            chunk = flat_weights[offset : offset + size]
            reshaped_chunk = chunk.reshape(shape)
            weights.append(reshaped_chunk)

            offset += size

        self.model.set_weights(weights)
