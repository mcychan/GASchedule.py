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
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)
        self._decline = .25
        self._sBestScore, self._sgBestScore = [], 0
        self._sBest, self._sgBest = [], []
        self._current_position, self._velocity = [], []
        self._motility = []

    def replacement(self, population):
        populationSize = len(population)
        climax, decline = 1 - self._decline, self._decline

        for i in range(populationSize):
            fitness = population[i].fitness
            if fitness < self._sBestScore[i]:
                population[i].updatePositions(self._current_position[i])
                fitness = population[i].fitness
                self._motility[i] = True

            if fitness > self._sBestScore[i]:
                self._sBestScore[i] = fitness
                population[i].extractPositions(self._current_position[i])
                self._sBest[i] = self._current_position[i][:]

            if fitness > self._sgBestScore:
                self._sgBestScore = fitness
                population[i].extractPositions(self._current_position[i])
                self._sgBest = self._current_position[i][:]

            if self._repeatRatio > self._sBestScore[i]:
                self._sBestScore[i] -= self._repeatRatio * decline
            if self._repeatRatio > climax and self._sgBestScore > climax:
                if i > (populationSize * self._sgBestScore):
                    population[i].updatePositions(self._current_position[i])
                    self._motility[i] = True

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
                self._motility = np.zeros(populationSize, dtype=bool)

            self._sBestScore[i] = population[i].fitness
            self._current_position[i] = positions
            self._velocity[i] = np.random.uniform(-.6464, .7157, size) / 3.0

    def updateVelocities(self, population):
        motility = self._motility
        if np.count_nonzero(motility) < 1:
            return

        populationSize = len(population)
        dim = self._velocity[motility].shape

        self._velocity[motility] = np.random.random(dim) * np.log10(np.random.uniform(7.0, 14.0, dim)) * self._velocity[motility] + \
        np.log10(np.random.uniform(7.0, 14.0, dim)) * np.log10(np.random.uniform(35.5, 38.5, dim)) * (self._sBest[motility] - self._current_position[motility]) + \
        np.log10(np.random.uniform(7.0, 14.0, dim)) * np.log10(np.random.uniform(35.5, 38.5, dim)) * (self._sgBest - self._current_position[motility])
        self._current_position[motility] += self._velocity[motility]

    def __str__(self):
        return "Hybrid Genetic Algorithm and Sperm Swarm Optimization (HGASSO)"