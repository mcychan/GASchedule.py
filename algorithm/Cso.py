from .NsgaIII import NsgaIII
import math
import numpy as np
import random
from time import time


# X. -S. Yang and Suash Deb, "Cuckoo Search via Lévy flights,"
# 2009 World Congress on Nature & Biologically Inspired Computing (NaBIC), Coimbatore, India,
# 2009, pp. 210-214, doi: 10.1109/NABIC.2009.5393690.
# Copyright (c) 2023 Miller Cy Chan


# Cuckoo Search Optimization (CSO)
class Cso(NsgaIII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._max_iterations = maxIterations
        self._maxRepeat = min(15, self._max_iterations // 2)
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)

        self._chromlen, self._pa, self._beta = 0, .25, 1.5
        num = math.gamma(1 + self._beta) * math.sin(math.pi * self._beta / 2)
        den = math.gamma((1 + self._beta) / 2) * self._beta * (2 ** ((self._beta - 1) / 2))
        self._σu, self._σv = (num / den) ** (1 / self._beta), 1

        self._sBestScore = []
        self._current_position = [[]]


    def initialize(self, population):
        prototype = self._prototype

        populationSize = len(population)
        for i in range(populationSize):
            positions = []
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype(positions)
            if i < 1:
                self._chromlen = len(positions)
                self._current_position = np.zeros((populationSize, self._chromlen), dtype=float)
                self._sBestScore = np.zeros(self._chromlen, dtype=float)


    def optimum(self, localVal, chromosome):
        localBest = self._prototype.makeEmptyFromPrototype()
        localBest.updatePositions(localVal)

        if localBest.dominates(chromosome):
            chromosome.updatePositions(localVal)
            return localVal

        positions = np.zeros(self._chromlen, dtype=float)
        chromosome.extractPositions(positions)
        return positions


    def updatePosition1(self, population):
        current_position = self._current_position[:]
        populationSize = self._populationSize
        u, v = np.random.normal(0, self._σu, self._chromlen), np.random.normal(0, self._σv, self._chromlen)
        S = u / (abs(v) ** (1 / self._beta))

        for i in range(populationSize):
            if i == 0:
                population[i].extractPositions(self._sBestScore)
            else:
                self._sBestScore = self.optimum(self._sBestScore, population[i])

            self._current_position[i] += np.random.randn(self._chromlen) * 0.01 * S * (current_position[i] - self._sBestScore)
            self._current_position[i] = self.optimum(self._current_position[i], population[i])


    def updatePosition2(self, population):
        current_position = self._current_position[:]
        populationSize = self._populationSize
        for i in range(populationSize):
            d1, d2 = np.random.randint(0, 5, 2)
            for j in range(self._chromlen):
                r = np.random.rand()
                if r < self._pa:
                    self._current_position[i, j] += random.random() * (current_position[d1, j] - current_position[d2, j])
            self._current_position[i] = self.optimum(self._current_position[i], population[i])


    def replacement(self, population):
        populationSize = self._populationSize
        self.updatePosition1(population)
        self.updatePosition2(population)

        for i in range(populationSize):
            chromosome = self._prototype.makeEmptyFromPrototype()
            chromosome.updatePositions(self._current_position[i])
            population[i] = chromosome

        result = super().replacement(population)
        result[0].extractPositions(self._current_position[0])
        self._sBestScore = self._current_position[0, :]
        return result


    # Starts and executes algorithm
    def run(self, maxRepeat=9999, minFitness=0.999):
        mutationSize, mutationProbability = self._mutationSize, self._mutationProbability
        populationSize = self._populationSize
        population = populationSize * [None]

        self.initialize(population)
        random.seed(round(time() * 1000))
        np.random.seed(int(time()))
        pop = [population, None]

        # Current generation
        currentGeneration = 0
        bestNotEnhance, lastBestFit = 0, 0.0

        cur, next = 0, 1
        while currentGeneration < self._max_iterations:
            if currentGeneration > 0:
                best = self.result
                print("Fitness:", "{:f}\t".format(best.fitness), "Generation:", currentGeneration, end="\r")

                # algorithm has reached criteria?
                if best.fitness > minFitness:
                    break

                difference = abs(best.fitness - lastBestFit)
                if difference <= 0.0000001:
                    bestNotEnhance += 1
                else:
                    lastBestFit = best.fitness
                    bestNotEnhance = 0

                if bestNotEnhance > (maxRepeat / 50):
                    self.reform()

            # crossover
            offspring = self.crossing(pop[cur])

            # mutation
            for child in offspring:
                child.mutation(mutationSize, mutationProbability)

            pop[cur].extend(offspring)

            # replacement
            pop[next] = self.replacement(pop[cur])
            self._best = pop[next][0] if pop[next][0].dominates(pop[cur][0]) else pop[cur][0]

            cur, next = next, cur
            currentGeneration += 1

    def __str__(self):
        return "Cuckoo Search Optimization (CSO)"
