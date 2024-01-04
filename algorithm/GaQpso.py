from .NsgaIII import NsgaIII
import math
import numpy as np
import random
from random import randrange
from time import time


# Jun Sun, Wei Fang, Vasile Palade, Xiaojun Wu, Wenbo Xu, "Quantum-behaved particle swarm optimization with Gaussian distributed local attractor point,"
# Applied Mathematics and Computation, Volume 218, Issue 7, 2011,
# Pages 3763-3775, doi: 10.1016/j.amc.2011.09.021
# Copyright (c) 2024 Miller Cy Chan


# Gaussian distributed local attractor QPSO (GAQPSO)
class GaQpso(NsgaIII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._currentGeneration, self._max_iterations = 0, maxIterations
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)

        self._currentGeneration = 0

        self._chromlen, self._alpha0, self._alpha1 = 0, .5, .96
        self._gBest, self._pBestScore = [], []

        self._current_position, self.__pBestPosition = [[]], [[]]


    def initialize(self, population):
        prototype = self._prototype

        populationSize = len(population)
        for i in range(populationSize):
            positions = []
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype(positions)
            if i < 1:
                self._chromlen = len(positions)
                self._gBest = np.zeros(self._chromlen, dtype=float)
                self._pBestScore = np.zeros(populationSize, dtype=float)
                self._pBestPosition = np.zeros((populationSize, self._chromlen), dtype=float)
                self._current_position = np.zeros((populationSize, self._chromlen), dtype=float)


    def optimum(self, localVal, chromosome):
        localBest = self._prototype.makeEmptyFromPrototype()
        localBest.updatePositions(localVal)

        if localBest.dominates(chromosome):
            chromosome.updatePositions(localVal)
            return localVal

        positions = np.zeros(self._chromlen, dtype=float)
        chromosome.extractPositions(positions)
        return positions


    @staticmethod
    def gaussian(x, mu, sigma):
        def N(x):
            return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
        if sigma == 0:
            return N(x)
        return N((x - mu) / sigma) / sigma


    def updatePosition(self, population):
        mBest = np.zeros(self._chromlen, dtype=float)
        current_position = self._current_position[:]
        populationSize = self._populationSize

        for i in range(populationSize):
            fitness = population[i].fitness
            if fitness > self._pBestScore[i]:
                self._pBestScore[i] = fitness
                population[i].extractPositions(self._current_position[i])
                self._pBestPosition[i] = self._current_position[i][:]
            self._gBest = self.optimum(self._gBest, population[i])

            mBest += self._pBestPosition[i] / populationSize

        alpha = self._alpha0 + (self._max_iterations - self._currentGeneration) * (self._alpha1 - self._alpha0) / self._max_iterations
        for i in range(populationSize):
            for j in range(self._chromlen):
                phi, u = np.random.rand(2)
                p = phi * self._pBestPosition[i, j] + (1 - phi) * self._gBest[j]
                n_p = GaQpso.gaussian(p, mBest[j], mBest[j] - self._pBestPosition[i, j])
                NP = n_p if randrange(100) < self._mutationProbability else p

                if np.random.rand() > .5:
                    self._current_position[i, j] += NP + alpha * abs(mBest[j] - current_position[i, j]) * math.log(1.0 / u)
                else:
                    self._current_position[i, j] += NP - alpha * abs(mBest[j] - current_position[i, j]) * math.log(1.0 / u)

            self._current_position[i] = self.optimum(self._current_position[i], population[i])


    def replacement(self, population):
        populationSize = self._populationSize
        self.updatePosition(population)

        for i in range(populationSize):
            chromosome = self._prototype.makeEmptyFromPrototype()
            chromosome.updatePositions(self._current_position[i])
            population[i] = chromosome

        return super().replacement(population)


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
        currentGeneration = self._currentGeneration
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
            self._currentGeneration = currentGeneration

    def __str__(self):
        return "Gaussian distributed local attractor QPSO (GAQPSO)"
