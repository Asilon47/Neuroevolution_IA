import numpy as np


class NeuralNetwork:
    def __init__(self, input_size=10, hidden_size=128, output_size=2):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.W1 = np.random.randn(input_size, hidden_size)
        self.b1 = np.zeros(hidden_size)

        self.W2 = np.random.randn(hidden_size, hidden_size // 2)
        self.b2 = np.zeros(hidden_size // 2)

        self.W3 = np.random.randn(hidden_size // 2, hidden_size // 4)
        self.b3 = np.zeros(hidden_size // 4)

        self.W4 = np.random.randn(hidden_size // 4, output_size)
        self.b4 = np.zeros(output_size)

    def forward(self, sensors):
        z1 = np.dot(sensors, self.W1) + self.b1
        a1 = np.tanh(z1)

        z2 = np.dot(a1, self.W2) + self.b2
        a2 = np.tanh(z2)

        z3 = np.dot(a2, self.W3) + self.b3
        a3 = np.tanh(z3)

        z4 = np.dot(a3, self.W4) + self.b4
        output = np.tanh(z4)

        return output

    def get_flat_weights(self):
        """Returns the DNA (all weights flattened into one list)"""
        return np.concatenate(
            [
                self.W1.flatten(),
                self.b1.flatten(),
                self.W2.flatten(),
                self.b2.flatten(),
                self.W3.flatten(),
                self.b3.flatten(),
                self.W4.flatten(),
                self.b4.flatten(),
            ]
        )

    def set_flat_weights(self, flat_weights):
        """Reconstructs the brain from DNA"""

        end_w1 = self.input_size * self.hidden_size
        self.W1 = flat_weights[0:end_w1].reshape(self.input_size, self.hidden_size)

        end_b1 = end_w1 + self.hidden_size
        self.b1 = flat_weights[end_w1:end_b1]

        end_w2 = end_b1 + self.hidden_size * (self.hidden_size // 2)
        self.W2 = flat_weights[end_b1:end_w2].reshape(
            self.hidden_size, self.hidden_size // 2
        )

        end_b2 = end_w2 + (self.hidden_size // 2)
        self.b2 = flat_weights[end_w2:end_b2]

        end_w3 = end_b2 + (self.hidden_size // 2) * (self.hidden_size // 4)
        self.W3 = flat_weights[end_b2:end_w3].reshape(
            self.hidden_size // 2, self.hidden_size // 4
        )

        end_b3 = end_w3 + (self.hidden_size // 4)
        self.b3 = flat_weights[end_w3:end_b3]

        end_w4 = end_b3 + (self.hidden_size // 4) * self.output_size
        self.W4 = flat_weights[end_b3:end_w4].reshape(
            self.hidden_size // 4, self.output_size
        )

        self.b4 = flat_weights[end_w4:]

    def save_model(self, filename="weights_final.npy"):
        """Saves the weights to a file"""
        weights = self.get_flat_weights()
        np.save(filename, weights)
        print(f"controlador guardado: {filename}")
