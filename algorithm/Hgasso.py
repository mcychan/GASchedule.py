from .NsgaII import NsgaII

import numpy as np


# Shehadeh, Hisham & Mustafa, Hossam & Tubishat, Mohammad. (2022).
# A Hybrid Genetic Algorithm and Sperm Swarm Optimization (HGASSO) for Multimodal Functions.
# International Journal of Applied Metaheuristic Computing. 13. 10.4018/IJAMC.292507.
# Copyright (c) 2022 Miller Cy Chan


# Hybrid Genetic Algorithm and Sperm Swarm Optimization (HGASSO)
class Hgasso(NsgaII):
    # Initializes Hybrid Genetic Algorithm and Sperm Swarm Optimization
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3):
        NsgaII.__init__(self, configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)
        self._sBestScore, self._sgBestScore = [], 0
        self._sBest, self._sgBest = [], []
        self._current_position, self._velocity = [], []

    def replacement(self, population):
        populationSize = len(population)

        for i in range(populationSize):
            fitness = population[i].fitness
            if fitness < self._sBestScore[i]:
                population[i].updatePositions(self._current_position[i])
                fitness = population[i].fitness

            if fitness > self._sBestScore[i]:
                self._sBestScore[i] = fitness
                self._sBest[i] = self._current_position[i][:]

            if fitness > self._sgBestScore:
                self._sgBestScore = fitness
                self._sgBest = self._current_position[i][:]

        self.updateVelocities(population)
        return super().replacement(population)

    def initialize(self, population):
        prototype = self._prototype
        size = 0
        populationSize = len(population)
        for i in range(populationSize):
            positions = []
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype(positions)
            if i < 1:
                size = len(positions)
                self._current_position = np.zeros((populationSize, size), dtype=float)
                self._velocity = np.zeros((populationSize, size), dtype=float)

                self._sBest = np.zeros((populationSize, size), dtype=float)
                self._sgBest = np.zeros(populationSize, dtype=float)
                self._sBestScore = np.zeros(populationSize, dtype=float)

            self._sBestScore[i] = population[i].fitness
            self._current_position[i] = np.array(positions)
            self._velocity[i] = np.random.uniform(-.6464, .7157, size) / 3.0

    def updateVelocities(self, population):
        dim = self._velocity.shape
        self._velocity = np.random.random(dim) * np.log10(np.random.uniform(7.0, 14.0, dim)) * self._velocity[:] + \
        np.log10(np.random.uniform(7.0, 14.0, dim)) * np.log10(np.random.uniform(35.5, 38.5, dim)) * (self._sBest - self._current_position) + \
        np.log10(np.random.uniform(7.0, 14.0, dim)) * np.log10(np.random.uniform(35.5, 38.5, dim)) * (self._sgBest - self._current_position)
        self._current_position += self._velocity

    def __str__(self):
        return "Hybrid Genetic Algorithm and Sperm Swarm Optimization (HGASSO)"
