import numpy as np
import random
from car import Car


class Population:
    def __init__(self, size=50, mutation_rate=0.20):
        self.size = size
        self.mutation_rate = mutation_rate
        self.generation = 1
        self.cars = [Car() for _ in range(size)]

    def update(self, obstacles_rects):
        alive_count = 0
        for car in self.cars:
            if car.alive:
                car.update(obstacles_rects)
                alive_count += 1
        return alive_count

    def get_best_car(self):
        sorted_cars = sorted(self.cars, key=lambda x: x.score, reverse=True)

        for car in sorted_cars:
            if car.alive:
                return car
        return None

    def draw(self, screen):
        for car in self.cars:
            if car.alive:
                car.draw(screen)

    def is_extinct(self):
        for car in self.cars:
            if car.alive:
                return False
        return True

    def evolve(self):
        self.cars.sort(key=lambda x: x.score, reverse=True)
        print(f"Gen {self.generation} Best Fitness: {int(self.cars[0].score)}")

        new_cars = []

        best_cars = self.cars[: self.size // 10]
        for elite in best_cars:
            child = Car()
            child.controller.set_flat_weights(elite.controller.get_flat_weights())
            new_cars.append(child)

        while len(new_cars) < self.size:
            top_half = self.cars[: self.size // 2]
            parent_a = random.choice(top_half)
            parent_b = random.choice(top_half)

            child_dna = self.crossover(parent_a, parent_b)
            child_dna = self.mutate(child_dna)

            child = Car()
            child.controller.set_flat_weights(child_dna)
            new_cars.append(child)

        self.cars = new_cars
        self.generation += 1

    def crossover(self, parent_a, parent_b):
        dna_a = parent_a.controller.get_flat_weights()
        dna_b = parent_b.controller.get_flat_weights()
        split = random.randint(0, len(dna_a))
        return np.concatenate((dna_a[:split], dna_b[split:]))

    def mutate(self, dna):
        for i in range(len(dna)):
            if random.random() < self.mutation_rate:
                mutation_value = np.random.randn() * 0.5
                dna[i] += mutation_value
        return dna
