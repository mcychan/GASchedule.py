from .LévyFlights import LévyFlights
from .NsgaIII import NsgaIII
import math
import numpy as np
import random
from time import time


# Xie, Jian & Chen, Huan. (2013).
# A Novel Bat Algorithm Based on Differential Operator and Lévy Flights Trajectory.
# Computational intelligence and neuroscience. 2013. 453812. 10.1155/2013/453812. 
# Copyright (c) 2024 Miller Cy Chan


# Bat algorithm with differential operator and Levy flights trajectory (DLBA)
class Dlba(NsgaIII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._currentGeneration, self._max_iterations = 0, maxIterations
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)

        # there should be at least 5 chromosomes in population
        if self._populationSize < 5:
            self._populationSize = 5

        self._chromlen, self._minValue, self._alpha, self._pa = 0, 0, .9, .25
        self._loudness, self._rate = None, None

        self._gBest = None
        self._position = [[]]
        self._maxValues, self._lf = None, None


    def initialize(self, population):
        prototype = self._prototype

        self._maxValues = []
        prototype.makeEmptyFromPrototype(self._maxValues)

        populationSize = self._populationSize
        for i in range(populationSize):
            positions = []
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype(positions)
            if i < 1:
                self._chromlen = len(positions)
                self._rate = np.zeros(populationSize, dtype=float)
                self._loudness = np.zeros(populationSize, dtype=float)
                self._position = np.zeros((populationSize, self._chromlen), dtype=float)
                self._lf = LévyFlights(self._chromlen)

            self._rate[i] = random.random()
            self._loudness[i] = random.random() + 1


    def updatePositions(self, population):
        mean = np.mean(self._loudness)
        currentGeneration, prototype = self._currentGeneration, self._prototype
        gBest, maxValues, minValue = self._gBest, self._maxValues, self._minValue
        position, rate, loudness = self._position, self._rate, self._loudness

        if gBest is None:
            gBest = position[0]
        prevBest = prototype.makeEmptyFromPrototype()
        prevBest.updatePositions(gBest)

        populationSize = self._populationSize
        for i in range(populationSize):
            beta, rand = np.random.uniform(size=2)
            𝛽1, 𝛽2 = np.random.uniform(low=-1, high=1, size=2)
            r1, r2, r3, r4 = np.random.randint(0, populationSize, 4)
            while r1 == r2:
                r2 = np.random.randint(0, populationSize)
            while r3 == r4:
                r4 = np.random.randint(0, populationSize)

            for j in range(self._chromlen):
                f1 = ((minValue - maxValues[j]) * currentGeneration / 𝛽1 + maxValues[j]) * beta
                f2 = ((maxValues[j] - minValue) * currentGeneration / 𝛽2 + minValue) * beta
                position[i, j] = gBest[j] + f1 * (position[r1][j] - position[r2][j]) + f2 * (position[r3][j] - position[r3][j])

                if rand > rate[i]:
                    𝜀 = np.random.uniform(low=-1, high=1)
                    position[i, j] += gBest[j] + 𝜀 * mean

            gBest = self._lf.updatePosition(population[i], position, i, gBest)


        globalBest = prototype.makeEmptyFromPrototype()
        globalBest.updatePositions(gBest)
        mean = np.mean(rate)
        for i in range(populationSize):
            positionTemp = np.copy(position)
            if random.random() < loudness[i]:
                𝜂 = np.random.uniform(low=-1, high=1)
                for j in range(self._chromlen):
                    position[i, j] = gBest[j] + 𝜂 * mean

                if prevBest.dominates(globalBest):
                    rate[i] *= (currentGeneration / 𝜂) ** 3
                    loudness[i] *= self._alpha

            position[i] = self._lf.optimum(position[i], population[i])


    def reform(self):
        random.seed(round(time() * 1000))
        np.random.seed(int(time()))
        if self._crossoverProbability < 95:
            self._crossoverProbability += 1.0
        elif self._pa < .5:
            self._pa += .01


    def replacement(self, population):
        populationSize = self._populationSize
        self.updatePositions(population)

        for i in range(populationSize):
            chromosome = self._prototype.makeEmptyFromPrototype()
            chromosome.updatePositions(self._position[i])
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
            [i for i in map(self.mutation, offspring)]

            pop[cur].extend(offspring)

            # replacement
            pop[next] = self.replacement(pop[cur])
            self._best = pop[next][0] if pop[next][0].dominates(pop[cur][0]) else pop[cur][0]

            cur, next = next, cur
            currentGeneration += 1
            self._currentGeneration = currentGeneration

    def __str__(self):
        return "Bat algorithm with differential operator and Levy flights trajectory (DLBA)"

