import math
import numpy as np
import random
from time import time

class LévyFlights:
    def __init__(self, chromlen):
        self._chromlen, self._beta = chromlen, 1.5
        num = math.gamma(1 + self._beta) * math.sin(math.pi * self._beta / 2)
        den = math.gamma((1 + self._beta) / 2) * self._beta * (2 ** ((self._beta - 1) / 2))
        self._σu, self._σv = (num / den) ** (1 / self._beta), 1


    def optimum(self, localVal, chromosome):
        localBest = chromosome.makeEmptyFromPrototype()
        localBest.updatePositions(localVal)

        if localBest.dominates(chromosome):
            chromosome.updatePositions(localVal)
            return localVal

        positions = np.zeros(self._chromlen, dtype=float)
        chromosome.extractPositions(positions)
        return positions


    def updatePosition(self, chromosome, currentPosition, i, gBest):
        curPos = np.copy(currentPosition[i])
        u, v = np.random.randn() * self._σu, np.random.randn() * self._σv
        S = u / (np.abs(v) ** (1 / self._beta))

        if gBest is None:
            gBest = np.zeros(self._chromlen, dtype=float)
            chromosome.extractPositions(gBest)
        else:
            gBest = self.optimum(gBest, chromosome)

        currentPosition[i] += np.random.normal(self._chromlen) * 0.01 * S * (curPos - gBest)
        currentPosition[i] = self.optimum(currentPosition[i], chromosome)

        return gBest


    def updatePositions(self, population, populationSize, currentPosition, gBest):
        for i in range(populationSize):
           gBest = self.updatePosition(population[i], currentPosition, i, gBest)

        return gBest
